#!/usr/bin/env python3
import sys
sys.path.insert(0, '/c/pp/GitHub/GenAI-Usecases/Graph-db')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create app directly - no imports from app package
app = FastAPI(title="Test API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Mortgage Graph Platform API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok", "database": "neo4j"}

@app.get("/metrics")
def metrics():
    return {
        "totalLoans": 42,
        "totalBorrowers": 28,
        "avgRiskScore": 65.5,
        "networkDensity": 0.34,
        "lastGdsJobTime": "2026-06-06T12:00:00Z",
        "lastGdsJobStatus": "completed"
    }

@app.get("/loans")
def loans():
    return {
        "loans": [{"loanId": "L001", "borrowerId": "B001", "amount": 450000, "status": "submitted", "riskScore": 62}],
        "total": 1
    }

@app.get("/loans/{loan_id}")
def get_loan(loan_id: str):
    return {"loanId": loan_id, "borrowerId": "B001", "amount": 450000, "status": "submitted", "riskScore": 62}

@app.post("/loans/ingest")
def ingest_loan(payload: dict):
    return {"success": True, "loanId": "L_new"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
