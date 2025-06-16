import pandas as pd
import os

input_csv = r"C:\Users\NITRO\OneDrive\Desktop\Talk2DB\space_mission dataset\astronauts.csv"
df = pd.read_csv(input_csv)

output_dir = "split_astronauts_tables"
os.makedirs(output_dir, exist_ok=True)

personal_info_columns = [
    "id", 
    "number", 
    "nationwide_number", 
    "name", 
    "original_name", 
    "sex", 
    "year_of_birth", 
    "nationality", 
    "military_civilian"
]
personal_info = df[personal_info_columns]
personal_info.to_csv(os.path.join(output_dir, "personal_info.csv"), index=False)

mission_info_columns = [
    "id",
    "selection", 
    "year_of_selection", 
    "mission_number", 
    "total_number_of_missions", 
    "occupation", 
    "year_of_mission", 
    "mission_title"
]
mission_info = df[mission_info_columns]
mission_info.to_csv(os.path.join(output_dir, "mission_info.csv"), index=False)

mission_performance_columns = [
    "id",
    "ascend_shuttle", 
    "in_orbit", 
    "descend_shuttle", 
    "hours_mission", 
    "total_hrs_sum", 
    "field21", 
    "eva_hrs_mission", 
    "total_eva_hrs"
]
mission_performance = df[mission_performance_columns]
mission_performance.to_csv(os.path.join(output_dir, "mission_performance.csv"), index=False)

print("All files have been created successfully.")
