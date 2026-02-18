"""
Test script to demonstrate search result filtering
"""
from langchain_core.documents import Document

# Simulate search results with scores
mock_results = [
    (Document(page_content="John Smith's annual salary is $85,000.", metadata={"source": "paystub.pdf", "chunk": 0}), 0.3),
    (Document(page_content="The mortgage rate is 6.5% APR.", metadata={"source": "loan_doc.pdf", "chunk": 1}), 0.5),
    (Document(page_content="Unrelated content about cars.", metadata={"source": "other.pdf", "chunk": 2}), 2.5),
    (Document(page_content="", metadata={"source": "empty.pdf", "chunk": 3}), 3.0),
]

print("=" * 80)
print("SEARCH RESULT FILTERING DEMONSTRATION")
print("=" * 80)

# Relevance threshold
relevance_threshold = 1.5

print(f"\n📊 Total results returned: {len(mock_results)}")
print(f"🎯 Relevance threshold: {relevance_threshold}")

# Filter by relevance
filtered_results = [(doc, score) for doc, score in mock_results if score < relevance_threshold]

print(f"✅ Results passing threshold: {len(filtered_results)}")

if not filtered_results:
    print("\n🔍 No relevant results found for your query.")
    print("💡 Try rephrasing your query or using different keywords.")
else:
    print(f"\n✅ Found {len(filtered_results)} relevant result{'s' if len(filtered_results) > 1 else ''}\n")
    
    for idx, (doc, score) in enumerate(filtered_results, start=1):
        relevance = max(0, min(100, int((1 - score/2) * 100)))
        print(f"📄 Result {idx}:")
        print(f"   Source: {doc.metadata.get('source')}")
        print(f"   Chunk: {doc.metadata.get('chunk')}")
        print(f"   Score: {score:.2f}")
        print(f"   Relevance: {relevance}%")
        print(f"   Content: {doc.page_content[:60]}...")
        print()

print("=" * 80)
