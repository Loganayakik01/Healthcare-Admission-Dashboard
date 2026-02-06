import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
# ========================================
# INITIAL SETUP
# ========================================
fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)

print("=" * 70)
print("HOSPITAL ANALYTICS DATA GENERATOR - SQL Server")
print("=" * 70)

START_DATE = datetime(2025, 8, 1)
END_DATE = datetime(2026, 1, 31)

NUM_PATIENTS = 3000
NUM_ADMISSIONS = 3000

DEPARTMENTS = [
    "Cardiology", "Oncology", "Orthopedics",
    "Pediatrics", "Emergency", "General Medicine"
]

BRANCHES = [
    {"name": "Chennai Main", "city": "Chennai", "beds": 250},
    {"name": "Bangalore North", "city": "Bangalore", "beds": 200},
    {"name": "Hyderabad Central", "city": "Hyderabad", "beds": 180}
]

INSURANCE_TYPES = ["Government", "Private", "Self-Pay"]
OUTCOMES = ["Recovered", "Improved", "Transferred", "Deceased"]

LOS_RULES = {
    "Emergency": (1, 3),
    "Cardiology": (4, 7),
    "Oncology": (6, 12),
    "Orthopedics": (3, 6),
    "Pediatrics": (2, 5),
    "General Medicine": (2, 6)
}

COST_RULES = {
    "Emergency": (10000, 40000),
    "Cardiology": (30000, 120000),
    "Oncology": (50000, 200000),
    "Orthopedics": (20000, 80000),
    "Pediatrics": (8000, 35000),
    "General Medicine": (12000, 45000)
}

PROCEDURE_TYPES = {
    "Cardiology": ["Angioplasty", "ECG", "Stress Test", "Cardiac Catheterization"],
    "Oncology": ["Chemotherapy", "Radiation", "Biopsy", "Immunotherapy"],
    "Orthopedics": ["Fracture Repair", "Joint Replacement", "Arthroscopy", "Spinal Surgery"],
    "Pediatrics": ["Vaccination", "Appendectomy", "General Checkup"],
    "Emergency": ["Trauma Care", "CPR", "Emergency Surgery", "Stabilization"],
    "General Medicine": ["Diagnostic Tests", "IV Therapy", "General Treatment"]
}

# ========================================
# 1. BRANCHES
# ========================================
print("\n[1/9] Generating Branches...")
branches_df = pd.DataFrame(
    [[i + 1, b["name"], b["city"], b["beds"]] for i, b in enumerate(BRANCHES)],
    columns=["branch_id", "branch_name", "city", "total_beds"]
)
print(f" {len(branches_df)} branches")

# ========================================
# 2. DEPARTMENTS
# ========================================
print("\n[2/9] Generating Departments...")
departments_data = []
dept_id = 1

allocation = {
    "Emergency": 0.25,
    "General Medicine": 0.25,
    "Cardiology": 0.15,
    "Orthopedics": 0.15,
    "Pediatrics": 0.12,
    "Oncology": 0.08
}

for branch_id, b in enumerate(BRANCHES, 1):
    for dept in DEPARTMENTS:
        departments_data.append([
            dept_id, dept, branch_id, int(b["beds"] * allocation[dept])
        ])
        dept_id += 1

departments_df = pd.DataFrame(
    departments_data,
    columns=["department_id", "department_name", "branch_id", "total_beds"]
)
print(f" {len(departments_df)} departments")

# ========================================
# 3. DOCTORS
# ========================================
print("\n[3/9] Generating Doctors...")
doctors_data = []
doctor_id = 1

for _, dept in departments_df.iterrows():
    for _ in range(random.randint(3, 5)):
        available = 160

        # Department-specific utilization
        if dept["department_name"] in ["Emergency", "General Medicine"]:
            utilization = random.uniform(0.75, 0.95)
        elif dept["department_name"] == "Oncology":
            utilization = random.uniform(0.65, 0.85)
        else:
            utilization = random.uniform(0.60, 0.80)

        doctors_data.append([
            doctor_id,
            fake.name(),
            dept["department_id"],
            dept["department_name"],
            available,
            int(available * utilization)
        ])
        doctor_id += 1

