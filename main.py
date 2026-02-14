import json
import os
from password_checker import check_password_strength

FILENAME = "accounts.json"

# Load existing accounts
if os.path.exists(FILENAME):
    with open(FILENAME, "r") as file:
        accounts = json.load(file)
else:
    accounts = {}

def save_accounts():
    with open(FILENAME, "w") as file:
        json.dump(accounts, file, indent=4)

def add_account():
    nickname = input("Enter account nickname (e.g., My School LMS): ")
    app = input("Enter app/platform name (e.g., Canvas, Gmail, Bank): ")
    category = input("Enter category (Academic / Personal / Internship): ")
    password = input("Enter password: ")

    score, issues = check_password_strength(password)

    print("\nPassword Strength:", score, "/ 5")

    if issues:
        print("Issues:")
        for issue in issues:
            print("-", issue)
    else:
        print("Strong password!")

    accounts[nickname] = {
        "app": app,
        "category": category,
        "password": password
    }

    save_accounts()
    print("Account saved successfully!\n")

def view_accounts():
    if not accounts:
        print("No accounts saved yet.")
        return

    print("\nSaved Accounts:")
    for nickname, data in accounts.items():
        print(f"- {nickname} ({data['app']} | {data['category']})")

def access_account():
    nickname = input("Enter account nickname to access: ")

    if nickname in accounts:
        print("\n--- Account Details ---")
        print("App:", accounts[nickname]["app"])
        print("Category:", accounts[nickname]["category"])
        print("Password:", accounts[nickname]["password"])
    else:
        print("Account not found.")

while True:
    print("\n===== GateKeeper =====")
    print("1. Add Account")
    print("2. View Accounts")
    print("3. Access Account")
    print("4. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_account()
    elif choice == "2":
        view_accounts()
    elif choice == "3":
        access_account()
    elif choice == "4":
        break
    else:
        print("Invalid option.")
