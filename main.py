#AI tools were used responsibly to support learning and development, not to replace understanding.

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
    # Loop until we have a valid nickname (unique or user agrees to auto‑generate)
    while True:
        nickname = input("Enter account nickname (e.g., My School LMS): ")
        if nickname in accounts:
            print("An account with this nickname already exists.")
            
            # Question 1: Overwrite?
            while True:
                overwrite = input("Do you want to overwrite it? (yes/no): ").lower()
                if overwrite in ["yes", "y"]:
                    # Confirmation before overwriting
                    confirm = input("Are you sure you want to overwrite? This will replace the existing account. (yes/no): ").lower()
                    if confirm in ["yes", "y"]:
                        # Overwrite confirmed – exit nickname loop and proceed
                        break
                    elif confirm in ["no", "n"]:
                        print("Overwrite cancelled.")
                        # Go back to the start of the duplicate handling
                        continue
                    else:
                        print("Please answer 'yes' or 'no'.")
                elif overwrite in ["no", "n"]:
                    # User does not want to overwrite → move to Question 2
                    break
                else:
                    print("Please answer 'yes' or 'no'.")
            
            # If overwrite was confirmed, we break out of the nickname loop
            if overwrite in ["yes", "y"] and confirm in ["yes", "y"]:
                break

            # Question 2: Create a similar name automatically?
            while True:
                create_similar = input("Do you want to create a new account with a similar name instead? (yes/no): ").lower()
                if create_similar in ["yes", "y"]:
                    # Generate unique nickname by appending a number
                    base_nickname = nickname
                    counter = 2
                    while f"{base_nickname} ({counter})" in accounts:
                        counter += 1
                    nickname = f"{base_nickname} ({counter})"
                    print(f"New nickname generated: {nickname}")
                    break
                elif create_similar in ["no", "n"]:
                    print("Please choose a different nickname.")
                    break
                else:
                    print("Please answer 'yes' or 'no'.")
            
            # If they chose to create a similar name, we exit the nickname loop
            if create_similar in ["yes", "y"]:
                break
            # Otherwise (they chose no), loop continues to ask for a new nickname
            continue
        else:
            # Nickname is unique – exit loop
            break

    app = input("Enter app/platform name (e.g., Canvas, Gmail, Bank): ")
    category = input("Enter category (Academic / Personal / Internship): ")

    while True:
        password = input("Enter password: ")

        score, issues = check_password_strength(password)

        print("\nPassword Strength:", score, "/ 5")

        if issues:
            print("Issues:")
            for issue in issues:
                print("-", issue)

            while True:
                change = input("\nThis password seems too easy. Would you like to change it? (yes/no): ").lower()
                if change in ["yes", "y"]:
                    print("Let's try again!\n")
                    break
                elif change in ["no", "n"]:
                    print("Password saved despite weaknesses.\n")
                    break
                else:
                    print("Please answer 'yes' or 'no'.")
            if change in ["yes", "y"]:
                continue
            else:
                break
        else:
            print("Strong password! Great job!")
            break

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
    search = input("Enter account name or partial name to search: ").lower()
    
    # Find all nicknames that contain the search term (case-insensitive)
    matches = [nick for nick in accounts if search in nick.lower()]
    
    if not matches:
        print("No accounts found matching that name.")
        return
    
    if len(matches) == 1:
        # Directly access the only match
        nickname = matches[0]
        print("\n--- Account Details ---")
        print("App:", accounts[nickname]["app"])
        print("Category:", accounts[nickname]["category"])
        print("Password:", accounts[nickname]["password"])
    else:
        # Multiple matches – list them and let user choose
        print("\nMultiple accounts found:")
        for idx, nick in enumerate(matches, 1):
            print(f"{idx}. {nick}")
        
        while True:
            try:
                choice = int(input(f"\nEnter the number of the account you want to access (1-{len(matches)}): "))
                if 1 <= choice <= len(matches):
                    nickname = matches[choice - 1]
                    print("\n--- Account Details ---")
                    print("App:", accounts[nickname]["app"])
                    print("Category:", accounts[nickname]["category"])
                    print("Password:", accounts[nickname]["password"])
                    break
                else:
                    print(f"Please enter a number between 1 and {len(matches)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

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
