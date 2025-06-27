import subprocess
import os

MAIN_PATH = os.path.abspath(r"C:\Users\hbhan\OneDrive\Desktop\programming\internship\Talk2DB\backend") 

NORMALIZATION_DIR = os.path.join(MAIN_PATH, "normalization_to_tables")
TABLE_SPLIT_DIR = os.path.join(MAIN_PATH, "mysql_schema_setup_for_space_dataset")
INSERTION_DIR = os.path.join(MAIN_PATH, "insertion_for_space_dataset")


csv_file_normalization_scripts = [
    "normalization_asteroids.py",
    "normalization_astronauts.py",
    "normalization_ISRO.py",
    "normalization_natural.py",
    "normalization_rockets.py",
    "normalization_space_missions.py",
    "normalization_space_news.py"
]


db_setup_scripts = [
    "split_asteroids_tables.py",
    "split_astronauts_tables.py",
    "split_isro_satellites_tables.py",
    "split_natural_satellites_tables.py",
    "split_rockets_tables.py",
    "split_space_missions_tables.py",
    "split_space_news.py",
    "split_stars_tables.py"
]


db_insert_scripts = [
    "insert_asteroids/insert_asteroids_data.py",
    "insert_astornauts/insert_astronauts_data.py",
    "insert_isro_satellite/insert_isro_satellites_data.py",
    "insert_natural_satellite/insert_natural_satellites_data.py",
    "insert_rockets/insert_rockets_data.py",
    "insert_space_missions/insert_space_missions.py",
    "insert_space_news/insert_spacenews.py",
    "insert_stars/stars_insertion.py"
]

def run_scripts(script_list, folder):
    for script in script_list:
        full_path = os.path.join(folder, script)
        print(f" Running: {full_path}")
        result = subprocess.run(["python", full_path])
        if result.returncode != 0:
            print(f"Error running {script}")
        else:
            print(f" Completed: {script}")

def main():
    print("=== Running Table Creation Scripts ===")
    run_scripts(db_setup_scripts, TABLE_SPLIT_DIR)

    print("\n=== Running Data Insertion Scripts ===")
    run_scripts(db_insert_scripts, INSERTION_DIR)


    print("\n All setup and insertions completed.")

if __name__ == "__main__":
    main()
