from fastapi import FastAPI, HTTPException
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import urllib
import os

app = FastAPI(title="Hospital Analytics Backend")

# ========================================
# DATABASE CONFIGURATION
# ========================================
# 1. PASTE YOUR SERVER NAME HERE
SERVER_NAME = "LAPTOP-A27GM7FS\\SQLEXPRESS"
DATABASE_NAME = "HospitalAnalytics"

# ODBC Driver 17 is usually standard with SSMS 2022.
# If it fails, try "ODBC Driver 18 for SQL Server"
DRIVER = "ODBC Driver 17 for SQL Server"

connection_string = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    "Trusted_Connection=yes;"
    "Encrypt=no;"  # Required for some local SQL 2022 setups
)

quoted_conn = urllib.parse.quote_plus(connection_string)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_conn}")


@app.post("/etl/run-load")
def run_etl():
    """
    EXTRACT: From CSV
    LOAD: Into SQL Server 2022
    This fulfills the Backend/ETL requirement.
    """
    csv_folder = r"D:\Hospital_analytics\data\csv_data"
    # Order matters for foreign keys, though 'replace' handles it loosely
    tables = [
        "branches", "departments", "doctors", "patients",
        "admissions", "procedures", "billing", "outcomes", "bed_occupancy"
    ]

    report = {}

    if not os.path.exists(csv_folder):
        raise HTTPException(status_code=404, detail="CSV folder not found. Run Step 1 first!")

    try:
        for table in tables:
            file_path = os.path.join(csv_folder, f"{table}.csv")
            if os.path.exists(file_path):
                # Load CSV
                df = pd.read_csv(file_path)

                # Load to SQL Server
                # 'replace' will drop existing tables and recreate them
                df.to_sql(table, engine, if_exists="replace", index=False)
                report[table] = f"Successfully loaded {len(df)} rows"
            else:
                report[table] = "File missing"

        return {"status": "Success", "data": report}

    except Exception as e:
        return {"status": "Error", "detail": str(e)}
@app.get("/kpis/summary")
def kpi_summary():
    """
    Executive-level KPIs for hospital performance
    """
    query = """
    SELECT
        COUNT(*) AS total_admissions,
        AVG(length_of_stay) AS avg_los,
        SUM(CASE WHEN admission_type = 'Emergency' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS emergency_pct,
        SUM(CASE WHEN is_readmission = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS readmission_rate
    FROM admissions
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")[0]

@app.get("/kpis/bed-alerts")
def bed_occupancy_alerts():
    """
    Flags departments with critical bed occupancy (>90%)
    """
    query = """
    SELECT
        department_name,
        branch_id,
        snapshot_datetime,
        occupancy_rate
    FROM bed_occupancy
    WHERE occupancy_rate > 90
    ORDER BY occupancy_rate DESC
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")
@app.get("/kpis/emergency-load")
def emergency_load():
    """
    Emergency department pressure analysis
    """
    query = """
    SELECT
        DATENAME(WEEKDAY, admission_datetime) AS day_of_week,
        DATEPART(HOUR, admission_datetime) AS hour_of_day,
        COUNT(*) AS emergency_cases
    FROM admissions
    WHERE admission_type = 'Emergency'
    GROUP BY
        DATENAME(WEEKDAY, admission_datetime),
        DATEPART(HOUR, admission_datetime)
    ORDER BY emergency_cases DESC
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")
@app.get("/kpis/doctor-utilization")
def doctor_utilization():
    """
    Doctor workload and utilization based on procedures
    """
    query = """
    SELECT
        doc.doctor_name,
        dept.department_name,
        doc.available_hours,
        SUM(pr.duration_minutes) / 60.0 AS actual_hours_spent,
        (SUM(pr.duration_minutes) / 60.0 / NULLIF(doc.available_hours, 0)) * 100 AS utilization_pct
    FROM doctors doc
    JOIN departments dept ON doc.department_id = dept.department_id
    LEFT JOIN procedures pr ON doc.doctor_id = pr.doctor_id
    GROUP BY doc.doctor_name, dept.department_name, doc.available_hours
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")

@app.get("/")
def home():
    return {"message": "Hospital API is online"}

