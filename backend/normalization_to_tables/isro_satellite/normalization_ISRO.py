import pandas as pd
import os

input_csv = r"ISRO_Satellite_Dataset.csv"
df = pd.read_csv(input_csv)

output_dir = "split_isro_satellite_tables"
os.makedirs(output_dir, exist_ok=True)

basic_info_columns = [
    "Satellite ID(Fake)",
    "Name of Satellite, Alternate Names",
    "Current Official Name of Satellite",
    "Country/Org of UN Registry",
    "Country of Operator/Owner",
    "Operator/Owner",
    "Users",
    "Purpose",
    "Detailed Purpose"
]
basic_info = df[basic_info_columns]
basic_info.to_csv(os.path.join(output_dir, "basic_info.csv"), index=False)

orbital_info_columns = [
    "Satellite ID(Fake)",
    "Class of Orbit",
    "Type of Orbit",
    "Longitude of GEO (degrees)",
    "Perigee (km)",
    "Apogee (km)",
    "Eccentricity",
    "Inclination (degrees)",
    "Period (minutes)"
]
orbital_info = df[orbital_info_columns]
orbital_info.to_csv(os.path.join(output_dir, "orbital_info.csv"), index=False)

launch_info_columns = [
    "Satellite ID(Fake)",
    "Launch Mass (kg.)",
    "Dry Mass (kg.)",
    "Power (watts)",
    "Date of Launch",
    "Expected Lifetime (yrs.)",
    "Contractor",
    "Country of Contractor",
    "Launch Site",
    "Launch Vehicle",
    "COSPAR Number",
    "NORAD Number",
    "Comments"
]
launch_info = df[launch_info_columns]
launch_info.to_csv(os.path.join(output_dir, "launch_info.csv"), index=False)

print("All files have been created successfully.")
