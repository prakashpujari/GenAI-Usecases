from __future__ import annotations

import io
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from src.config import load_settings
from src.pii import redact_pii, detect_pii
from src.guardrails import apply_input_guardrails, apply_output_guardrails


class UploadedDoc:
    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self.redacted_text = redact_pii(text)
        self.pii = detect_pii(text)


def extract_text_from_pdf_bytes(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            pages.append(text)
    return "\n".join(pages)


def build_vector_store(docs: Iterable[UploadedDoc], chunk_size: int, chunk_overlap: int, api_key: str, embed_model: str) -> FAISS:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents: list[Document] = []
    for doc in docs:
        for idx, chunk in enumerate(splitter.split_text(doc.redacted_text)):
            documents.append(Document(page_content=chunk, metadata={"source": doc.name, "chunk": idx}))

    embeddings = OpenAIEmbeddings(model=embed_model, api_key=api_key)
    return FAISS.from_documents(documents=documents, embedding=embeddings)


def generate_summary_with_llm(query: str, search_results: list[tuple], api_key: str) -> str:
    """Generate a summary of search results using OpenAI LLM"""
    
    if not search_results:
        return "I couldn't find any relevant information in the uploaded documents to answer your question."
    
    # Prepare context from search results
    context_parts = []
    for idx, (doc, sanitized_text, score) in enumerate(search_results, start=1):
        source = doc.metadata.get('source', 'Unknown')
        context_parts.append(f"[Source: {source}]\n{sanitized_text}")
    
    context = "\n\n".join(context_parts)
    
    # Create prompt for LLM
    system_prompt = """You are a helpful mortgage document assistant. Your role is to answer questions about mortgage documents accurately and concisely based ONLY on the provided context.

Rules:
- Only use information from the provided context
- Be specific and cite sources when possible
- If the context doesn't contain enough information to answer fully, say so
- Keep answers concise and professional
- Never make up information
- All PII (SSNs, emails, phone numbers, etc.) has been redacted for privacy
- NEVER include actual PII values in your response - refer to them as "[REDACTED]" if needed
- When discussing personal information, use generic terms like "the borrower's SSN is redacted" instead of actual values"""

    user_prompt = f"""Question: {query}

Context from mortgage documents:
{context}

Please provide a clear, concise answer based on the context above."""
    
    # Call OpenAI API
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"


st.set_page_config(page_title="SecureMortgageAI", page_icon="🔒", layout="wide")
load_dotenv()
settings = load_settings()

st.title("🔒 SecureMortgageAI")
st.caption("AI-powered mortgage document assistant with PII protection and security guardrails")

with st.sidebar:
    st.header("📁 Document Upload")
    st.write("Upload W-2s or Paystubs (PDF).")
    uploads = st.file_uploader("PDF files", type=["pdf"], accept_multiple_files=True)
    st.caption("💡 You can also generate sample PDFs with scripts/generate_sample_pdfs.py")
    
    st.divider()
    st.header("🛡️ Safety Guardrails")
    st.write("**Active protections:**")
    st.markdown("""
    - ✅ PII Detection & Redaction
    - ✅ Prompt Injection Prevention
    - ✅ Input Length Validation
    - ✅ Content Filtering
    - ✅ Topic Relevance Check
    - ✅ Output Sanitization
    """)
    with st.expander("Learn more"):
        st.write("""
        **Input Guardrails:**
        - Queries must be 3-500 characters
        - Blocks prompt injection attempts
        - Filters inappropriate content
        - Warns about off-topic queries
        
        **Output Guardrails:**
        - Double-checks PII redaction
        - Sanitizes results for safety
        - Prevents code injection
        """)

if not settings.openai_api_key:
    st.error("OPENAI_API_KEY is not set. Add it to your environment to enable embeddings.")
    st.stop()

uploaded_docs: list[UploadedDoc] = []
if uploads:
    for file in uploads:
        text = extract_text_from_pdf_bytes(file.read())
        uploaded_docs.append(UploadedDoc(file.name, text))

if not uploaded_docs:
    st.info("Upload PDFs to build the vector index and search.")
    st.stop()

# Show document statistics
st.subheader("📄 Uploaded Documents")
doc_stats = []
for doc in uploaded_docs:
    doc_stats.append({
        "Document": doc.name,
        "Characters": len(doc.text),
        "PII Items": len(doc.pii)
    })
st.dataframe(doc_stats, use_container_width=True, hide_index=True)

with st.expander("🔍 View Detected PII"):
    pii_rows = []
    for doc in uploaded_docs:
        for match in doc.pii:
            pii_rows.append({"Document": doc.name, "Type": match.label, "Value": redact_pii(match.value)})
    if pii_rows:
        st.dataframe(pii_rows, use_container_width=True, hide_index=True)
    else:
        st.write("No PII detected.")

# Build vector store
with st.spinner("🔄 Building vector embeddings..."):
    vector_store = build_vector_store(
        uploaded_docs,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        api_key=settings.openai_api_key,
        embed_model=settings.openai_embed_model,
    )
st.success("✅ Vector embeddings created successfully! Ready to chat.")

st.divider()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat interface
st.subheader("💬 Ask Questions About Your Documents")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 View Sources"):
                for idx, source in enumerate(message["sources"], start=1):
                    st.caption(f"{idx}. {source}")

# Chat input
query = st.chat_input("Ask a question about your mortgage documents...")

if query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Apply input guardrails
    guardrail_result = apply_input_guardrails(query)
    
    if not guardrail_result.passed:
        error_msg = f"⚠️ {guardrail_result.reason}\n\n"
        if guardrail_result.suggested_action:
            error_msg += f"💡 {guardrail_result.suggested_action}"
        
        st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        with st.chat_message("assistant"):
            st.markdown(error_msg)
    else:
        # Show warning if query might not be relevant (but continue)
        warning_msg = ""
        if guardrail_result.reason:
            warning_msg = f"ℹ️ {guardrail_result.reason}\n\n"
        
        # Perform search
        with st.spinner("🔎 Searching..."):
            # Use similarity_search_with_score to get relevance scores
            results_with_scores = vector_store.similarity_search_with_score(query, k=4)
            
            # Filter by relevance threshold
            relevance_threshold = 1.5
            results = [(doc, score) for doc, score in results_with_scores if score < relevance_threshold]
        
        # Check if we have valid results
        if not results:
            response_msg = warning_msg + "🔍 I couldn't find any relevant information in the uploaded documents to answer your question.\n\n💡 Try rephrasing your query or using different keywords related to mortgage documents."
            st.session_state.messages.append({"role": "assistant", "content": response_msg, "sources": []})
            with st.chat_message("assistant"):
                st.markdown(response_msg)
        else:
            # Extract documents for processing
            docs = [doc for doc, score in results]
            
            # Apply output guardrails
            result_texts = [doc.page_content for doc in docs]
            sanitized_texts, output_validation = apply_output_guardrails(result_texts)
            
            if not output_validation.passed:
                response_msg = f"⚠️ {output_validation.reason}: {output_validation.suggested_action}"
                st.session_state.messages.append({"role": "assistant", "content": response_msg, "sources": []})
                with st.chat_message("assistant"):
                    st.markdown(response_msg)
            else:
                # Filter out empty results
                valid_results = [(doc, sanitized_text, score) for (doc, score), sanitized_text in zip(results, sanitized_texts) if sanitized_text.strip()]
                
                if not valid_results:
                    response_msg = warning_msg + "🔍 No relevant results found for your query.\n\n💡 Try rephrasing your query or using different keywords related to mortgage documents."
                    st.session_state.messages.append({"role": "assistant", "content": response_msg, "sources": []})
                    with st.chat_message("assistant"):
                        st.markdown(response_msg)
                else:
                    # Generate summary using LLM
                    with st.spinner("✨ Generating response..."):
                        summary = generate_summary_with_llm(query, valid_results, settings.openai_api_key)
                        # CRITICAL: Redact any PII from LLM response for safety
                        summary = redact_pii(summary)
                    
                    # Prepare sources list
                    sources = []
                    for doc, _, score in valid_results:
                        source_name = doc.metadata.get('source', 'Unknown')
                        chunk_num = doc.metadata.get('chunk', 'N/A')
                        relevance = max(0, min(100, int((1 - score/2) * 100)))
                        sources.append(f"{source_name} (Chunk {chunk_num}) - {relevance}% relevant")
                    
                    # Combine warning (if any) with summary
                    final_response = warning_msg + summary
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_response,
                        "sources": sources
                    })
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.markdown(final_response)
                        with st.expander("📚 View Sources"):
                            for idx, source in enumerate(sources, start=1):
                                st.caption(f"{idx}. {source}")

# Add a button to clear chat history
if st.session_state.messages:
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()
