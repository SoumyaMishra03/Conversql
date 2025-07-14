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

def validate_query_access(user_role: str, db_name: str) -> bool:
    db_name=db_name.lower()
    allowed = ROLE_DATABASE_ACCESS.get(user_role)
    if not allowed:
        return False
    return "*" in allowed or db_name in allowed

def explain_denial(user_role: str, db_name: str) -> str:
    db_name=db_name.lower()
    if user_role not in ROLE_DATABASE_ACCESS:
        return f"Unknown role: '{user_role}'. No database access granted."
    allowed = ROLE_DATABASE_ACCESS[user_role]
    if "*" in allowed or db_name in allowed:
        return f"Access granted for '{user_role}' role on '{db_name}'."
    else:
        return f"Access denied: '{user_role}' role cannot access '{db_name}'. Allowed: {sorted(allowed)}"
