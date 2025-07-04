import mysql.connector

def get_full_schema_map(host, user, password):
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES;")
    databases = [row[0] for row in cursor.fetchall()]
    full_map = {}
    for db in databases:
        try:
            cursor.execute(f"USE `{db}`;")
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                cursor.execute(f"DESCRIBE `{table}`;")
                columns = [row[0] for row in cursor.fetchall()]
                full_map.setdefault(db, {})[table] = columns
        except mysql.connector.Error:
            continue
    cursor.close()
    conn.close()
    return full_map

def build_query(intent, schema_entities, operators, values,
                db_host='localhost', db_user='root', db_pass='root'):

    database = None
    table = None
    columns = []
    table_to_db = {}
    column_to_table_db = {}

    full_map = get_full_schema_map(db_host, db_user, db_pass)
    for db, tables in full_map.items():
        for t, cols in tables.items():
            table_to_db[t] = db
            for c in cols:
                norm_c = c.lower().replace(' ', '')
                column_to_table_db[norm_c] = (db, t)

    for e in schema_entities:
        if e['type'] == 'database' and database is None:
            database = e['value']
        elif e['type'] == 'table' and table is None:
            table = e['value']
        elif e['type'] == 'column':
            columns.append(e['value'])

    if table and not database:
        database = table_to_db.get(table)

    if database is None and table is None and columns:
        for col in columns:
            norm_col = col.lower().replace(' ', '')
            if norm_col in column_to_table_db:
                database, table = column_to_table_db[norm_col]
                break

    if database and table:
        full_table = f"`{database}`.`{table}`"
    else:
        return "ERROR: Could not resolve table."

    select_clause = "*"
    if intent == "COUNT_ROWS":
        select_clause = "COUNT(*)"
    elif intent == "AGGREGATE_AVG":
        select_clause = f"AVG(`{columns[0]}`)" if columns else "AVG(`id`)"
    elif intent == "AGGREGATE_SUM":
        select_clause = f"SUM(`{columns[0]}`)" if columns else "SUM(`id`)"
    elif intent == "AGGREGATE_MINMAX":
        select_clause = f"MAX(`{columns[0]}`)" if columns else "MAX(`id`)"

    where_clauses = []
    for i, ((raw, op), val) in enumerate(zip(operators, values)):
        col = columns[i] if i < len(columns) else (columns[-1] if columns else 'id')
        if val["type"] in ("STRING", "DATE"):
            clause = f"`{col}` {op} '{val['value']}'"
        else:
            clause = f"`{col}` {op} {val['value']}"
        where_clauses.append(clause)

    where = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"SELECT {select_clause} FROM {full_table}{where};"
    return query
