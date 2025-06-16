import pandas as pd

def normalize(input_file):
    df = pd.read_csv(input_file)

    organization_table = ["Organisation","Location"]
    rockets_table = ["Organisation","Details","Rocket_Status","Price"]
    missions_table = ["Organisation","Mission_Status"]

    org_df = df[organization_table]
    rocket_df = df[rockets_table]
    mission_df = df[missions_table]
    org_df.to_csv("organizations.csv", index=False)
    rocket_df.to_csv("rockets.csv", index=False)
    mission_df.to_csv("missions.csv", index=False)

    print("data split successfully !")

input_file = r'space_missions.csv'
normalize(input_file)