doctors_df = pd.DataFrame(
    doctors_data,
    columns=["doctor_id", "doctor_name", "department_id",
             "department_name", "available_hours", "booked_hours"]
)
print(f"  {len(doctors_df)} doctors")

# ========================================
# 4. PATIENTS
# ========================================
print("\n[4/9] Generating Patients...")
patients_data = []

for pid in range(1, NUM_PATIENTS + 1):
    # Better age distribution
    age_group = random.choices(
        ["child", "young", "adult", "senior", "elderly"],
        weights=[10, 20, 30, 28, 12]
    )[0]

    age_ranges = {
        "child": (0, 14),
        "young": (15, 35),
        "adult": (36, 55),
        "senior": (56, 75),
        "elderly": (76, 95)
    }

    age = random.randint(*age_ranges[age_group])

    patients_data.append([
        pid, fake.name(), age,
        random.choice(["Male", "Female"]),
        random.choices(INSURANCE_TYPES, weights=[40, 45, 15])[0]
    ])

patients_df = pd.DataFrame(
    patients_data,
    columns=["patient_id", "patient_name", "age", "gender", "insurance_type"]
)
print(f"  {len(patients_df)} patients")

# ========================================
# 5. ADMISSIONS (WITH PATTERNS!)
# ========================================
print("\n[5/9] Generating Admissions (with seasonal patterns)...")
admissions_data = []
used_patients = []

for aid in range(1, NUM_ADMISSIONS + 1):
    if aid % 500 == 0:
        print(f"  ... {aid}/{NUM_ADMISSIONS}")

    # FIX: 10% READMISSIONS
    if len(used_patients) > 100 and random.random() < 0.10:
        patient = patients_df[patients_df["patient_id"].isin(used_patients)].sample(1).iloc[0]
    else:
        patient = patients_df.sample(1).iloc[0]
        used_patients.append(patient["patient_id"])

    age = patient["age"]

    # FIX: Age-based department selection
    if age < 15:
        dept = "Pediatrics"
    elif age > 60 and random.random() < 0.35:
        dept = random.choices(["Cardiology", "Oncology"], weights=[60, 40])[0]
    elif age > 50 and random.random() < 0.20:
        dept = "Cardiology"
    else:
        dept = random.choice(DEPARTMENTS)

    branch_id = random.choices(
        range(1, len(BRANCHES) + 1),
        weights=[b["beds"] for b in BRANCHES]
    )[0]

    # FIX: SEASONAL PATTERNS
    admit_date = fake.date_time_between(START_DATE, END_DATE)
    is_weekend = admit_date.weekday() >= 5

    # FIX: Emergency probability based on time
    if dept == "Emergency":
        emergency_prob = 0.90
    elif is_weekend:
        emergency_prob = 0.45
    else:
        emergency_prob = 0.30

    is_emergency = random.random() < emergency_prob

    # FIX: Time-based admission patterns
    if is_emergency:
        hour = random.choices(
            list(range(24)),
            weights=[3, 2, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 4, 5, 6, 7, 8, 9, 8, 7, 6, 5]
        )[0]
    else:
        hour = random.randint(8, 16)

    admit_time = admit_date.replace(hour=hour, minute=random.randint(0, 59))

    # FIX: Department-specific LOS
    los = random.randint(*LOS_RULES[dept])

    # FIX: Seasonal LOS variation
    if admit_time.month in [12, 1] and dept in ["Emergency", "General Medicine"]:
        los += random.randint(0, 2)  # Winter flu = longer stays

    discharge = admit_time + timedelta(days=los, hours=random.randint(8, 16))
    is_readmission = 0
    dept_id = departments_df[
        (departments_df.department_name == dept) &
        (departments_df.branch_id == branch_id)
        ].iloc[0]["department_id"]

    doctor_id = doctors_df[
        doctors_df.department_id == dept_id
        ].sample(1).iloc[0]["doctor_id"]

    admissions_data.append([
        aid, patient["patient_id"], dept_id, dept,
        branch_id, doctor_id, admit_time, discharge,
        "Emergency" if is_emergency else "Scheduled", los
    ])

