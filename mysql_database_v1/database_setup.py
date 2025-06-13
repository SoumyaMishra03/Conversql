import subprocess
import os

db_setup_scripts = [
    "mysql_airport_schema_setup.py",
    "mysql_employment_schema_setup.py",
    "mysql_financial_schema_setup.py",
    "mysql_hospital_schema_setup.py",
    "mysql_product_schema_setup.py",
    "mysql_realestate_schema_setup.py",
    "mysql_student_schema_setup.py"
]

for script in db_setup_scripts:
    print(f"Running setup: {script}")
    subprocess.run(["python", script])  

db_insert_scripts = {
    "insertion_airport.py",
    "employee_insertion.py",
    "bank_insertion.py",
    "hospital_insertion.py",
    "product_insertion.py",
    "realestate_insertion.py",
    "student_insertion.py"
}

for script in db_insert_scripts:
    print(f"Launching insert: {script}")
    subprocess.run(["python", script])  

print("--- All database setup and insertions launched ---")