import mysql.connector
import pandas as pd

def convert_date_columns(df, date_columns):
    for col in date_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col].astype(float) / 1000, unit='s', errors='coerce').dt.strftime('%Y-%m-%d')
            except Exception:
                df[col] = None
    return df

def insert_data(cursor, table_name, csv_file, columns, date_cols=None, batch_size=500):
    placeholders = ", ".join(["%s"] * len(columns))
    cols = ", ".join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
    df = pd.read_csv(csv_file, dtype=str)
    if date_cols is not None:
        df = convert_date_columns(df, date_cols)
    df = df.replace(r'^\s*nan\s*$', None, regex=True)
    df = df.where(pd.notnull(df), None)
    data = list(df[columns].itertuples(index=False, name=None))
    for i in range(0, len(data), batch_size):
        chunk = data[i:i + batch_size]
        cursor.executemany(insert_sql, chunk)
    print(f"Inserted {len(data)} rows into table {table_name} from {csv_file}.")

def main():
    db_name = 'isro_satellites_db'
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'database': db_name,
        'raise_on_warnings': True
    }
    
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
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
