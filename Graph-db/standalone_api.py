#!/usr/bin/env python3
"""Standalone API - no imports from app package"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "OK", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok", "database": "neo4j"}

@app.get("/metrics")
def metrics():
    return {"totalLoans": 42, "totalBorrowers": 28, "avgRiskScore": 65.5, "networkDensity": 0.34, "lastGdsJobTime": "2026-06-06", "lastGdsJobStatus": "completed"}

@app.get("/loans")
def loans(skip: int = 0, limit: int = 10):
    return {"items": [{"loanId": "L001", "borrowerName": "John", "amount": 450000, "status": "submitted", "riskScore": 62, "createdAt": "2026-06-01T10:00:00Z"}], "total": 1}

@app.get("/loans/{loan_id}")
def get_loan(loan_id: str):
    return {"loan": {"loanId": loan_id, "amount": 450000, "status": "submitted", "purpose": "purchase", "ltv": 85.5, "dti": 42.3}, "borrower": {"borrowerId": "B001", "name": "John"}, "property": {"propertyId": "P001", "address": "123 Main", "city": "Austin", "state": "TX", "zip": "78701", "type": "single_family"}, "income": {"incomeId": "I001", "type": "w2", "employerName": "Tech", "annualIncome": 180000}, "documents": [], "riskScore": 62}

@app.post("/loans/ingest")
def ingest(payload: dict = None):
    return {"loanId": "L_new", "violations": [], "status": "ingested"}

@app.get("/loans/{loan_id}/risk")
def risk(loan_id: str):
    return {"loanId": loan_id, "ltv": 85.5, "dti": 42.3, "riskScore": 62, "networkRiskScore": 58, "fraudCommunity": None, "riskCentrality": None, "sharedContacts": 5, "similarityFlags": ["high_ltv"], "violations": []}

@app.get("/loans/{loan_id}/explain")
def explain(loan_id: str):
    return {"loanId": loan_id, "rules": [{"ruleId": "R001", "name": "DTI", "type": "threshold", "severity": "low"}], "regulations": ["TRID"], "graphSignals": ["High density"]}

@app.post("/graph/query")
def graph(payload: dict = None):
    return {"query": "", "rows": [{"type": "Borrower", "id": "B001"}, {"type": "Loan", "id": "L001"}]}

@app.get("/jobs")
def jobs():
    return {"jobs": [{"jobId": "job-001", "type": "gds", "status": "completed", "progress": 100}]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
