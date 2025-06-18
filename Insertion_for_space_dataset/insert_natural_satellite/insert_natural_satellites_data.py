import mysql.connector
import pandas as pd

def insert_data(cursor, table_name, csv_file, columns, batch_size=500):
    placeholders = ", ".join(["%s"] * len(columns))
    cols = ", ".join(f"`{col}`" for col in columns)
    insert_sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
    df = pd.read_csv(csv_file, dtype=str)
    df = df.replace(r'^\s*nan\s*$', None, regex=True)
    df = df.where(pd.notnull(df), None)
    data = list(df[columns].itertuples(index=False, name=None))
    for i in range(0, len(data), batch_size):
        chunk = data[i:i + batch_size]
        cursor.executemany(insert_sql, chunk)
    print(f"Inserted {len(data)} rows into table {table_name} from {csv_file}.")

def main():
    db_name = 'natural_satellites_db'
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
        identity_columns = ["planet", "name"]
        insert_data(cursor, "satellite_identity", "satellite_identity.csv", identity_columns)
        physical_columns = ["planet", "name", "gm", "radius", "density", "magnitude", "albedo"]
        insert_data(cursor, "satellite_physical", "satellite_physical.csv", physical_columns)
        
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Data insertion complete for natural_satellites_db.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
