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


def main() -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    build_w2(data_dir / "sample_w2.pdf")
    build_paystub(data_dir / "sample_paystub.pdf")
    print(f"Sample PDFs created in {data_dir}")


if __name__ == "__main__":
    main()
