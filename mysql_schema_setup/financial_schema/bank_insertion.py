import mysql.connector
import csv

# DB Configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'financial_transaction'
}

# Insert into customers table
def insert_customers(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO customers (
                    CustomerID, CustomerDOB, CustGender, 
                    CustLocation, CustAccountBalance
                ) VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                row['CustomerID'],
                row['CustomerDOB'],
                row['CustGender'],
                row['CustLocation'],
                float(row['CustAccountBalance']) if row['CustAccountBalance'] else None
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted customer: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting customer {row['CustomerID']}: {e}")

def insert_transactions(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            query = """
                INSERT INTO transactions (
                    TransactionID, CustomerID, 
                    TransactionDate, TransactionTime, TransactionAmount_INR
                ) VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                row['TransactionID'],
                row['CustomerID'],
                row['TransactionDate'],
                row['TransactionTime'],
                row['TransactionAmount (INR)']
            )
            try:
                cursor.execute(query, values)
                print(f"Inserted transaction: {values}")
            except mysql.connector.Error as e:
                print(f"Error inserting transaction {row['TransactionID']}: {e}")

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        insert_customers(cursor, 'customers.csv')
        insert_transactions(cursor, 'transactions.csv')

        conn.commit()
        print("All data inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
