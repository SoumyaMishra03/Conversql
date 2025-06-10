import mysql.connector
import csv

def insert_from_csv():
    db_name = 'hospital_db'
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

        with open('patients.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            patient_data = [
                (row['Patient_ID'], int(row['Age']), row['Gender'])
                for row in reader
            ]

        patient_query = (
            "INSERT INTO patients (Patient_ID, Age, Gender) "
            "VALUES (%s, %s, %s)"
        )
        cursor.executemany(patient_query, patient_data)
        print(f"Inserted {cursor.rowcount} rows into 'patients' table.")
        with open('hospital_encounters.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            encounter_data = [
                (
                    row['Patient_ID'],
                    row['Condition'],
                    row['Procedure'],
                    float(row['Cost']),
                    int(row['Length_of_Stay']),
                    row['Readmission'],
                    row['Outcome'],
                    row['Satisfaction']
                )
                for row in reader
            ]

        encounter_query = (
            "INSERT INTO hospital_encounters "
            "(Patient_ID, `Condition`, `Procedure`, Cost, Length_of_Stay, Readmission, Outcome, Satisfaction) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cursor.executemany(encounter_query, encounter_data)
        print(f"Inserted {cursor.rowcount} rows into 'hospital_encounters' table.")

        cnx.commit()
        cursor.close()
        cnx.close()
        print("CSV data inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    insert_from_csv()
