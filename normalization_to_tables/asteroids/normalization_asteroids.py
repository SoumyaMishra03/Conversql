import pandas as pd
import os

input_csv = r"C:\Users\NITRO\OneDrive\Desktop\Talk2DB\space_mission dataset\asteroids.csv"
df = pd.read_csv(input_csv)

output_dir = "split_asteroids_tables"
os.makedirs(output_dir, exist_ok=True)

neo_reference_columns = [
    "Neo Reference ID", "Name", "Absolute Magnitude",
    "Est Dia in KM(min)", "Est Dia in KM(max)", 
    "Est Dia in M(min)", "Est Dia in M(max)",
    "Est Dia in Miles(min)", "Est Dia in Miles(max)",
    "Est Dia in Feet(min)", "Est Dia in Feet(max)"
]
neo_reference = df[neo_reference_columns]
neo_reference.to_csv(os.path.join(output_dir, "neo_reference.csv"), index=False)

close_approach_columns = [
    "Neo Reference ID",    
    "Close Approach Date", "Epoch Date Close Approach",
    "Relative Velocity km per sec", "Relative Velocity km per hr",
    "Miles per hour", "Miss Dist.(Astronomical)",
    "Miss Dist.(lunar)", "Miss Dist.(kilometers)",
    "Miss Dist.(miles)"
]
close_approach = df[close_approach_columns]
close_approach.to_csv(os.path.join(output_dir, "close_approach.csv"), index=False)

orbit_data_columns = [
    "Neo Reference ID",    
    "Orbiting Body", "Orbit ID", "Orbit Determination Date",
    "Orbit Uncertainity", "Minimum Orbit Intersection", "Jupiter Tisserand Invariant",
    "Epoch Osculation", "Eccentricity", "Semi Major Axis","Inclination",
    "Asc Node Longitude", "Orbital Period", "Perihelion Distance",
    "Perihelion Arg", "Aphelion Dist", "Perihelion Time",
    "Mean Anomaly", "Mean Motion", "Equinox", "Hazardous"
]
orbit_data = df[orbit_data_columns]
orbit_data.to_csv(os.path.join(output_dir, "orbit_data.csv"), index=False)

print("All files have been created successfully.")
