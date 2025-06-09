import pandas as pd

# Load the master CSV file
df = pd.read_csv(r"C:\Users\NITRO\OneDrive\Desktop\Datasets\employee_data.csv")

# --- 1. Create the Personal Data Table ---
# Select personal columns and drop any duplicates if needed
employee_personal = df[[
    "EmpID", "FirstName", "LastName", "DOB", "GenderCode",
    "RaceDesc", "MaritalDesc", "State", "LocationCode", "ADEmail"
]].drop_duplicates()
employee_personal.to_csv("employee_personal.csv", index=False)

# --- 2. Create the Employment Details Table ---
employee_employment = df[[
    "EmpID", "StartDate", "ExitDate", "Title", "Supervisor",
    "BusinessUnit", "EmployeeStatus", "EmployeeType", "PayZone",
    "EmployeeClassificationType", "DepartmentType", "Division",
    "JobFunctionDescription", "Performance Score", "Current Employee Rating"
]].drop_duplicates()
employee_employment.to_csv("employee_employment.csv", index=False)

# --- 3. Create the Termination Details Table ---
employee_termination = df[[
    "EmpID", "TerminationType", "TerminationDescription"
]].drop_duplicates()
employee_termination.to_csv("employee_termination.csv", index=False)

print("Created employee_personal.csv, employee_employment.csv, and employee_termination.csv successfully.")