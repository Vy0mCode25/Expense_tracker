import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.auth import verify_admin
from app import models, schemas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

router = APIRouter(prefix="/summary", tags=["Summary"], dependencies=[Depends(verify_admin)])


def _get_monthly_totals(db: Session, month: str):
    total_salary = db.query(func.coalesce(func.sum(models.SalaryRecord.amount), 0.0)).filter(
        models.SalaryRecord.month == month
    ).scalar()

    total_employee_expense = db.query(func.coalesce(func.sum(models.EmployeeExpense.amount), 0.0)).filter(
        models.EmployeeExpense.month == month
    ).scalar()

    total_company_wages = db.query(func.coalesce(func.sum(models.CompanyWage.amount), 0.0)).filter(
        models.CompanyWage.month == month
    ).scalar()

    grand_total = total_salary + total_employee_expense + total_company_wages

    return {
        "month": month,
        "total_salary": total_salary,
        "total_employee_expense": total_employee_expense,
        "total_company_wages": total_company_wages,
        "grand_total": grand_total,
    }


@router.get("/{month}", response_model=schemas.MonthlySummary)
def monthly_summary(month: str, db: Session = Depends(get_db)):
    """month format: '2026-08' (YYYY-MM)"""
    return _get_monthly_totals(db, month)


@router.get("/{month}/report-pdf")
def monthly_report_pdf(month: str, db: Session = Depends(get_db)):
    """Generates a downloadable PDF report for the given month (YYYY-MM)."""
    totals = _get_monthly_totals(db, month)

    salary_records = (
        db.query(models.SalaryRecord, models.Employee.name)
        .join(models.Employee, models.SalaryRecord.employee_id == models.Employee.id)
        .filter(models.SalaryRecord.month == month)
        .all()
    )
    employee_expenses = (
        db.query(models.EmployeeExpense, models.Employee.name)
        .join(models.Employee, models.EmployeeExpense.employee_id == models.Employee.id)
        .filter(models.EmployeeExpense.month == month)
        .all()
    )
    company_wages = db.query(models.CompanyWage).filter(models.CompanyWage.month == month).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=18, spaceAfter=6)
    heading_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6)

    elements = []
    elements.append(Paragraph(f"Monthly Company Expense Report - {month}", title_style))
    elements.append(Spacer(1, 0.3 * cm))

    # ---- Summary cards table ----
    summary_data = [
        ["Total Salary", "Total Employee Expense", "Total Company Wages", "Grand Total"],
        [
            f"Rs. {totals['total_salary']:.2f}",
            f"Rs. {totals['total_employee_expense']:.2f}",
            f"Rs. {totals['total_company_wages']:.2f}",
            f"Rs. {totals['grand_total']:.2f}",
        ],
    ]
    summary_table = Table(summary_data, colWidths=[4.2 * cm] * 4)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f7fafc")),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)

    # ---- Salary section ----
    elements.append(Paragraph("Salary Records", heading_style))
    if salary_records:
        data = [["Employee", "Amount (Rs.)", "Status"]]
        for record, emp_name in salary_records:
            data.append([emp_name, f"{record.amount:.2f}", record.status])
        t = Table(data, colWidths=[7 * cm, 4 * cm, 4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a5568")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No salary records for this month.", styles["Normal"]))

    # ---- Employee expense section ----
    elements.append(Paragraph("Employee Expenses", heading_style))
    if employee_expenses:
        data = [["Employee", "Amount (Rs.)", "Reason", "Receipt"]]
        for expense, emp_name in employee_expenses:
            has_receipt = "Yes" if expense.receipt_base64 else "No"
            data.append([emp_name, f"{expense.amount:.2f}", expense.reason or "-", has_receipt])
        t = Table(data, colWidths=[5.5 * cm, 3.5 * cm, 4 * cm, 2 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a5568")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No employee expenses for this month.", styles["Normal"]))

    # ---- Company wages section ----
    elements.append(Paragraph("Company Wages (Rent, Bills, Vendor, etc.)", heading_style))
    if company_wages:
        data = [["Title", "Amount (Rs.)", "Notes"]]
        for wage in company_wages:
            data.append([wage.title, f"{wage.amount:.2f}", wage.notes or "-"])
        t = Table(data, colWidths=[7 * cm, 4 * cm, 4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a5568")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No company wage entries for this month.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    filename = f"company_expense_report_{month}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
