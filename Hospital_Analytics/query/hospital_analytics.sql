USE HospitalAnalytics;

CREATE VIEW vw_AdmissionDetails AS 
SELECT 
    a.admission_id,
    p.patient_name,
    p.age,
    p.gender,
    d.department_name,
    doc.doctor_name,
    b.branch_name,
    a.admission_datetime,
    a.discharge_datetime,
    a.length_of_stay,
    a.is_readmission,
    bill.total_cost,
    out.outcome
FROM admissions a
JOIN patients p ON a.patient_id = p.patient_id
JOIN departments d ON a.department_id = d.department_id
JOIN doctors doc ON a.doctor_id = doc.doctor_id
JOIN branches b ON a.branch_id = b.branch_id
JOIN billing bill ON a.admission_id = bill.admission_id
JOIN outcomes out ON a.admission_id = out.admission_id;

CREATE VIEW vw_DoctorWorkload AS
SELECT 
    doc.doctor_name,
    dept.department_name,
    doc.available_hours,
    COUNT(pr.procedure_id) as total_procedures,
    SUM(pr.duration_minutes) / 60.0 as actual_hours_spent,
    (SUM(pr.duration_minutes) / 60.0 / NULLIF(doc.available_hours, 0)) * 100 as utilization_pct
FROM doctors doc
JOIN departments dept ON doc.department_id = dept.department_id
LEFT JOIN procedures pr ON doc.doctor_id = pr.doctor_id 
GROUP BY doc.doctor_name, dept.department_name, doc.available_hours;

SELECT TOP 10 * FROM vw_DoctorWorkload;

Select top 3 * 
from bed_occupancy