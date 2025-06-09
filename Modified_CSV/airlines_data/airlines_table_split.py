import pandas as pd

def split_dataset(input_excel_file):
    df = pd.read_csv(input_excel_file)
    passengers_table = ['Passenger ID', 'First Name','Last Name', 'Gender','Age', 'Nationality']
    passengers_df = df[passengers_table]
    airports_table = ['Airport Name','Airport Country Code','Country Name','Airport Continent','Continents']
    airports_df = df[airports_table]
    flights_table = [ 'Passenger ID','Airport Name','Departure Date','Arrival Airport','Pilot Name','Flight Status']
    flights_df = df[flights_table]   
    passengers_df.to_csv('passengers_table.csv', index=False)
    airports_df.to_csv('airports_table.csv', index=False)
    flights_df.to_csv('flights_table.csv', index=False)
    
    print("Data has been split into multiple CSV files.")


input_excel_file = r'C:\Users\hbhan\OneDrive\Desktop\programming\internship\csv\Airline Dataset.csv'  
split_dataset(input_excel_file)