admissions_df = pd.DataFrame(
    admissions_data,
    columns=[
        "admission_id", "patient_id", "department_id", "department_name",
        "branch_id", "doctor_id", "admission_datetime",
        "discharge_datetime", "admission_type", "length_of_stay"
    ]
)
admissions_df = admissions_df.sort_values(
    ["patient_id", "admission_datetime"]
)

admissions_df["is_readmission"] = 0

for pid, group in admissions_df.groupby("patient_id"):
    prev_discharge = None
    for idx, row in group.iterrows():
        if prev_discharge:
            if (row["admission_datetime"] - prev_discharge).days <= 30:
                admissions_df.at[idx, "is_readmission"] = 1
        prev_discharge = row["discharge_datetime"]

print(f" {len(admissions_df)} admissions")
print("\n[5.1] Flagging 30-day readmissions...")
admissions_df = admissions_df.sort_values(["patient_id", "admission_datetime"])
admissions_df["is_readmission"] = 0

for pid, group in admissions_df.groupby("patient_id"):
    if len(group) > 1:
        prev_discharge = None
        for idx, row in group.iterrows():
            if prev_discharge and (row["admission_datetime"] - prev_discharge).days <= 30:
                admissions_df.at[idx, "is_readmission"] = 1
            prev_discharge = row["discharge_datetime"]

# Re-sort by admission_id to keep it clean for the SQL load
admissions_df = admissions_df.sort_values("admission_id")
print(f" Flagged {admissions_df['is_readmission'].sum()} readmissions")
# ========================================
# 6. PROCEDURES (DEPARTMENT-SPECIFIC)
# ========================================
print("\n[6/9] Generating Procedures...")
procedures_data = []
pid = 1

for _, adm in admissions_df.iterrows():
    #  FIX: Department-specific procedure counts
    if adm["department_name"] == "Oncology":
        num_procedures = random.randint(2, 5)
    elif adm["department_name"] == "Cardiology":
        num_procedures = random.randint(1, 3)
    else:
        num_procedures = random.randint(1, 2)

    for _ in range(num_procedures):
        days_into = random.randint(0, max(0, adm["length_of_stay"] - 1))

        procedures_data.append([
            pid,
            adm["admission_id"],
            adm["doctor_id"],
            random.choice(PROCEDURE_TYPES[adm["department_name"]]),
            adm["admission_datetime"] + timedelta(days=days_into),
            random.randint(30, 240)
        ])
        pid += 1

procedures_df = pd.DataFrame(
    procedures_data,
    columns=["procedure_id", "admission_id","doctor_id",
             "procedure_type", "procedure_datetime", "duration_minutes"]
)
print(f" {len(procedures_df)} procedures")

# ========================================
# 7. BILLING (REALISTIC COSTS)
# ========================================
print("\n[7/9] Generating Billing...")
billing_data = []

