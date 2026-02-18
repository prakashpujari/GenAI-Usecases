"""
Test LLM Response Redaction - Ensures SSNs in AI responses are redacted
"""
from src.pii import redact_pii, detect_pii

# Simulate LLM responses that might contain PII
llm_responses = [
    "The Social Security Number (SSN) for Jane is 999-99-9999, as indicated in the provided context.",
    "The borrower's SSN is 123-45-6789 and their email is john@example.com",
    "According to the W-2, the employee SSN: 555-12-3456 has an income of $85,000",
    "The applicant can be reached at (555) 123-4567 or via SSN 111-22-3333",
    "Contact information: Email is jane.doe@email.com, phone is 555-987-6543",
]

print("=" * 80)
print("🔒 LLM RESPONSE REDACTION TEST")
print("=" * 80)
print("\nScenario: LLM accidentally includes PII in its response")
print("Solution: Apply redact_pii() to ALL LLM outputs before showing to user")
print("=" * 80)

for i, response in enumerate(llm_responses, 1):
    print(f"\nTest {i}:")
    print(f"  LLM Output (BEFORE redaction):")
    print(f"    {response}")
    
    # Detect PII in response
    detected = detect_pii(response)
    if detected:
        print(f"  ⚠️  Detected {len(detected)} PII item(s):")
        for pii in detected:
            print(f"      - {pii.label}: {pii.value}")
    
    # Redact the response
    redacted_response = redact_pii(response)
    print(f"  ✅ After redaction (SAFE to display):")
    print(f"    {redacted_response}")

print("\n" + "=" * 80)
print("IMPLEMENTATION IN app.py:")
print("=" * 80)
print("""
# After LLM generates response:
with st.spinner("✨ Generating response..."):
    summary = generate_summary_with_llm(query, valid_results, settings.openai_api_key)
    # CRITICAL: Redact any PII from LLM response for safety
    summary = redact_pii(summary)  # <-- THIS LINE IS ESSENTIAL!
""")

print("=" * 80)
print("✅ This ensures even if LLM includes PII, it gets redacted before display")
print("=" * 80)

# Real-world test case
print("\n" + "=" * 80)
print("🔍 REAL-WORLD SCENARIO")
print("=" * 80)

context_with_redacted_ssn = """
Document: W-2 Form
Employee: Jane Doe
SSN: [SSN_REDACTED]
Employer: ABC Corporation
Annual Income: $75,000
"""

# Simulate what might happen:
# 1. LLM sees redacted context but somehow generates an SSN (hallucination or pattern matching)
llm_hallucinated_response = "Based on the W-2, Jane Doe's Social Security Number is 999-99-9999 and her annual income is $75,000."

print("\nContext sent to LLM (already redacted):")
print(context_with_redacted_ssn)

print("\nLLM Response (might contain hallucinated PII):")
print(f"  {llm_hallucinated_response}")

# Detect if hallucinated
detected_hallucinated = detect_pii(llm_hallucinated_response)
print(f"\n⚠️  LLM hallucinated {len(detected_hallucinated)} PII item(s)!")

# Redact it
safe_response = redact_pii(llm_hallucinated_response)
print(f"\n✅ After mandatory redaction (what user sees):")
print(f"  {safe_response}")

print("\n" + "=" * 80)
print("CONCLUSION: Always redact LLM responses as final safety layer!")
print("=" * 80)
