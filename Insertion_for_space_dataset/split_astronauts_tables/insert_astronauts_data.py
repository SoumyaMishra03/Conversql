import mysql.connector
import pandas as pd

def insert_data(cursor, table_name, csv_file, columns, batch_size=500):
    """Bulk-insert data from a CSV into a specified table using the given columns."""
    placeholders = ", ".join(["%s"] * len(columns))
    cols = ", ".join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"

    # Load data into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Replace NaN with None to enable proper insertion of SQL NULL values
    df = df.where(pd.notnull(df), None)
    
    # Convert DataFrame rows corresponding to the specified columns into a list of tuples
    data = list(df[columns].itertuples(index=False, name=None))
    
    # Insert in chunks for faster performance with large datasets
    for i in range(0, len(data), batch_size):
        chunk = data[i:i+batch_size]
        cursor.executemany(insert_sql, chunk)
    print(f"Inserted {len(data)} rows into table {table_name} from {csv_file}.")

def main():
    db_name = 'astronauts_db'
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
        
        # Define the columns for each table based on the CSV structure
        personal_info_columns = [
            "id", "number", "nationwide_number", "name", "original_name",
            "sex", "year_of_birth", "nationality", "military_civilian"
        ]
        mission_info_columns = [
            "id", "selection", "year_of_selection", "mission_number",
            "total_number_of_missions", "occupation", "year_of_mission", "mission_title"
        ]
        mission_performance_columns = [
            "id", "ascend_shuttle", "in_orbit", "descend_shuttle",
            "hours_mission", "total_hrs_sum", "field21", "eva_hrs_mission", "total_eva_hrs"
        ]
        
        # Insert data into each table from corresponding CSV files
        insert_data(cursor, "personal_info", "personal_info.csv", personal_info_columns)
        insert_data(cursor, "mission_info", "mission_info.csv", mission_info_columns)
        insert_data(cursor, "mission_performance", "mission_performance.csv", mission_performance_columns)

        # Commit all insertions at once to speed up the process
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Data insertion complete. All data inserted successfully into the astronauts tables.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
