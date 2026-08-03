from pydantic import BaseModel
import datetime
from typing import Optional


# ---------- Employee ----------
class EmployeeBase(BaseModel):
    name: str
    designation: Optional[str] = None
    salary: float
    contact: Optional[str] = None
    join_date: Optional[datetime.date] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Salary Record ----------
class SalaryRecordBase(BaseModel):
    employee_id: int
    month: str  # "2026-08"
    amount: float
    status: Optional[str] = "pending"


class SalaryRecordCreate(SalaryRecordBase):
    pass


class SalaryRecordOut(SalaryRecordBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Employee Expense ----------
class EmployeeExpenseBase(BaseModel):
    employee_id: int
    amount: float
    reason: Optional[str] = None
    month: str  # "2026-08"
    date: Optional[datetime.date] = None


class EmployeeExpenseCreate(EmployeeExpenseBase):
    pass


class EmployeeExpenseOut(EmployeeExpenseBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Company Wage ----------
class CompanyWageBase(BaseModel):
    title: str
    amount: float
    month: str  # "2026-08"
    date: Optional[datetime.date] = None
    notes: Optional[str] = None


class CompanyWageCreate(CompanyWageBase):
    pass


class CompanyWageOut(CompanyWageBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Summary ----------
class MonthlySummary(BaseModel):
    month: str
    total_salary: float
    total_employee_expense: float
    total_company_wages: float
    grand_total: float
