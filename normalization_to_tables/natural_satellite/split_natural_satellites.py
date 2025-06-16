import pandas as pd
import os

input_csv = r"C:\Users\NITRO\OneDrive\Desktop\Talk2DB\space_mission dataset\natural_satellites.csv"
df = pd.read_csv(input_csv)

output_dir = "split_natural_satellite_tables"
os.makedirs(output_dir, exist_ok=True)

identity_columns = ["planet", "name"]
satellite_identity = df[identity_columns]
satellite_identity.to_csv(os.path.join(output_dir, "satellite_identity.csv"), index=False)

physical_columns = ["planet", "name", "gm", "radius", "density", "magnitude", "albedo"]
satellite_physical = df[physical_columns]
satellite_physical.to_csv(os.path.join(output_dir, "satellite_physical.csv"), index=False)

print("All files have been created successfully.")
