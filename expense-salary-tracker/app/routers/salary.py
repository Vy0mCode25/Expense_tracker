from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import verify_admin
from app import models, schemas
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

router = APIRouter(prefix="/salary", tags=["Salary"], dependencies=[Depends(verify_admin)])


@router.get("/", response_model=list[schemas.SalaryRecordOut])
def list_salary_records(month: str | None = None, employee_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.SalaryRecord)
    if month:
        query = query.filter(models.SalaryRecord.month == month)
    if employee_id:
        query = query.filter(models.SalaryRecord.employee_id == employee_id)
    return query.order_by(models.SalaryRecord.month.desc()).all()


@router.post("/", response_model=schemas.SalaryRecordOut)
def create_salary_record(record: schemas.SalaryRecordCreate, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == record.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    new_record = models.SalaryRecord(**record.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.patch("/{record_id}/status", response_model=schemas.SalaryRecordOut)
def update_salary_status(record_id: int, status: str, db: Session = Depends(get_db)):
    """Quick toggle — pass ?status=paid or ?status=pending"""
    if status not in ("paid", "pending"):
        raise HTTPException(status_code=400, detail="status must be 'paid' or 'pending'")
    record = db.query(models.SalaryRecord).filter(models.SalaryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Salary record not found")
    record.status = status
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=schemas.SalaryRecordOut)
def update_salary_record(record_id: int, updated: schemas.SalaryRecordCreate, db: Session = Depends(get_db)):
    record = db.query(models.SalaryRecord).filter(models.SalaryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Salary record not found")
    for key, value in updated.model_dump().items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_salary_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(models.SalaryRecord).filter(models.SalaryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Salary record not found")
    db.delete(record)
    db.commit()
    return {"message": "Salary record deleted successfully"}


@router.get("/{record_id}/slip-pdf")
def salary_slip_pdf(record_id: int, db: Session = Depends(get_db)):
    """Generates a downloadable salary slip PDF for one employee, one month."""
    record = db.query(models.SalaryRecord).filter(models.SalaryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Salary record not found")
    employee = db.query(models.Employee).filter(models.Employee.id == record.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    company_style = ParagraphStyle("Company", parent=styles["Heading1"], fontSize=18, textColor=colors.HexColor("#0B2A45"))
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#66727C"), spaceAfter=14)
    title_style = ParagraphStyle("SlipTitle", parent=styles["Heading2"], fontSize=14, spaceBefore=10, spaceAfter=10)

    elements = []
    elements.append(Paragraph("AD Tech Solution", company_style))
    elements.append(Paragraph("Expense &amp; Salary Ledger", sub_style))
    elements.append(Paragraph(f"Salary Slip — {record.month}", title_style))

    info_data = [
        ["Employee Name", employee.name],
        ["Designation", employee.designation or "-"],
        ["Contact", employee.contact or "-"],
        ["Pay Period", record.month],
        ["Status", record.status.upper()],
        ["Issued On", date.today().isoformat()],
    ]
    info_table = Table(info_data, colWidths=[5 * cm, 10 * cm])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#66727C")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E8EC")),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.6 * cm))

    amount_data = [["Description", "Amount (Rs.)"], ["Net Salary Paid", f"{record.amount:.2f}"]]
    amount_table = Table(amount_data, colWidths=[10 * cm, 5 * cm])
    amount_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B2A45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E1E8EC")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(amount_table)
    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph("This is a system-generated salary slip.", sub_style))

    doc.build(elements)
    buffer.seek(0)

    filename = f"salary_slip_{employee.name.replace(' ', '_')}_{record.month}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
