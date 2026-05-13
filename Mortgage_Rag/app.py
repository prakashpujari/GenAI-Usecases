from __future__ import annotations

import io
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader
import streamlit as st
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from src.config import load_settings
from src.pii import redact_pii, detect_pii
from src.guardrails import apply_input_guardrails, apply_output_guardrails
from src.logger import get_logger
from src.underwriting_agents import run_underwriting_workflow

# Initialize logger
logger = get_logger(__name__)


class UploadedDoc:
    def __init__(self, name: str, text: str) -> None:
        logger.info(f"Initializing UploadedDoc: name={name}, text_length={len(text)}")
        self.name = name
        self.text = text
        self.redacted_text = redact_pii(text)
        self.pii = detect_pii(text)
        logger.info(f"UploadedDoc initialized: name={name}, pii_count={len(self.pii)}")


def extract_text_from_pdf_bytes(data: bytes) -> str:
    logger.info(f"Extracting text from PDF: data_size={len(data)} bytes")
    try:
        reader = PdfReader(io.BytesIO(data))
        pages: list[str] = []
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text:
                pages.append(text)
                logger.debug(f"Extracted page {idx + 1}: {len(text)} characters")
        result = "\n".join(pages)
        logger.info(f"PDF extraction complete: {len(pages)} pages, {len(result)} total characters")
        return result
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}", exc_info=True)
        raise


def build_vector_store(docs: Iterable[UploadedDoc], chunk_size: int, chunk_overlap: int, api_key: str, embed_model: str) -> FAISS:
    logger.info(f"Building vector store: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, embed_model={embed_model}")
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        documents: list[Document] = []
        doc_list = list(docs)
        logger.info(f"Processing {len(doc_list)} documents")
        
        for doc in doc_list:
            chunks = splitter.split_text(doc.redacted_text)
            logger.debug(f"Document '{doc.name}' split into {len(chunks)} chunks")
            for idx, chunk in enumerate(chunks):
                documents.append(Document(page_content=chunk, metadata={"source": doc.name, "chunk": idx}))
        
        logger.info(f"Total documents created: {len(documents)}")
        embeddings = OpenAIEmbeddings(model=embed_model, api_key=api_key)
        logger.info("Creating FAISS index from documents")
        vector_store = FAISS.from_documents(documents=documents, embedding=embeddings)
        logger.info("Vector store created successfully")
        return vector_store
    except Exception as e:
        logger.error(f"Error building vector store: {e}", exc_info=True)
        raise


st.set_page_config(page_title="SecureMortgageAI", page_icon="🔒", layout="wide")
logger.info("=" * 80)
logger.info("Application started: SecureMortgageAI")
load_dotenv()
settings = load_settings()
logger.info(f"Settings loaded: chunk_size={settings.chunk_size}, chunk_overlap={settings.chunk_overlap}")

st.title("🔒 SecureMortgageAI")
st.caption("AI-powered mortgage document assistant with PII protection and security guardrails")
st.info(
    "Decision support mode: this system proposes Approve/Refer/Decline recommendations with rationale and policy citations. Final credit decisions are always made by a human underwriter."
)

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
    logger.error("OPENAI_API_KEY is not set")
    st.error("OPENAI_API_KEY is not set. Add it to your environment to enable embeddings.")
    st.stop()

uploaded_docs: list[UploadedDoc] = []
if uploads:
    logger.info(f"Processing {len(uploads)} uploaded files")
    for file in uploads:
        logger.info(f"Processing file: {file.name}")
        text = extract_text_from_pdf_bytes(file.read())
        uploaded_docs.append(UploadedDoc(file.name, text))
    logger.info(f"Successfully processed {len(uploaded_docs)} documents")

