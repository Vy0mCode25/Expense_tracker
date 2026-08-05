from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, employees, salary, employee_expenses, company_wages, summary

# Create all tables automatically on startup (simple setup, no migrations needed for now)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Company Expense & Salary Tracker", version="1.0.0")

# Allow frontend (React) to call this API - adjust origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(salary.router)
app.include_router(employee_expenses.router)
app.include_router(company_wages.router)
app.include_router(summary.router)


@app.get("/")
def root():
    return {"message": "Company Expense & Salary Tracker API is running"}


# TEMPORARY diagnostic route — remove once the database is confirmed to be persistent.
# Does NOT reveal the password, only which type of database is actually active.
@app.get("/debug-db-info")
def debug_db_info():
    import os
    return {
        "database_url_env_var_is_set": bool(os.environ.get("DATABASE_URL")),
        "engine_dialect_in_use": engine.dialect.name,  # "postgresql" = correct, "sqlite" = still wrong
    }