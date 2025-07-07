import mysql.connector

def get_full_schema_map(host, user, password):
    conn = mysql.connector.connect(host=host, user=user, password=password)
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

def build_query(intent, schema_entities, operators, values, db_host='localhost', db_user='root', db_pass='Helloworld@2025'):
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

    # fallback 1: only database detected
    if database and not table:
        return f"SHOW TABLES FROM `{database}`;"
    # fallback 2: nothing detected, show all dbs
    if database is None and table is None and not columns:
        return "SHOW DATABASES;"

    if database and table:
        full_table = f"`{database}`.`{table}`"
    else:
        return "ERROR: Could not resolve table."

    # build SELECT clause
    select_clause = "*"
    if "COUNT_ROWS" in intent:
        select_clause = "COUNT(*)"
    elif "AGGREGATE_AVG" in intent:
        select_clause = f"AVG(`{columns[0]}`)" if columns else "AVG(`id`)"
    elif "AGGREGATE_SUM" in intent:
        select_clause = f"SUM(`{columns[0]}`)" if columns else "SUM(`id`)"
    elif "AGGREGATE_MINMAX" in intent:
        select_clause = f"MAX(`{columns[0]}`)" if columns else "MAX(`id`)"

    # build WHERE clause
    where_clauses = []
    for i, ((raw, op), val) in enumerate(zip(operators, values)):
        nearest_col = columns[-1] if columns else 'id'
        if len(columns) > 1 and val.get('span'):
            v_pos = val['span'][0]
            col_dist = [(abs(v_pos - schema_entities[j]['matched_token_span'][0]), c)
                        for j, c in enumerate(columns) if 'matched_token_span' in schema_entities[j]]
            if col_dist:
                nearest_col = min(col_dist)[1]
        elif i < len(columns):
            nearest_col = columns[i]

        if val["type"] in ("STRING", "DATE"):
            clause = f"`{nearest_col}` {op} '{val['value']}'"
        else:
            clause = f"`{nearest_col}` {op} {val['value']}"
        where_clauses.append(clause)

    where = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"SELECT {select_clause} FROM {full_table}{where};"
    return query