if not uploaded_docs:
    logger.debug("No documents uploaded, showing info message")
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
    logger.info(f"New query received: '{query}' (length={len(query)})")
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Apply input guardrails
    logger.info("Applying input guardrails to query")
    guardrail_result = apply_input_guardrails(query)
    
    if not guardrail_result.passed:
        logger.warning(f"Query failed guardrail check: {guardrail_result.reason}")
        error_msg = f"⚠️ {guardrail_result.reason}\n\n"
        if guardrail_result.suggested_action:
            error_msg += f"💡 {guardrail_result.suggested_action}"
        
        st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        with st.chat_message("assistant"):
            st.markdown(error_msg)
    else:
        # Show warning if query might not be relevant (but continue)
        logger.info("Query passed input guardrails")
        warning_msg = ""
        if guardrail_result.reason:
            logger.warning(f"Guardrail warning: {guardrail_result.reason}")
            warning_msg = f"ℹ️ {guardrail_result.reason}\n\n"
        
        # Perform search
        logger.info("Performing vector similarity search")
        with st.spinner("🔎 Searching..."):
            # Use similarity_search_with_score to get relevance scores
            results_with_scores = vector_store.similarity_search_with_score(query, k=4)
            logger.info(f"Initial search returned {len(results_with_scores)} results")
            
            # Filter by relevance threshold
            relevance_threshold = 1.5
            results = [(doc, score) for doc, score in results_with_scores if score < relevance_threshold]
            logger.info(f"After filtering (threshold={relevance_threshold}): {len(results)} results")
        
        # Check if we have valid results
        if not results:
            logger.info("No relevant results found for query")
            response_msg = warning_msg + "🔍 I couldn't find any relevant information in the uploaded documents to answer your question.\n\n💡 Try rephrasing your query or using different keywords related to mortgage documents."
            st.session_state.messages.append({"role": "assistant", "content": response_msg, "sources": []})
            with st.chat_message("assistant"):
                st.markdown(response_msg)
        else:
            # Extract documents for processing
            docs = [doc for doc, score in results]
            logger.info(f"Extracted {len(docs)} documents for processing")
            
            # Apply output guardrails
            logger.info("Applying output guardrails")
            result_texts = [doc.page_content for doc in docs]
            sanitized_texts, output_validation = apply_output_guardrails(result_texts)
            
            if not output_validation.passed:
                logger.warning(f"Output validation failed: {output_validation.reason}")
                response_msg = f"⚠️ {output_validation.reason}: {output_validation.suggested_action}"
                st.session_state.messages.append({"role": "assistant", "content": response_msg, "sources": []})
                with st.chat_message("assistant"):
                    st.markdown(response_msg)
            else:
                # Filter out empty results
                valid_results = [(doc, sanitized_text, score) for (doc, score), sanitized_text in zip(results, sanitized_texts) if sanitized_text.strip()]
                logger.info(f"Valid results after sanitization: {len(valid_results)}")
                
                if not valid_results:
                    logger.warning("No valid results after sanitization")
                    response_msg = warning_msg + "🔍 No relevant results found for your query.\n\n💡 Try rephrasing your query or using different keywords related to mortgage documents."
                    st.session_state.messages.append({"role": "assistant", "content": response_msg, "sources": []})
                    with st.chat_message("assistant"):
                        st.markdown(response_msg)
                else:
                    # Generate structured underwriting recommendation
                    logger.info("Running underwriting workflow")
                    with st.spinner("✨ Generating response..."):
                        borrower_payload = [
                            {"name": document.name, "text": document.text}
                            for document in uploaded_docs
                        ]
                        underwriting_result = run_underwriting_workflow(
                            query=query,
                            borrower_documents=borrower_payload,
                            policy_vector_store=vector_store,
                            thresholds={
                                "min_credit_score": settings.min_credit_score,
                                "max_dti": settings.max_dti,
                                "max_ltv": settings.max_ltv,
                                "min_employment_months": settings.min_employment_months,
                            },
                        )
                        summary = redact_pii(underwriting_result.summary_markdown)
                    
                    # Prepare sources list
                    sources = []
                    for citation in underwriting_result.output.get("policy_citations", []):
                        source_name = citation.get("source", "Unknown")
                        section = citation.get("section", "N/A")
                        score = citation.get("score", "N/A")
                        sources.append(f"{source_name} (Section {section}) - score {score}")

                    if not sources:
                        sources = ["MISSING policy citations - refer to human underwriter for manual policy validation"]
                    
                    logger.info(f"Response generated successfully with {len(sources)} sources")
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
