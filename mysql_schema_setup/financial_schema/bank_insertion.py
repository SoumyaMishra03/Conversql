import mysql.connector
import csv

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'financial_transaction'
}

def insert_customers(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        seen_ids = set()
        for row in reader:
            try:
                cust_id = row['CustomerID']
                if cust_id in seen_ids:
                    continue  
                seen_ids.add(cust_id)

                account_balance = float(row['CustAccountBalance']) if row['CustAccountBalance'] else 0.0
                values = (
                    cust_id,
                    row['CustomerDOB'],
                    row['CustGender'],
                    row['CustLocation'],
                    account_balance
                )
                data.append(values)
            except (ValueError, KeyError) as e:
                print(f"Skipping customer row due to error: {e} -> {row}")

    query = """
        INSERT IGNORE INTO customers (
            CustomerID, CustomerDOB, CustGender, 
            CustLocation, CustAccountBalance
        ) VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} unique customers.")
    except mysql.connector.Error as e:
        print(f"Error inserting customers: {e}")

def insert_transactions(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            try:
                txn_amount = float(row['TransactionAmount (INR)']) if row['TransactionAmount (INR)'] else 0.0
                values = (
                    row['TransactionID'],
                    row['CustomerID'],
                    row['TransactionDate'],
                    row['TransactionTime'],
                    txn_amount
                )
                data.append(values)
            except (ValueError, KeyError) as e:
                print(f"Skipping transaction row due to error: {e} -> {row}")

    query = """
        INSERT INTO transactions (
            TransactionID, CustomerID, 
            TransactionDate, TransactionTime, TransactionAmount_INR
        ) VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, data)
        print(f"Inserted {len(data)} transactions.")
    except mysql.connector.Error as e:
        print(f"Error inserting transactions: {e}")

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
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
