#!/usr/bin/env python3
"""
Simple test server - returns mock data for frontend testing
Run: python3 test_server.py
Access: http://localhost:8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mortgage Graph API Test", version="1.0.0")

# Allow all CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok", "database": "neo4j"}

# Metrics endpoint
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

# Loans list
@app.get("/loans")
def loans():
    return {
        "loans": [
            {
                "loanId": "L001",
                "borrowerId": "B001",
                "amount": 450000,
                "status": "submitted",
                "riskScore": 62
            },
            {
                "loanId": "L002",
                "borrowerId": "B002",
                "amount": 350000,
                "status": "approved",
                "riskScore": 45
            }
        ],
        "total": 2
    }

# Single loan
@app.get("/loans/{loan_id}")
def get_loan(loan_id: str):
    return {
        "loanId": loan_id,
        "borrowerId": "B001",
        "amount": 450000,
        "status": "submitted",
        "riskScore": 62
    }

# Ingest loan
@app.post("/loans/ingest")
def ingest_loan(payload: dict):
    return {"success": True, "loanId": "L_new"}

# Root
@app.get("/")
def root():
    return {"message": "Mortgage Graph Platform API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    print("Starting test server...")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)
