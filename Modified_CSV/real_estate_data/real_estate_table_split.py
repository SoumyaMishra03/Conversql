import pandas as pd

def split_real_estate_dataset(input_excel_file):
    df = pd.read_csv(input_excel_file)
    df.columns = df.columns.str.strip()

    properties_table = ['Name', 'Property Title', 'Price', 'Description']
    locations_table = ['Name', 'Location', 'Total_Area', 'Price_per_SQFT']
    features_table = ['Name', 'Baths', 'Balcony']

    properties_df = df[properties_table]
    locations_df = df[locations_table]
    features_df = df[features_table]

    properties_df.to_csv('properties_table.csv', index=False)
    locations_df.to_csv('locations_table.csv', index=False)
    features_df.to_csv('features_table.csv', index=False)

    print("Data has been split into multiple CSV files.")

input_excel_file = r'C:\Users\hbhan\OneDrive\Desktop\programming\internship\Talk2DB\csv\Real Estate Data V21.csv'
split_real_estate_dataset(input_excel_file)
