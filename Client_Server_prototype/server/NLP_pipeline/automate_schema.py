import mysql.connector
import json
import os

TARGET_DATABASES = [
    "asteroids_db",
    "astronauts_db",
    "isro_satellites_db",
    "natural_satellites_db",
    "rockets_db",
    "space_missions_db",
    "spacenews_db",
    "stars_db"
]

def generate_schema_json_from_selected_dbs(
    host="localhost",
    user="root",
    password="root",
    output_path="plugin_schema.json",
    individual_dir="db_schemas"
):
    # Create output directory for individual DB schemas
    os.makedirs(individual_dir, exist_ok=True)

    conn = mysql.connector.connect(host=host, user=user, password=password)
    cursor = conn.cursor()

    schema_json = {"databases": []}

    for db in TARGET_DATABASES:
        try:
            cursor.execute(f"USE `{db}`;")
            cursor.execute("SHOW TABLES;")
            tables = [tbl[0] for tbl in cursor.fetchall()]

            db_entry = {"name": db, "tables": []}

            for tbl in tables:
                cursor.execute(f"DESCRIBE `{tbl}`;")
                columns = [col[0] for col in cursor.fetchall()]

                db_entry["tables"].append({
                    "name": tbl,
                    "columns": columns
                })

            # Add to combined plugin_schema.json
            schema_json["databases"].append(db_entry)

            # Write individual db_name.json
            individual_path = os.path.join(individual_dir, f"{db}.json")
            with open(individual_path, "w") as f:
                json.dump(db_entry, f, indent=2)
            print(f"Saved: {individual_path}")

        except mysql.connector.Error as e:
            print(f"Skipping {db} due to error: {e}")
            continue

    cursor.close()
    conn.close()

    with open(output_path, "w") as f:
        json.dump(schema_json, f, indent=2)

    print(f"Combined schema saved to: {output_path}")

if __name__ == "__main__":
    generate_schema_json_from_selected_dbs()
