ROLE_DATABASE_ACCESS = {
    "science": {"stars_db", "natural_satellites_db"},
    "missions": {"space_missions_db", "rockets_db", "astronauts_db"},
    "news": {"spacenews_db"},
    "isro": {"isro_satellites_db"},
    "asteroid": {"asteroids_db"},
    "admin": {"*"}
}

ALL_DATABASES = {
    'asteroids_db', 'astronauts_db', 'isro_satellites_db',
    'natural_satellites_db', 'rockets_db', 'space_missions_db',
    'spacenews_db', 'stars_db'
}

def validate_query_access(user_role: str, db_name: str, intent=None) -> bool:
    """
    Enhanced RBAC with intent-based access control
    Admin users can perform all operations
    Regular users can only perform SELECT operations
    """
    if user_role == "admin":
        return True
    
    # Check if the operation is destructive
    if intent:
        destructive_intents = [
            "INSERT_ROWS", "UPDATE_ROWS", "DELETE_ROWS", 
            "DROP_TABLE", "DROP_DATABASE", "TRUNCATE_TABLE"
        ]
        
        if any(destructive_intent in intent for destructive_intent in destructive_intents):
            return False
    
    # Regular users can access their allowed databases for SELECT operations only
    db_name = db_name.lower()
    allowed = ROLE_DATABASE_ACCESS.get(user_role)
    if not allowed:
        return False
    return "*" in allowed or db_name in allowed

def explain_denial(user_role: str, db_name: str, intent=None) -> str:
    """
    Enhanced denial explanation with intent-based messaging
    """
    if user_role != "admin" and intent:
        destructive_intents = [
            "INSERT_ROWS", "UPDATE_ROWS", "DELETE_ROWS", 
            "DROP_TABLE", "DROP_DATABASE", "TRUNCATE_TABLE"
        ]
        
        if any(destructive_intent in intent for destructive_intent in destructive_intents):
            return f"Access denied: Only administrators can perform INSERT, UPDATE, DELETE, or DROP operations. Your role: {user_role}"
    
    db_name = db_name.lower()
    if user_role not in ROLE_DATABASE_ACCESS:
        return f"Unknown role: '{user_role}'. No database access granted."
    allowed = ROLE_DATABASE_ACCESS[user_role]
    if "*" in allowed or db_name in allowed:
        return f"Access granted for '{user_role}' role on '{db_name}'."
    else:
        return f"Access denied: '{user_role}' role cannot access '{db_name}'. Allowed: {sorted(allowed)}"

def get_allowed_operations(user_role):
    """
    Get list of allowed operations for a user role
    """
    if user_role == "admin":
        return [
            "SELECT", "INSERT", "UPDATE", "DELETE", 
            "DROP TABLE", "DROP DATABASE", "TRUNCATE", 
            "CREATE", "ALTER"
        ]
    else:
        return ["SELECT"]

def is_admin_only_operation(intent):
    """
    Check if the operation requires admin privileges
    """
    admin_only_intents = [
        "INSERT_ROWS", "UPDATE_ROWS", "DELETE_ROWS", 
        "DROP_TABLE", "DROP_DATABASE", "TRUNCATE_TABLE"
    ]
    
    return any(admin_intent in intent for admin_intent in admin_only_intents)
