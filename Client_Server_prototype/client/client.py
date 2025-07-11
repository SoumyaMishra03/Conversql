import sys
import requests
import getpass

SERVER_IP   = "10.2.80.64"
SERVER_PORT = 8000
BASE_URL    = f"http://{SERVER_IP}:{SERVER_PORT}"

def login():
    while True:
        user = input("Username: ").strip()
        pwd  = getpass.getpass("Password: ").strip()
        r = requests.post(
            f"{BASE_URL}/login",
            json={"username": user, "password": pwd},
            timeout=5
        )
        if r.status_code == 200:
            role = r.json().get("role", "").lower()
            print(f"\nWelcome, {user}! Role: {role}\n")
            return user, pwd, role
        else:
            print("Login failed:", r.text)

def show_menu(role: str):
    print("Select an action:")
    print(" 1) Enter a natural-language query")
    print(" 2) Switch user")
    print(" 3) Exit")
    if role == "admin":
        print(" 4) Show recent access logs")
        print(" 5) Lock out a user")

def do_query(user: str, pwd: str):
    q = input("\nEnter your query (or 'back' to menu): ").strip()
    if not q or q.lower() == "back":
        return
    r = requests.post(
        f"{BASE_URL}/query",
        json={"username": user, "password": pwd, "query": q},
        timeout=10
    )
    if r.status_code == 200:
        payload = r.json()
        rows = payload.get("data", payload.get("sample_rows", []))
        if not rows:
            print("\n[ No results returned ]")
        else:
            print("\nResults:")
            for row in rows:
                print(row)
    else:
        print(f"\nQuery failed ({r.status_code}): {r.text}")

def view_logs(user: str, pwd: str):
    r = requests.get(
        f"{BASE_URL}/logs/access",
        params={"admin_user": user, "admin_pass": pwd},
        timeout=5
    )
    if r.status_code == 200:
        print("\nAccess Logs (id | user | time | query):")
        for rec in r.json().get("logs", []):
            print(" | ".join(str(x) for x in rec))
    else:
        print(f"\nLogs error ({r.status_code}): {r.text}")

def lock_user(user: str, pwd: str):
    tgt  = input("Username to lock out: ").strip()
    mins = input("Duration (minutes): ").strip()
    try:
        m = int(mins)
    except ValueError:
        print("Invalid number.")
        return
    r = requests.post(
        f"{BASE_URL}/admin/lock",
        json={
            "admin_user": user,
            "admin_pass": pwd,
            "target_user": tgt,
            "duration_minutes": m
        },
        timeout=5
    )
    if r.status_code == 200:
        info = r.json()
        print(f"\nLocked '{info.get('locked_user','?')}' until {info.get('until','?')}")
    else:
        print(f"\nLock error ({r.status_code}): {r.text}")

def main():
    while True:
        user, pwd, role = login()
        while True:
            show_menu(role)
            choice = input("> ").strip()
            if choice == "1":
                do_query(user, pwd)
            elif choice == "2":
                break
            elif choice == "3":
                sys.exit(0)
            elif choice == "4" and role == "admin":
                view_logs(user, pwd)
            elif choice == "5" and role == "admin":
                lock_user(user, pwd)
            else:
                print("Invalid choice.\n")

if __name__ == "__main__":
    main()
