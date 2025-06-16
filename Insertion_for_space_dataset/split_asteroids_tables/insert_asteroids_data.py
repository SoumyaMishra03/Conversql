import mysql.connector
import pandas as pd

def convert_date_columns(df, date_columns):
    for col in date_columns:
        if col in df.columns:
            # Convert assuming the column values represent Unix timestamps in milliseconds.
            df[col] = pd.to_datetime(df[col], unit='ms', errors='coerce').dt.strftime('%Y-%m-%d')
    return df

def insert_data(cursor, table_name, csv_file, columns, date_cols=None, batch_size=500):
    placeholders = ", ".join(["%s"] * len(columns))
    cols = ", ".join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
    
    # Read CSV as DataFrame
    df = pd.read_csv(csv_file)
    
    # If there are date columns to convert, do that
    if date_cols is not None:
        df = convert_date_columns(df, date_cols)
    
    # Convert any NaN values to None so that they insert as SQL NULL
    df = df.where(pd.notnull(df), None)
    
    # Convert DataFrame to list of tuples based on the specified columns
    data = list(df[columns].itertuples(index=False, name=None))
    
    for i in range(0, len(data), batch_size):
        chunk = data[i:i+batch_size]
        cursor.executemany(insert_sql, chunk)
    print(f"Inserted {len(data)} rows into table {table_name} from {csv_file}.")

def main():
    db_name = 'asteroids'
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

        neo_reference_columns = [
            "Neo Reference ID", "Name", "Absolute Magnitude",
            "Est Dia in KM(min)", "Est Dia in KM(max)",
            "Est Dia in M(min)", "Est Dia in M(max)",
            "Est Dia in Miles(min)", "Est Dia in Miles(max)",
            "Est Dia in Feet(min)", "Est Dia in Feet(max)"
        ]
        insert_data(cursor, "neo_reference", "neo_reference.csv", neo_reference_columns)

        close_approach_columns = [
            "Neo Reference ID", "Close Approach Date", "Epoch Date Close Approach",
            "Relative Velocity km per sec", "Relative Velocity km per hr",
            "Miles per hour", "Miss Dist.(Astronomical)", "Miss Dist.(lunar)",
            "Miss Dist.(kilometers)", "Miss Dist.(miles)"
        ]
        close_approach_date_cols = ["Close Approach Date", "Epoch Date Close Approach"]
        insert_data(cursor, "close_approach", "close_approach.csv", close_approach_columns, date_cols=close_approach_date_cols)

        orbit_data_columns = [
            "Neo Reference ID", "Orbiting Body", "Orbit ID",
            "Orbit Determination Date", "Orbit Uncertainity", "Minimum Orbit Intersection",
            "Jupiter Tisserand Invariant", "Epoch Osculation", "Eccentricity",
            "Semi Major Axis", "Inclination", "Asc Node Longitude", "Orbital Period",
            "Perihelion Distance", "Perihelion Arg", "Aphelion Dist",
            "Perihelion Time", "Mean Anomaly", "Mean Motion", "Equinox", "Hazardous"
        ]
        orbit_date_cols = ["Orbit Determination Date", "Epoch Osculation"]
        insert_data(cursor, "orbit_data", "orbit_data.csv", orbit_data_columns, date_cols=orbit_date_cols)

        cnx.commit()
        cursor.close()
        cnx.close()
        print("Data insertion complete. All data inserted successfully into the asteroids tables.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
