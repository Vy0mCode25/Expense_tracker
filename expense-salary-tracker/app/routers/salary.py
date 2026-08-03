from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/salary", tags=["Salary"])


@router.get("/", response_model=list[schemas.SalaryRecordOut])
def list_salary_records(month: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.SalaryRecord)
    if month:
        query = query.filter(models.SalaryRecord.month == month)
    return query.all()


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
