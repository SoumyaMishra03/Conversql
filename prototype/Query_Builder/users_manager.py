USERS = {
    "soumya": {"username": "soumya", "password": "nebula123", "role": "science"},
    "anita": {"username": "anita", "password": "headlines22", "role": "news"},
    "kabir": {"username": "kabir", "password": "rock3tmissions", "role": "missions"},
    "admin": {"username": "admin", "password": "rootaccess", "role": "admin"}
}

def get_user(username: str, password: str):
    user = USERS.get(username.lower())
    if user and user["password"] == password:
        return {"username": user["username"], "role": user["role"]}
    return None
