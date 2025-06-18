import mysql.connector

def create_database(cursor, db_name):
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created (or already exists).")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    TABLES = {}

    TABLES['personal_info'] = (
        "CREATE TABLE IF NOT EXISTS personal_info ("
        "  `id` VARCHAR(10),"
        "  `number` VARCHAR(10),"
        "  `nationwide_number` VARCHAR(20),"
        "  `name` VARCHAR(100),"
        "  `original_name` VARCHAR(100),"
        "  `sex` VARCHAR(10),"
        "  `year_of_birth` INT,"
        "  `nationality` VARCHAR(50),"
        "  `military_civilian` VARCHAR(20)"
        ")"
    )

    TABLES['mission_info'] = (
        "CREATE TABLE IF NOT EXISTS mission_info ("
        "  `id` VARCHAR(10),"
        "  `selection` VARCHAR(100),"
        "  `year_of_selection` INT,"
        "  `mission_number` INT,"
        "  `total_number_of_missions` INT,"
        "  `occupation` VARCHAR(100),"
        "  `year_of_mission` INT,"
        "  `mission_title` VARCHAR(200)"
        ")"
    )

    TABLES['mission_performance'] = (
        "CREATE TABLE IF NOT EXISTS mission_performance ("
        "  `id` VARCHAR(10),"
        "  `ascend_shuttle` VARCHAR(50),"
        "  `in_orbit` VARCHAR(50),"
        "  `descend_shuttle` VARCHAR(50),"
        "  `hours_mission` FLOAT,"
        "  `total_hrs_sum` FLOAT,"
        "  `field21` VARCHAR(50),"
        "  `eva_hrs_mission` FLOAT,"
        "  `total_eva_hrs` FLOAT"
        ")"
    )

    for table_name, ddl in TABLES.items():
        try:
            print(f"Creating table {table_name}: ", end="")
            cursor.execute(ddl)
            print("OK")
        except mysql.connector.Error as err:
            print(f"Error creating table {table_name}: {err.msg}")

def main():
    db_name = 'astronauts_db'
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'raise_on_warnings': True
    }

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        create_database(cursor, db_name)
        cursor.execute(f"USE {db_name}")
        create_tables(cursor)
        cnx.commit()
        cursor.close()
        cnx.close()
        print("All tables created successfully in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    main()
