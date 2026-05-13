"""
Test script to demonstrate the LLM summary generation
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Mock search results
mock_results = [
    (
        type('Doc', (), {
            'metadata': {'source': 'w2_2023.pdf', 'chunk': 0},
            'page_content': 'Employee: John Smith\nEmployer: ABC Corporation\nWages, tips, other compensation: $85,000.00\nFederal income tax withheld: $12,750.00\nYear: 2023'
        })(),
        'Employee: John Smith\nEmployer: ABC Corporation\nWages, tips, other compensation: $85,000.00\nFederal income tax withheld: $12,750.00\nYear: 2023',
        0.3
    ),
    (
        type('Doc', (), {
            'metadata': {'source': 'paystub_jan2024.pdf', 'chunk': 1},
            'page_content': 'Pay Period: 01/01/2024 - 01/15/2024\nGross Pay: $3,542.00\nFederal Tax: $531.00\nState Tax: $177.00\nNet Pay: $2,834.00'
        })(),
        'Pay Period: 01/01/2024 - 01/15/2024\nGross Pay: $3,542.00\nFederal Tax: $531.00\nState Tax: $177.00\nNet Pay: $2,834.00',
        0.4
    )
]

query = "What is the borrower's annual income?"

print("=" * 80)
print("CHATBOT LLM SUMMARY DEMONSTRATION")
print("=" * 80)

print(f"\n💬 User Query: {query}\n")
print("🔍 Search Results Found: 2\n")

# Prepare context
context_parts = []
for idx, (doc, sanitized_text, score) in enumerate(mock_results, start=1):
    source = doc.metadata.get('source', 'Unknown')
    context_parts.append(f"[Source: {source}]\n{sanitized_text}")

context = "\n\n".join(context_parts)

# Create prompt
system_prompt = """You are a helpful mortgage document assistant. Your role is to answer questions about mortgage documents accurately and concisely based ONLY on the provided context.

Rules:
- Only use information from the provided context
- Be specific and cite sources when possible
- If the context doesn't contain enough information to answer fully, say so
- Keep answers concise and professional
- Never make up information
- All PII has been redacted for privacy"""

user_prompt = f"""Question: {query}

Context from mortgage documents:
{context}

Please provide a clear, concise answer based on the context above."""

print("📤 Calling OpenAI LLM...\n")

try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
    else:
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
        
        summary = response.choices[0].message.content
        
        print("✨ LLM RESPONSE:")
        print("-" * 80)
        print(summary)
        print("-" * 80)
        
        print("\n📚 SOURCES:")
        for idx, (doc, _, score) in enumerate(mock_results, start=1):
            source_name = doc.metadata.get('source', 'Unknown')
            chunk_num = doc.metadata.get('chunk', 'N/A')
            relevance = max(0, min(100, int((1 - score/2) * 100)))
            print(f"  {idx}. {source_name} (Chunk {chunk_num}) - {relevance}% relevant")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 80)
