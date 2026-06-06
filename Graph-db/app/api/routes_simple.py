"""
Simple test routes - returns mock data to verify API works
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "database": "neo4j",
        "version": "1.0.0"
    }

@router.get("/metrics")
def metrics():
    """Dashboard metrics"""
    return {
        "totalLoans": 42,
        "totalBorrowers": 28,
        "avgRiskScore": 65.5,
        "networkDensity": 0.34,
        "lastGdsJobTime": "2026-06-06T12:00:00Z",
        "lastGdsJobStatus": "completed"
    }

@router.get("/loans")
def list_loans():
    """List all loans"""
    return {
        "loans": [
            {
                "loanId": "L001",
                "borrowerId": "B001",
                "amount": 450000,
                "status": "submitted",
                "riskScore": 62
            }
        ],
        "total": 1
    }

@router.get("/loans/{loan_id}")
def get_loan(loan_id: str):
    """Get loan details"""
    return {
        "loanId": loan_id,
        "borrowerId": "B001",
        "amount": 450000,
        "status": "submitted",
        "riskScore": 62
    }

@router.post("/loans/ingest")
def ingest_loan(payload: dict):
    """Ingest a loan"""
    return {"success": True, "loanId": "L_new"}

@router.get("/")
def root():
    """Root endpoint"""
    return {"message": "Mortgage Graph Platform API", "version": "1.0.0"}
