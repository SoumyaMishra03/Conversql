import mysql.connector
import pandas as pd

def convert_date_columns(df, date_columns):
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], unit='ms', errors='coerce').dt.strftime('%Y-%m-%d')
    return df

def insert_data(cursor, table_name, csv_file, columns, date_cols=None, batch_size=500, drop_duplicates_by=None):
    placeholders = ", ".join(["%s"] * len(columns))
    cols = ", ".join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
    
    df = pd.read_csv(csv_file)

    if date_cols is not None:
        df = convert_date_columns(df, date_cols)

    if drop_duplicates_by is not None:
        df = df.drop_duplicates(subset=drop_duplicates_by)

    df = df.where(pd.notnull(df), None)

    data = list(df[columns].itertuples(index=False, name=None))  

    for i in range(0, len(data), batch_size):
        chunk = data[i:i+batch_size]
        cursor.executemany(insert_sql, chunk)
    
    print(f"Inserted {len(data)} rows into table {table_name} from {csv_file}.")

def main():
    db_name = 'asteroids'
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

        neo_reference_columns = [
            "Neo Reference ID", "Name", "Absolute Magnitude",
            "Est Dia in KM(min)", "Est Dia in KM(max)",
            "Est Dia in M(min)", "Est Dia in M(max)",
            "Est Dia in Miles(min)", "Est Dia in Miles(max)",
            "Est Dia in Feet(min)", "Est Dia in Feet(max)"
        ]

        insert_data(
            cursor, 
            table_name="neo_reference", 
            csv_file="neo_reference.csv", 
            columns=neo_reference_columns, 
            drop_duplicates_by=["Neo Reference ID", "Name"]
        )

        close_approach_columns = [
            "Neo Reference ID", "Close Approach Date", "Epoch Date Close Approach",
            "Relative Velocity km per sec", "Relative Velocity km per hr",
            "Miles per hour", "Miss Dist.(Astronomical)", "Miss Dist.(lunar)",
            "Miss Dist.(kilometers)", "Miss Dist.(miles)"
        ]
        close_approach_date_cols = ["Close Approach Date", "Epoch Date Close Approach"]
        insert_data(
            cursor,
            table_name="close_approach",
            csv_file="close_approach.csv",
            columns=close_approach_columns,
            date_cols=close_approach_date_cols,
            drop_duplicates_by=["Neo Reference ID"]
        )

        orbit_data_columns = [
            "Neo Reference ID", "Orbiting Body", "Orbit ID",
            "Orbit Determination Date", "Orbit Uncertainity", "Minimum Orbit Intersection",
            "Jupiter Tisserand Invariant", "Epoch Osculation", "Eccentricity",
            "Semi Major Axis", "Inclination", "Asc Node Longitude", "Orbital Period",
            "Perihelion Distance", "Perihelion Arg", "Aphelion Dist",
            "Perihelion Time", "Mean Anomaly", "Mean Motion", "Equinox", "Hazardous"
        ]
        orbit_date_cols = ["Orbit Determination Date", "Epoch Osculation"]
        insert_data(
            cursor,
            table_name="orbit_data",
            csv_file="orbit_data.csv",
            columns=orbit_data_columns,
            date_cols=orbit_date_cols,
            drop_duplicates_by=["Neo Reference ID"]
        )

        cnx.commit()
        cursor.close()
        cnx.close()
        print(" Data insertion complete. All data inserted successfully into the asteroids tables.")
    
    except mysql.connector.Error as err:
        print(f" Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
