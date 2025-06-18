import mysql.connector
import csv
import time

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'spacenews_db'
}

CHUNK_SIZE = 500  

def insert_in_chunks(cursor, query, data, label):
    total = len(data)
    print(f"Inserting {total} rows into {label}...")
    for i in range(0, total, CHUNK_SIZE):
        chunk = data[i:i + CHUNK_SIZE]
        try:
            cursor.executemany(query, chunk)
            print(f"  → Inserted {i + len(chunk)} / {total}")
        except mysql.connector.Error as e:
            print(f" Failed to insert chunk starting at row {i}: {e}")
            time.sleep(1)

def insert_news_articles(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [
            (
                row['title'],
                row['url'],
                row['content'],
                row['postexcerpt']
            ) for row in reader
        ]
    query = """
        INSERT INTO news_articles_table (title, url, content, postexcerpt)
        VALUES (%s, %s, %s, %s)
    """
    insert_in_chunks(cursor, query, data, "news_articles_table")

def insert_publishing_info(cursor, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [
            (
                row['title'],
                row['author'],
                row['date']
            ) for row in reader
        ]
    query = """
        INSERT INTO publishing_info (title, author, date)
        VALUES (%s, %s, %s)
    """
    insert_in_chunks(cursor, query, data, "publishing_info")

def main():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        insert_news_articles(cursor, 'news_articles_table.csv')
        insert_publishing_info(cursor, 'publishing_info.csv')

        conn.commit()
        print(" All data inserted successfully.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
