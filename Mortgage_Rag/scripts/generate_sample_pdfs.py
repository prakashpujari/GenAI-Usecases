from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def build_w2(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, "Form W-2 - Wage and Tax Statement")
    c.drawString(72, 690, "Employee Name: Alex Johnson")
    c.drawString(72, 670, "Employee SSN: 123-45-6789")
    c.drawString(72, 650, "Employer Name: Acme Lending LLC")
    c.drawString(72, 630, "Employer EIN: 12-3456789")
    c.drawString(72, 600, "Wages, tips, other compensation: $78,450.00")
    c.drawString(72, 580, "Federal income tax withheld: $9,200.00")
    c.drawString(72, 560, "Social security wages: $78,450.00")
    c.drawString(72, 540, "Medicare wages and tips: $78,450.00")
    c.showPage()
    c.save()


def build_paystub(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, "Paystub")
    c.drawString(72, 690, "Employee Name: Alex Johnson")
    c.drawString(72, 670, "Pay Period: 01/01/2026 - 01/15/2026")
    c.drawString(72, 650, "Pay Date: 01/20/2026")
    c.drawString(72, 630, "Hourly Rate: $42.50")
    c.drawString(72, 610, "Gross Pay: $3,400.00")
    c.drawString(72, 590, "Net Pay: $2,720.00")
    c.drawString(72, 570, "YTD Gross: $6,800.00")
    c.drawString(72, 550, "Routing Number: 021000021")
    c.drawString(72, 530, "Account Number: 000123456789")
    c.showPage()
    c.save()


def build_bank_statement(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, "Bank Statement")
    c.drawString(72, 700, "Borrower: Alex Johnson")
    c.drawString(72, 680, "Statement Period: 01/01/2026 - 01/31/2026")
    c.drawString(72, 660, "Account Type: Checking")
    c.drawString(72, 640, "Beginning Balance: $41,280.00")
    c.drawString(72, 620, "Deposits & Credits: $7,920.00")
    c.drawString(72, 600, "Withdrawals & Debits: $6,410.00")
    c.drawString(72, 580, "Available Balance: $42,790.00")
    c.drawString(72, 560, "Monthly Debt: $1,850.00")
    c.drawString(72, 540, "Mortgage Reserve Months: 7")
    c.showPage()
    c.save()


def build_employment_letter(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, "Verification of Employment Letter")
    c.drawString(72, 700, "Employment Letter")
    c.drawString(72, 680, "Employee Name: Alex Johnson")
    c.drawString(72, 660, "Employer Name: Acme Lending LLC")
    c.drawString(72, 640, "Position: Senior Operations Analyst")
    c.drawString(72, 620, "Employment Start Date: 01/15/2022")
    c.drawString(72, 600, "Employment Tenure: 49 months")
    c.drawString(72, 580, "Gross Monthly Income: $6,800.00")
    c.drawString(72, 560, "Status: Full-time, non-probationary")
    c.showPage()
    c.save()


def build_id_document(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, "Government Identification Document")
    c.drawString(72, 700, "Passport ID Document")
    c.drawString(72, 680, "Name: Alex Johnson")
    c.drawString(72, 660, "DOB: 08/17/1989")
    c.drawString(72, 640, "Address: 1456 Oak Ridge Drive, Austin, TX 78701")
    c.drawString(72, 620, "ID Number: P23874691")
    c.drawString(72, 600, "Issued Country: United States")
    c.drawString(72, 580, "KYC Verification: Complete")
    c.showPage()
    c.save()


def build_loan_application(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, "Mortgage Loan Application Summary")
    c.drawString(72, 700, "Borrower: Alex Johnson")
    c.drawString(72, 680, "DOB: 08/17/1989")
    c.drawString(72, 660, "Property Address: 1456 Oak Ridge Drive, Austin, TX 78701")
    c.drawString(72, 640, "Credit Score: 742")
    c.drawString(72, 620, "Loan Amount: $420,000.00")
    c.drawString(72, 600, "Property Value: $560,000.00")
    c.drawString(72, 580, "Monthly Income: $6,800.00")
    c.drawString(72, 560, "Monthly Debt: $1,850.00")
    c.drawString(72, 540, "Employment Tenure: 49 months")
    c.showPage()
    c.save()


def main() -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    build_w2(data_dir / "sample_w2.pdf")
    build_paystub(data_dir / "sample_paystub.pdf")
    build_bank_statement(data_dir / "sample_bank_statement.pdf")
    build_employment_letter(data_dir / "sample_employment_letter.pdf")
    build_id_document(data_dir / "sample_id_document.pdf")
    build_loan_application(data_dir / "sample_loan_application.pdf")
    print(f"Sample PDFs created in {data_dir}")


if __name__ == "__main__":
    main()
