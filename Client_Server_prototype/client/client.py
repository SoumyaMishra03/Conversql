import requests
from getpass import getpass
import json

SERVER_IP = "10.2.80.64"
SERVER_PORT = 8000
SERVER = f"http://{SERVER_IP}:{SERVER_PORT}"

class Session:
    def __init__(self):
        self.username = None
        self.password = None
        self.role = None

def login():
    username = input("Username: ")
    password = getpass("Password: ")
    res = requests.post(f"{SERVER}/login", json={"username": username, "password": password})
    if res.status_code == 200:
        role = res.json()["role"]
        print(f"Welcome, {username}! Role: {role}")
        session = Session()
        session.username = username
        session.password = password
        session.role = role
        return session
    else:
        print(res.json()["detail"])
        return None

def logout(session):
    res = requests.post(f"{SERVER}/logout", json={"username": session.username, "password": session.password})
    if res.status_code == 200:
        print("Logged out successfully.")
    else:
        print(res.text)

def run_query(session):
    q = input("Enter your query (NL or SQL): ")
    data = {"username": session.username, "password": session.password, "query": q}
    res = requests.post(f"{SERVER}/query", json=data)
    try:
        print(json.dumps(res.json(), indent=2))
    except:
        print(res.text)

def view_logs(session):
    res = requests.get(f"{SERVER}/logs/access", params={"admin_user": session.username, "admin_pass": session.password})
    print(json.dumps(res.json(), indent=2))

def lock_user(session):
    target = input("Username to lock: ")
    duration = int(input("Duration in minutes: "))
    data = {
        "admin_user": session.username,
        "admin_pass": session.password,
        "target_user": target,
        "duration_minutes": duration
    }
    res = requests.post(f"{SERVER}/admin/lock", json=data)
    print(res.json())

def send_message(session):
    msg = input("Message to admin: ")
    data = {"username": session.username, "password": session.password, "message": msg}
    res = requests.post(f"{SERVER}/message", json=data)
    print(res.json())

def admin_send_message(session):
    to_user = input("Send message to user: ")
    msg = input("Message: ")
    data = {
        "admin_user": session.username,
        "admin_pass": session.password,
        "target_user": to_user,
        "message": msg
    }
    res = requests.post(f"{SERVER}/admin/message", json=data)
    print(res.json())

def user_inbox(session):
    res = requests.get(f"{SERVER}/messages", params={"username": session.username, "password": session.password})
    print(json.dumps(res.json(), indent=2))

def view_all_messages(session):
    res = requests.get(f"{SERVER}/admin/messages", params={"admin_user": session.username, "admin_pass": session.password})
    print(json.dumps(res.json(), indent=2))

def add_user(session):
    uname = input("New username: ")
    role = input("Role: ")
    pos = input("Position: ")
    data = {
        "admin_user": session.username,
        "admin_pass": session.password,
        "target_user": uname,
        "role": role,
        "position": pos
    }
    res = requests.post(f"{SERVER}/admin/add_user", json=data)
    print(res.json())

def main():
    session = None
    while not session:
        session = login()
    while True:
        print("\nSelect an action:")
        print("1) Query")
        print("2) Send Message to Admin")
        print("3) View My Inbox")
        print("4) Logout & Switch User")
        print("5) Exit")
        if session.role == "admin":
            print("6) View Access Logs")
            print("7) Lock a User")
            print("8) Send Message to User")
            print("9) View All Messages")
            print("10) Add New User")
        choice = input("> ")
        if choice == "1":
            run_query(session)
        elif choice == "2":
            send_message(session)
        elif choice == "3":
            user_inbox(session)
        elif choice == "4":
            logout(session)
            session = None
            while not session:
                session = login()
        elif choice == "5":
            logout(session)
            break
        elif choice == "6" and session.role == "admin":
            view_logs(session)
        elif choice == "7" and session.role == "admin":
            lock_user(session)
        elif choice == "8" and session.role == "admin":
            admin_send_message(session)
        elif choice == "9" and session.role == "admin":
            view_all_messages(session)
        elif choice == "10" and session.role == "admin":
            add_user(session)
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
