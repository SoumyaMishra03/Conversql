import mysql.connector
import csv

def insert_data_from_csv():
    db_name = 'products_db'
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

        with open('products_table.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            products_data = [
                (
                    row['Uniq Id'],
                    row['Category'],
                    row['Product Title'],
                    row['Product Description'],
                    row['Brand'],
                    row['Pack Size Or Quantity'],
                    row['Image Urls']
                ) for row in reader
            ]
        cursor.executemany(
            "INSERT INTO products (UniqId, Category, ProductTitle, ProductDescription, Brand, PackSizeOrQuantity, ImageUrls) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            products_data
        )
        print(f"Inserted {cursor.rowcount} rows into 'products'.")

        with open('pricing_table.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            pricing_data = [
                (
                    row['Uniq Id'],
                    row['Mrp'],
                    row['Price'],
                    row['Offers'],
                    row['Combo Offers']
                ) for row in reader
            ]
        cursor.executemany(
            "INSERT INTO pricing (UniqId, Mrp, Price, Offers, ComboOffers) "
            "VALUES (%s, %s, %s, %s, %s)",
            pricing_data
        )
        print(f"Inserted {cursor.rowcount} rows into 'pricing'.")

        with open('availability_table.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            availability_data = [
                (
                    row['Uniq Id'],
                    row['Site Name'],
                    row['Stock Availibility'],
                    row['Product Asin']
                ) for row in reader
            ]
        cursor.executemany(
            "INSERT INTO availability (UniqId, SiteName, StockAvailibility, ProductAsin) "
            "VALUES (%s, %s, %s, %s)",
            availability_data
        )
        print(f"Inserted {cursor.rowcount} rows into 'availability'.")

        cnx.commit()
        cursor.close()
        cnx.close()
        print("CSV data inserted successfully into products_db.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

if __name__ == "__main__":
    insert_data_from_csv()
