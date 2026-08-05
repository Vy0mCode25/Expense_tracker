from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import verify_admin
from app import models, schemas

router = APIRouter(prefix="/employee-expenses", tags=["Employee Expenses"], dependencies=[Depends(verify_admin)])


@router.get("/", response_model=list[schemas.EmployeeExpenseOut])
def list_employee_expenses(month: str | None = None, employee_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.EmployeeExpense)
    if month:
        query = query.filter(models.EmployeeExpense.month == month)
    if employee_id:
        query = query.filter(models.EmployeeExpense.employee_id == employee_id)
    return query.order_by(models.EmployeeExpense.month.desc()).all()


@router.post("/", response_model=schemas.EmployeeExpenseOut)
def create_employee_expense(expense: schemas.EmployeeExpenseCreate, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == expense.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    new_expense = models.EmployeeExpense(**expense.model_dump())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@router.put("/{expense_id}", response_model=schemas.EmployeeExpenseOut)
def update_employee_expense(expense_id: int, updated: schemas.EmployeeExpenseCreate, db: Session = Depends(get_db)):
    expense = db.query(models.EmployeeExpense).filter(models.EmployeeExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Employee expense not found")
    for key, value in updated.model_dump().items():
        setattr(expense, key, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.patch("/{expense_id}/status", response_model=schemas.EmployeeExpenseOut)
def update_expense_status(expense_id: int, status: str, db: Session = Depends(get_db)):
    """Quick toggle — pass ?status=paid or ?status=pending"""
    if status not in ("paid", "pending"):
        raise HTTPException(status_code=400, detail="status must be 'paid' or 'pending'")
    expense = db.query(models.EmployeeExpense).filter(models.EmployeeExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Employee expense not found")
    expense.status = status
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
def delete_employee_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.EmployeeExpense).filter(models.EmployeeExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Employee expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Employee expense deleted successfully"}