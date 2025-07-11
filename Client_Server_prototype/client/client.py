import sys
import requests
import getpass

SERVER = "10.2.80.64"
PORT   = 8000
BASE   = f"http://{SERVER}:{PORT}"

def login():
    while True:
        user = input("Username: ").strip()
        pwd  = getpass.getpass("Password: ").strip()
        try:
            r = requests.post(f"{BASE}/login",
                              json={"username": user, "password": pwd},
                              timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            continue
        if r.status_code == 200:
            role = r.json().get("role","").lower()
            print(f"\n✅ Logged in as {user} ({role})\n")
            return user, pwd, role
        if r.status_code == 401:
            print("Invalid username or password.")
        else:
            print(f"Login error ({r.status_code}): {r.text}")

def logout(user, pwd):
    r = requests.post(f"{BASE}/logout",
                      json={"username": user, "password": pwd},
                      timeout=5)
    if r.status_code == 200:
        print("\n🔒 Logged out.\n")
    else:
        print(f"Logout failed ({r.status_code}): {r.text}")

def show_menu(role):
    print("Select an action:")
    print(" 1) Query")
    print(" 2) Send Message")
    print(" 3) View Inbox")
    print(" 4) Logout & Switch User")
    print(" 5) Exit")
    if role == "admin":
        print(" 6) View Access Logs")
        print(" 7) Lock User")
        print(" 8) Add New User")

def do_query(user, pwd):
    q = input("\nNL query (or 'back'): ").strip()
    if not q or q.lower() == "back":
        return
    try:
        r = requests.post(f"{BASE}/query",
                          json={"username":user,"password":pwd,"query":q},
                          timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return
    if r.status_code == 200:
        rows = r.json().get("sample_rows", [])
        if not rows:
            print("\n[ No results ]")
        else:
            print("\nResults:")
            for row in rows:
                print(" ", row)
    else:
        print(f"Query failed ({r.status_code}): {r.text}")

def send_message(user, pwd, role):
    if role == "admin":
        to = input("\nSend to user: ").strip()
        url = f"{BASE}/admin/message"
        body = {"admin_user": user, "admin_pass": pwd, "target_user": to}
    else:
        url = f"{BASE}/message"
        body = {"username": user, "password": pwd}

    msg = input("Message (or 'back'): ").strip()
    if not msg or msg.lower() == "back":
        return
    body["message"] = msg

    try:
        r = requests.post(url, json=body, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return
    if r.status_code == 200:
        print("✉ Message sent.")
    else:
        print(f"Send failed ({r.status_code}): {r.text}")

def view_inbox(user, pwd, role):
    try:
        if role == "admin":
            r = requests.get(f"{BASE}/admin/messages",
                             params={"admin_user":user,"admin_pass":pwd}, timeout=5)
            header = "Inbox (user→admin):"
        else:
            r = requests.get(f"{BASE}/messages",
                             params={"username":user,"password":pwd}, timeout=5)
            header = "Inbox (admin→you):"
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return
    if r.status_code == 200:
        msgs = r.json().get("messages", [])
        if not msgs:
            print(f"\n[ No messages ]")
        else:
            print(f"\n{header}")
            for m in msgs:
                print(f"[{m['time']}] {m['from']}: {m['message']}")
    else:
        print(f"Inbox fetch failed ({r.status_code}): {r.text}")

def view_logs(user, pwd):
    try:
        r = requests.get(f"{BASE}/logs/access",
                         params={"admin_user":user,"admin_pass":pwd}, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return
    if r.status_code == 200:
        print("\nAccess Logs:")
        for rec in r.json().get("logs", []):
            print(" | ".join(str(x) for x in rec))
    else:
        print(f"Logs fetch failed ({r.status_code}): {r.text}")

def lock_user(user, pwd):
    tgt = input("\nUsername to lock out: ").strip()
    d   = input("Duration (minutes): ").strip()
    try:
        m = int(d)
    except:
        print("Invalid duration."); return
    try:
        r = requests.post(f"{BASE}/admin/lock",
                          json={"admin_user":user,"admin_pass":pwd,
                                "target_user":tgt,"duration_minutes":m}, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return
    if r.status_code == 200:
        info = r.json()
        print(f"🔒 Locked '{info['locked_user']}' until {info['until']}")
    else:
        print(f"Lock failed ({r.status_code}): {r.text}")

def add_user(user, pwd):
    new_u = input("\nNew username: ").strip()
    dept  = input("Department: ").strip()
    pos   = input("Position: ").strip()
    try:
        r = requests.post(f"{BASE}/admin/add_user",
                          json={"admin_user":user,"admin_pass":pwd,
                                "username":new_u,
                                "department":dept,
                                "position":pos}, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return
    if r.status_code == 200:
        out = r.json()
        print(f"👤 Created '{out['username']}', password: {out['password']}")
    else:
        print(f"Add-user failed ({r.status_code}): {r.text}")

def main():
    try:
        while True:
            user, pwd, role = login()
            while True:
                show_menu(role)
                choice = input("> ").strip()
                if choice == "1":
                    do_query(user, pwd)
                elif choice == "2":
                    send_message(user, pwd, role)
                elif choice == "3":
                    view_inbox(user, pwd, role)
                elif choice == "4":
                    logout(user, pwd)
                    break
                elif choice == "5":
                    logout(user, pwd)
                    sys.exit(0)
                elif choice == "6" and role == "admin":
                    view_logs(user, pwd)
                elif choice == "7" and role == "admin":
                    lock_user(user, pwd)
                elif choice == "8" and role == "admin":
                    add_user(user, pwd)
                else:
                    print("Invalid choice.\n")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

main()
