from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    designation = Column(String, nullable=True)
    salary = Column(Float, nullable=False, default=0)  # base/monthly salary
    contact = Column(String, nullable=True)
    join_date = Column(Date, nullable=True)

    salary_records = relationship("SalaryRecord", back_populates="employee", cascade="all, delete")
    expenses = relationship("EmployeeExpense", back_populates="employee", cascade="all, delete")


class SalaryRecord(Base):
    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month = Column(String, nullable=False)  # format: "2026-08"
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending / paid

    employee = relationship("Employee", back_populates="salary_records")


class EmployeeExpense(Base):
    __tablename__ = "employee_expenses"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    month = Column(String, nullable=False)  # format: "2026-08"
    date = Column(Date, nullable=True)
    receipt_base64 = Column(Text, nullable=True)  # bill/receipt photo, stored as base64 data URL

    employee = relationship("Employee", back_populates="expenses")


class CompanyWage(Base):
    __tablename__ = "company_wages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # e.g. Rent, Electricity Bill, Vendor Payment
    amount = Column(Float, nullable=False)
    month = Column(String, nullable=False)  # format: "2026-08"
    date = Column(Date, nullable=True)
    notes = Column(String, nullable=True)
