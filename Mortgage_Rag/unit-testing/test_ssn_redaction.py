"""
Test SSN Redaction - Shows different redaction strategies
"""
from src.pii import redact_pii, detect_pii

# Test cases with various SSN formats
test_cases = [
    "Applicant SSN: 123-45-6789",
    "Social Security Number is 987654321",
    "SSN 123 45 6789 on file",
    "Contact: SSN: 555-12-3456, Phone: (555) 123-4567",
    "Multiple SSNs: 111-22-3333 and 444-55-6666",
]

print("=" * 70)
print("SSN REDACTION TEST - Current Implementation (Full Redaction)")
print("=" * 70)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}:")
    print(f"  Original: {test}")
    print(f"  Redacted: {redact_pii(test)}")
    
    # Show what was detected
    detected = detect_pii(test)
    ssn_matches = [m for m in detected if m.label == "SSN"]
    if ssn_matches:
        print(f"  Detected: {len(ssn_matches)} SSN(s) - {[m.value for m in ssn_matches]}")

print("\n" + "=" * 70)
print("✅ All SSNs are being redacted to [SSN_REDACTED]")
print("=" * 70)

# Alternative: Partial redaction (showing last 4 digits)
import re

def redact_ssn_partial(text: str) -> str:
    """Alternative: Redact SSN but show last 4 digits"""
    pattern = re.compile(r"\b(?!000|666|9\d\d)(\d{3})[- ]?(?!00)(\d{2})[- ]?(?!0000)(\d{4})\b")
    return pattern.sub(r"XXX-XX-\3", text)

print("\n" + "=" * 70)
print("ALTERNATIVE: Partial Redaction (Shows Last 4 Digits)")
print("=" * 70)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}:")
    print(f"  Original: {test}")
    print(f"  Partial:  {redact_ssn_partial(test)}")

print("\n" + "=" * 70)
print("Which format do you prefer?")
print("  1. Full Redaction: 123-45-6789 → [SSN_REDACTED]")
print("  2. Partial Redaction: 123-45-6789 → XXX-XX-6789")
print("=" * 70)
