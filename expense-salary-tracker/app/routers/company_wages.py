from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import verify_admin
from app import models, schemas

router = APIRouter(prefix="/company-wages", tags=["Company Wages"], dependencies=[Depends(verify_admin)])


@router.get("/", response_model=list[schemas.CompanyWageOut])
def list_company_wages(month: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.CompanyWage)
    if month:
        query = query.filter(models.CompanyWage.month == month)
    return query.all()


@router.post("/", response_model=schemas.CompanyWageOut)
def create_company_wage(wage: schemas.CompanyWageCreate, db: Session = Depends(get_db)):
    new_wage = models.CompanyWage(**wage.model_dump())
    db.add(new_wage)
    db.commit()
    db.refresh(new_wage)
    return new_wage


@router.put("/{wage_id}", response_model=schemas.CompanyWageOut)
def update_company_wage(wage_id: int, updated: schemas.CompanyWageCreate, db: Session = Depends(get_db)):
    wage = db.query(models.CompanyWage).filter(models.CompanyWage.id == wage_id).first()
    if not wage:
        raise HTTPException(status_code=404, detail="Company wage entry not found")
    for key, value in updated.model_dump().items():
        setattr(wage, key, value)
    db.commit()
    db.refresh(wage)
    return wage


@router.delete("/{wage_id}")
def delete_company_wage(wage_id: int, db: Session = Depends(get_db)):
    wage = db.query(models.CompanyWage).filter(models.CompanyWage.id == wage_id).first()
    if not wage:
        raise HTTPException(status_code=404, detail="Company wage entry not found")
    db.delete(wage)
    db.commit()
    return {"message": "Company wage entry deleted successfully"}
