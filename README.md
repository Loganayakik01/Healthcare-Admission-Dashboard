**Hospital Analytics Dashboard**

**Overview**
This project is a hospital analytics platform designed to provide real-time insights into operations, patient flow, doctor utilization, and financial performance.

**Problem Statement**
Hospitals lack centralized visibility into bed occupancy, admissions, staff workload, and costs, leading to inefficiencies and delayed decisions.

**Solution**
This solution uses synthetic data, SQL analytics, APIs, and Power BI dashboards to enable data-driven hospital management.

**Tech Stack**
- Python (Data Generation, ETL)
- SQL Server (Data Storage & Views)
- FastAPI (Backend APIs)
- Power BI (Visualization & Reporting)

**Project Components**

**1. Data Generation**
Realistic hospital data is generated using Python and Faker, covering patients, admissions, doctors, billing, outcomes, and bed occupancy.

**2. Database & Views**
Data is loaded into SQL Server. Analytical views are created for optimized reporting.

**3. Backend API**
FastAPI exposes KPIs such as occupancy alerts, doctor utilization, and emergency load.

**4. Power BI Dashboard**
Interactive dashboards with slicers for branch and time period. Includes automated monthly reporting.

**Key Features**
- Bed Occupancy Rate
- Average Length of Stay (ALOS)
- Doctor Utilization
- Emergency vs Scheduled Admissions
- Financial Analytics
- Monthly Automated Reports

**How to Run**
1. Run data generation script
2. Load data into SQL Server
3. Start FastAPI backend
4. Open Power BI file and refresh data
