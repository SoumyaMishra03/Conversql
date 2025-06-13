import pandas as pd

def split_hospital_data(input_csv_file):
    # Load the master CSV file
    df = pd.read_csv(input_csv_file)
    
    # --- 1. Create the Patients table ---
    # Select patient-specific columns and remove duplicates if the same patient appears multiple times
    patients_columns = ['Patient_ID', 'Age', 'Gender']
    patients_df = df[patients_columns].drop_duplicates()
    patients_df.to_csv("patients.csv", index=False)
    
    # --- 2. Create the Hospital Encounters table ---
    # Select columns related to clinical and encounter details,
    # These details may be repeated if a patient has multiple encounters.
    encounters_columns = ['Patient_ID', 'Condition', 'Procedure', 'Cost', 'Length_of_Stay', 'Readmission', 'Outcome', 'Satisfaction']
    encounters_df = df[encounters_columns]
    encounters_df.to_csv("hospital_encounters.csv", index=False)
    
    print("Created patients.csv and hospital_encounters.csv successfully.")

# Provide the input CSV filename and split the data
input_csv_file = r"C:\Users\NITRO\OneDrive\Desktop\Datasets\hospital data analysis.csv"
split_hospital_data(input_csv_file)