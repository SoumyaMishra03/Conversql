import pandas as pd
import os

input_csv = r"rockets.csv"
df = pd.read_csv(input_csv)

output_dir = "split_rockets_tables"
os.makedirs(output_dir, exist_ok=True)

rocket_general_info_cols = ["Name", "Cmp", "Wiki", "Status"]
rocket_general_info = df[rocket_general_info_cols]
rocket_general_info.to_csv(os.path.join(output_dir, "rocket_general_info.csv"), index=False)

technical_specs_cols = [
    "Name",
    "Liftoff Thrust",
    "Payload to LEO",
    "Stages",
    "Strap-ons",
    "Rocket Height",
    "Price",
    "Payload to GTO",
    "Fairing Diameter",
    "Fairing Height"
]
rocket_technical_specs = df[technical_specs_cols]
rocket_technical_specs.to_csv(os.path.join(output_dir, "rocket_technical_specs.csv"), index=False)

print("All files have been created successfully.")
