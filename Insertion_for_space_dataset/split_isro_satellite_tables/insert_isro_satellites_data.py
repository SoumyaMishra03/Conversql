import mysql.connector
import pandas as pd

def convert_date_columns(df, date_columns):
    """
    Convert columns containing Unix epoch timestamps (in milliseconds)
    into a YYYY-MM-DD string. Converts the column values by first converting
    to float then dividing by 1000 (to get seconds). Any failures will result in None.
    """
    for col in date_columns:
        if col in df.columns:
            # Try converting the column to float, then to datetime.
            try:
                df[col] = pd.to_datetime(df[col].astype(float) / 1000, unit='s', errors='coerce').dt.strftime('%Y-%m-%d')
            except Exception:
                df[col] = None
    return df

def insert_data(cursor, table_name, csv_file, columns, date_cols=None, batch_size=500):
    """
    Bulk insert data from a CSV file into the specified table.
    
    - Reads the CSV with all columns as string.
    - Uses regex replacement to convert any cell containing only "nan" (ignoring case/whitespace) to None.
    - Converts designated date columns if needed.
    - Builds tuples for insertion and runs in batches.
    """
    # Build the INSERT statement with placeholders.
    placeholders = ", ".join(["%s"] * len(columns))
    cols = ", ".join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
    
    # Read the CSV forcing all columns as strings.
    df = pd.read_csv(csv_file, dtype=str)
    
    # Convert date columns if required.
    if date_cols is not None:
        df = convert_date_columns(df, date_cols)
    
    # Replace any cells matching a pattern of "nan" (case-insensitive, with optional whitespace) with None.
    df = df.replace(r'^\s*nan\s*$', None, regex=True)
    
    # Additionally, fill any remaining NA (should be None already).
    df = df.where(pd.notnull(df), None)
    
    # Extract only the selected columns and convert DataFrame rows into a list of tuples.
    data = list(df[columns].itertuples(index=False, name=None))
    
    # Insert the data in chunks.
    for i in range(0, len(data), batch_size):
        chunk = data[i:i + batch_size]
        cursor.executemany(insert_sql, chunk)
    print(f"Inserted {len(data)} rows into table {table_name} from {csv_file}.")

def main():
    db_name = 'isro_satellites_db'
    config = {
        'user': 'root',
        'password': 'Helloworld@2025',
        'host': 'localhost',
        'database': db_name,
        'raise_on_warnings': True
    }
    
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # Insertion for basic_info table.
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
        insert_data(cursor, "basic_info", "basic_info.csv", basic_info_columns)
        
        # Insertion for orbital_info table.
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
        insert_data(cursor, "orbital_info", "orbital_info.csv", orbital_info_columns)
        
        # Insertion for launch_info table.
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
        # Assume "Date of Launch" is stored as Unix epoch (milliseconds).
        launch_date_cols = ["Date of Launch"]
        insert_data(cursor, "launch_info", "launch_info.csv", launch_info_columns, date_cols=launch_date_cols)
        
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Data insertion complete. All data inserted successfully into the ISRO satellites tables.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
