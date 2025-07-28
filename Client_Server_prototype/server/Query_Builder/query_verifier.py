import mysql.connector
from mysql.connector import Error

def verify_query(sql, host, user, password, database=None):
    """
    Enhanced query verifier with support for destructive operations
    """
    conn = None
    try:
        conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        cur = conn.cursor()
        
        # Check if it's a destructive operation
        sql_upper = sql.upper().strip()
        is_destructive = any(sql_upper.startswith(op) for op in 
                           ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE'])
        
        if is_destructive:
            # For destructive operations, we want to execute and return affected rows count
            cur.execute(sql)
            affected_rows = cur.rowcount
            conn.commit()  # Commit the transaction for destructive operations
            
            # Return success with affected rows count
            return True, f"Operation completed successfully. Affected rows: {affected_rows}"
        else:
            # For SELECT operations, return the actual data
            cur.execute(sql)
            rows = cur.fetchall()
            return True, rows
            
    except Error as e:
        # Rollback any pending transaction on error
        if conn and conn.is_connected():
            conn.rollback()
        return False, str(e)
    finally:
        if 'cur' in locals():
            cur.close()
        if conn and conn.is_connected():
            conn.close()

def verify_query_safe_mode(sql, host, user, password, database=None):
    """
    Safe mode query verifier - only allows SELECT operations
    """
    sql_upper = sql.upper().strip()
    
    # Block all destructive operations in safe mode
    destructive_ops = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE']
    if any(sql_upper.startswith(op) for op in destructive_ops):
        return False, "Safe mode: Destructive operations are not allowed"
    
    # Use regular verifier for SELECT operations
    return verify_query(sql, host, user, password, database)
