#!/usr/bin/env python3
"""
Test use case: Complete loan ingestion and risk analysis flow

This script tests:
1. Health check endpoint
2. Loan ingestion with valid payload
3. Loan list retrieval
4. Risk metrics retrieval
"""

import requests
import json
from datetime import date

# Configuration
API_BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_health_check():
    """Test health endpoint"""
    print("\n[TEST 1] Health Check")
    print("-" * 50)
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        print("✅ PASSED: Health check successful")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_loan_ingestion():
    """Test loan ingestion endpoint"""
    print("\n[TEST 2] Loan Ingestion")
    print("-" * 50)

    payload = {
        "borrower": {
            "borrowerId": "B001",
            "name": "John Smith",
            "ssnHash": "hash123",
            "dob": "1985-05-15"
        },
        "loan": {
            "loanId": "L001",
            "amount": 450000,
            "status": "submitted",
            "purpose": "purchase",
            "originationDate": "2026-06-01",
            "ltv": 78.5,
            "dti": 38.2
        },
        "property": {
            "propertyId": "P001",
            "address": "123 Main St",
            "city": "Austin",
            "state": "TX",
            "zip": "73301",
            "type": "single_family"
        },
        "income": {
            "incomeId": "I001",
            "type": "w2",
            "employerName": "Tech Corp",
            "annualIncome": 180000,
            "startDate": "2020-01-15"
        },
        "documents": [
            {
                "documentId": "D001",
                "type": "paystub",
                "sourceSystem": "document-mgmt",
                "uploadedAt": "2026-06-01T10:00:00Z"
            }
        ]
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/loans/ingest",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert result["loanId"] == "L001"
        assert result["status"] == "ingested"

        print("✅ PASSED: Loan ingestion successful")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_loan_list():
    """Test loan list retrieval"""
    print("\n[TEST 3] Get Loan List")
    print("-" * 50)
    try:
        response = requests.get(
            f"{API_BASE_URL}/loans?limit=10&offset=0",
            headers=HEADERS,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Found {result.get('total', 0)} loans")
        if result.get('items'):
            print(f"Sample loan: {result['items'][0]['loanId']}")

        assert response.status_code == 200
        assert "items" in result
        assert "total" in result

        print("✅ PASSED: Loan list retrieved")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_metrics():
    """Test metrics endpoint"""
    print("\n[TEST 4] Get Metrics")
    print("-" * 50)
    try:
        response = requests.get(
            f"{API_BASE_URL}/metrics",
            headers=HEADERS,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        assert response.status_code == 200
        assert "totalLoans" in result
        assert "avgRiskScore" in result

        print("✅ PASSED: Metrics retrieved")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_graph_query():
    """Test graph query endpoint"""
    print("\n[TEST 5] Graph Query (Cypher)")
    print("-" * 50)

    payload = {
        "cypher": "MATCH (n) RETURN count(n) as count LIMIT 5",
        "params": {}
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/graph/query",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Columns: {result.get('columns', [])}")
        print(f"Rows: {result.get('rows', [])}")

        assert response.status_code == 200
        assert "columns" in result
        assert "rows" in result

        print("✅ PASSED: Graph query executed")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("MORTGAGE GRAPH PLATFORM - TEST SUITE")
    print("=" * 50)

    results = []

    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Loan Ingestion", test_loan_ingestion()))
    results.append(("Loan List", test_loan_list()))
    results.append(("Metrics", test_metrics()))
    results.append(("Graph Query", test_graph_query()))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print("-" * 50)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 50)

    return passed == total


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