for _, adm in admissions_df.iterrows():
    dept = adm["department_name"]
    los = adm["length_of_stay"]

    #  FIX: Department-specific cost ranges
    base_min, base_max = COST_RULES[dept]

    room_cost = random.randint(3000, 8000) * los

    num_proc = len(procedures_df[procedures_df["admission_id"] == adm["admission_id"]])
    procedure_cost = random.randint(base_min // 2, base_max // 2) * num_proc

    medicine_cost = random.randint(2000, 30000)
    diagnostic_cost = random.randint(3000, 15000)

    total = room_cost + procedure_cost + medicine_cost + diagnostic_cost

    # FIX: Insurance-based coverage
    patient = patients_df[patients_df["patient_id"] == adm["patient_id"]].iloc[0]

    if patient["insurance_type"] == "Government":
        insurance_covered = total * random.uniform(0.70, 0.90)
    elif patient["insurance_type"] == "Private":
        insurance_covered = total * random.uniform(0.60, 0.85)
    else:
        insurance_covered = 0

    patient_paid = total - insurance_covered

    billing_data.append([
        adm["admission_id"],
        room_cost,
        procedure_cost,
        medicine_cost,
        diagnostic_cost,
        total,
        round(insurance_covered, 2),
        round(patient_paid, 2)
    ])

billing_df = pd.DataFrame(
    billing_data,
    columns=[
        "admission_id", "room_cost", "procedure_cost",
        "medicine_cost", "diagnostic_cost",
        "total_cost", "insurance_covered", "patient_paid"
    ]
)
print(f"{len(billing_df)} billing records")

# ========================================
# 8. OUTCOMES (DEPARTMENT-SPECIFIC)
# ========================================
print("\n[8/9] Generating Outcomes...")
outcomes_data = []

for _, adm in admissions_df.iterrows():
    dept = adm["department_name"]
    patient = patients_df[patients_df["patient_id"] == adm["patient_id"]].iloc[0]

    #FIX: Realistic outcome distributions
    if dept == "Oncology":
        outcome = random.choices(OUTCOMES, weights=[50, 30, 15, 5])[0]
    elif dept == "Emergency":
        outcome = random.choices(OUTCOMES, weights=[60, 25, 10, 5])[0]
    elif patient["age"] > 75:
        outcome = random.choices(OUTCOMES, weights=[60, 25, 12, 3])[0]
    else:
        outcome = random.choices(OUTCOMES, weights=[75, 20, 4, 1])[0]

    outcomes_data.append([adm["admission_id"], outcome])

outcomes_df = pd.DataFrame(
    outcomes_data,
    columns=["admission_id", "outcome"]
)
print(f" {len(outcomes_df)} outcomes")

# ========================================
# 9. BED OCCUPANCY (CRITICAL!)
# ========================================
print("\n[9/9] Generating Bed Occupancy snapshots...")
bed_occupancy_data = []
snapshot_id = 1

current_date = START_DATE
while current_date <= END_DATE:
    snapshot_time = current_date.replace(hour=8, minute=0)

    for _, dept in departments_df.iterrows():
        # Count active admissions at this time
        active = admissions_df[
            (admissions_df["department_id"] == dept["department_id"]) &
            (admissions_df["admission_datetime"] <= snapshot_time) &
            (admissions_df["discharge_datetime"] >= snapshot_time)
            ]

        occupied = min(len(active), dept["total_beds"])
        occupancy_rate = (occupied / dept["total_beds"] * 100) if dept["total_beds"] > 0 else 0

        bed_occupancy_data.append([
            snapshot_id,
            dept["department_id"],
            dept["department_name"],
            dept["branch_id"],
            snapshot_time,
            occupied,
            dept["total_beds"],
            round(occupancy_rate, 2)
        ])
        snapshot_id += 1

    current_date += timedelta(days=1)

bed_occupancy_df = pd.DataFrame(
    bed_occupancy_data,
    columns=["snapshot_id", "department_id", "department_name",
             "branch_id", "snapshot_datetime", "occupied_beds",
             "total_beds", "occupancy_rate"]
)
print(f" {len(bed_occupancy_df)} snapshots")
print("\n" + "=" * 70)
print("EXPORTING CSV FILES")
print("=" * 70)


os.makedirs("csv_data", exist_ok=True)

branches_df.to_csv("csv_data/branches.csv", index=False)
departments_df.to_csv("csv_data/departments.csv", index=False)
doctors_df.to_csv("csv_data/doctors.csv", index=False)
patients_df.to_csv("csv_data/patients.csv", index=False)
admissions_df.to_csv("csv_data/admissions.csv", index=False)
procedures_df.to_csv("csv_data/procedures.csv", index=False)
billing_df.to_csv("csv_data/billing.csv", index=False)
outcomes_df.to_csv("csv_data/outcomes.csv", index=False)
bed_occupancy_df.to_csv("csv_data/bed_occupancy.csv", index=False)

print("CSV files generated successfully in /csv_data folder")
print("Step 1 complete — Data generation isolated")
print("=" * 70)
