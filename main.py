#AI tools were used responsibly to support learning and development, not to replace understanding.

import json
import os
import random
import string
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Pyperclip is included directly in the project (see pyperclip.py file)
# Licensed under BSD-3-Clause - see LICENSE-pyperclip.txt
import pyperclip

from password_checker import check_password_strength

# Simple formatting
SEPARATOR = "-" * 40
DOUBLE_SEPARATOR = "=" * 40

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

def generate_password(length=16):
    """Generate a strong random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        if (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*" for c in password)):
            return password

def detect_password_reuse():
    """Find passwords that are used across multiple accounts"""
    password_map = {}
    reused_passwords = []
    
    for nickname, data in accounts.items():
        pwd = data['password']
        if pwd in password_map:
            password_map[pwd].append(nickname)
        else:
            password_map[pwd] = [nickname]
    
    for pwd, nicknames in password_map.items():
        if len(nicknames) > 1:
            reused_passwords.append({
                'password': pwd,
                'accounts': nicknames,
                'count': len(nicknames)
            })
    
    return reused_passwords

def show_intro():
    """Display introduction menu with welcome message and tips"""
    print(f"\n{DOUBLE_SEPARATOR}")
    print("          GATEKEEPER")
    print(DOUBLE_SEPARATOR)
    print("\nYour personal password manager")
    
    print(f"\n📁 Local storage only")
    print("   Accounts saved on this device")
    print("   ⚠️  Data lost if program files are deleted")
    
    tips = [
        "💡 Tip: Use 12+ characters for strong passwords",
        "💡 Tip: Mix uppercase, lowercase, numbers, symbols",
        "💡 Tip: Never reuse passwords across accounts",
        "💡 Tip: Search accounts by partial names",
        "💡 Tip: You can have multiple accounts with same name",
        "💡 Tip: Delete old accounts to stay organized",
        "💡 Tip: Try the GUI for visual password management!"
    ]
    print(f"\n{random.choice(tips)}")
    
    account_count = len(accounts)
    print(f"\n📊 {account_count} saved account(s)")
    
    reused = detect_password_reuse()
    if reused:
        print(f"⚠️  {len(reused)} reused password(s) detected")
    
    print(f"\n{SEPARATOR}")

def add_account():
    nickname = input("\nNickname (e.g., My School LMS): ")

    app = input("App name (e.g., Canvas, Gmail): ")
    category = input("Category (Academic/Personal/Internship/Other): ")
    
    # Normalize category
    category_lower = category.lower()
    if category_lower in ["academic", "personal", "internship"]:
        category = category_lower.capitalize()
    else:
        category = "Other"

    use_generated = input("Generate strong password? (y/n): ").lower()
    if use_generated in ["yes", "y"]:
        password = generate_password()
        print(f"Generated: {password}")
    else:
        while True:
            password = input("Password: ")

            score, issues = check_password_strength(password)

            print(f"\nStrength: {score}/5")

            if issues:
                print("Issues:")
                for issue in issues:
                    print(f"  • {issue}")

                while True:
                    change = input("\nChange password? (y/n): ").lower()
                    if change in ["yes", "y"]:
                        print("")
                        break
                    elif change in ["no", "n"]:
                        print("Saved with weaknesses\n")
                        break
                    else:
                        print("Please answer y or n")
                if change in ["yes", "y"]:
                    continue
                else:
                    break
            else:
                print("Strong password!")
                break

    # Check for duplicate data
    duplicate_found = False
    duplicate_nicknames = []
    
    for existing_nick, existing_data in accounts.items():
        if (existing_data["app"] == app and 
            existing_data["category"] == category and 
            existing_data["password"] == password):
            duplicate_found = True
            duplicate_nicknames.append(existing_nick)
    
    if duplicate_found:
        print(f"\n⚠️  Duplicate account found:")
        for dup_nick in duplicate_nicknames:
            print(f"  • {dup_nick}")
        
        while True:
            continue_anyway = input("\nSave anyway? (y/n): ").lower()
            if continue_anyway in ["yes", "y"]:
                print("Saving...\n")
                break
            elif continue_anyway in ["no", "n"]:
                print("Cancelled\n")
                return
            else:
                print("Please answer y or n")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    accounts[nickname] = {
        "app": app,
        "category": category,
        "password": password,
        "created": current_time,
        "last_modified": current_time
    }

    save_accounts()
    print("✓ Account saved\n")

def view_accounts():
    if not accounts:
        print("\nNo accounts saved yet")
        return

    print(f"\nFilter:")
    print("1. All")
    print("2. Academic")
    print("3. Personal")
    print("4. Internship")
    print("5. Other")
    
    filter_choice = input("Choice (1-5): ")
    
    # Filter accounts based on choice
    filtered_accounts = {}
    if filter_choice == "1":
        filtered_accounts = accounts
    elif filter_choice == "2":
        filtered_accounts = {k: v for k, v in accounts.items() if v["category"].lower() == "academic"}
    elif filter_choice == "3":
        filtered_accounts = {k: v for k, v in accounts.items() if v["category"].lower() == "personal"}
    elif filter_choice == "4":
        filtered_accounts = {k: v for k, v in accounts.items() if v["category"].lower() == "internship"}
    elif filter_choice == "5":
        filtered_accounts = {k: v for k, v in accounts.items() if v["category"].lower() not in ["academic", "personal", "internship"]}
    else:
        print("Showing all")
        filtered_accounts = accounts
    
    if not filtered_accounts:
        print("No accounts in this category")
        return

    print(f"\nSaved Accounts:")
    sorted_nicknames = sorted(filtered_accounts.keys())
    
    for idx, nickname in enumerate(sorted_nicknames, 1):
        data = filtered_accounts[nickname]
        created = data.get('created', 'Unknown').split()[0]
        print(f"{idx}. {nickname} ({data['app']} | {data['category']})")
        print(f"   📅 {created}")
    
    while True:
        choice = input("\nDelete an account? (y/n): ").lower()
        if choice in ["yes", "y"]:
            while True:
                try:
                    delete_num = int(input(f"Account number to delete (1-{len(sorted_nicknames)}): "))
                    if 1 <= delete_num <= len(sorted_nicknames):
                        nickname_to_delete = sorted_nicknames[delete_num - 1]
                        
                        print(f"\nDelete: {nickname_to_delete}")
                        print(f"App: {accounts[nickname_to_delete]['app']}")
                        
                        while True:
                            confirm = input("\nConfirm delete? (y/n): ").lower()
                            if confirm in ["yes", "y"]:
                                del accounts[nickname_to_delete]
                                save_accounts()
                                print("✓ Account deleted")
                                return
                            elif confirm in ["no", "n"]:
                                print("Cancelled")
                                return
                            else:
                                print("Please answer y or n")
                    else:
                        print(f"Enter 1-{len(sorted_nicknames)}")
                except ValueError:
                    print("Enter a number")
        elif choice in ["no", "n"]:
            break
        else:
            print("Please answer y or n")

def access_account():
    search = input("\nSearch (partial name): ").lower()
    
    matches = [nick for nick in accounts if search in nick.lower()]
    
    if not matches:
        print("No matches found")
        return
    
    matches.sort()
    
    if len(matches) == 1:
        nickname = matches[0]
        print(f"\n--- {nickname} ---")
        print(f"App: {accounts[nickname]['app']}")
        print(f"Category: {accounts[nickname]['category']}")
        print(f"Password: {accounts[nickname]['password']}")
        created = accounts[nickname].get('created', 'Unknown').split()[0]
        print(f"Created: {created}")
    else:
        print(f"\nMatches:")
        for idx, nick in enumerate(matches, 1):
            print(f"{idx}. {nick}")
        
        while True:
            try:
                choice = int(input(f"\nChoose (1-{len(matches)}): "))
                if 1 <= choice <= len(matches):
                    nickname = matches[choice - 1]
                    print(f"\n--- {nickname} ---")
                    print(f"App: {accounts[nickname]['app']}")
                    print(f"Category: {accounts[nickname]['category']}")
                    print(f"Password: {accounts[nickname]['password']}")
                    created = accounts[nickname].get('created', 'Unknown').split()[0]
                    print(f"Created: {created}")
                    break
                else:
                    print(f"Enter 1-{len(matches)}")
            except ValueError:
                print("Enter a number")

def show_password_reuse():
    reused = detect_password_reuse()
    
    if not reused:
        print(f"\n✓ No password reuse detected")
        return
    
    print(f"\n⚠️  PASSWORD REUSE")
    print(SEPARATOR)
    
    for item in reused:
        print(f"\nPassword: {item['password']}")
        print(f"Used in {item['count']} accounts:")
        for acc in item['accounts']:
            print(f"  • {acc} ({accounts[acc]['app']})")
    
    print(f"\n⚠️  Use unique passwords for better security")

# ============================================================================
# ENHANCED GUI WITH PYPERCLIP AND EDIT FEATURE
# ============================================================================

class GateKeeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GateKeeper Password Manager")
        self.root.geometry("750x600")
        
        # Password visibility toggle
        self.show_passwords = False
        
        # Current selected account
        self.current_account = None
        
        self.setup_ui()
        self.refresh_list()
    
    def setup_ui(self):
        # Top frame for search and actions
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        # Search bar with real-time filtering
        ttk.Label(top_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_list)
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Category filter dropdown
        ttk.Label(top_frame, text="Category:").pack(side=tk.LEFT, padx=(20,5))
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(top_frame, textvariable=self.category_var, 
                                       values=["All", "Academic", "Personal", "Internship", "Other"],
                                       state="readonly", width=15)
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.filter_list)
        
        # Refresh button
        refresh_btn = ttk.Button(top_frame, text="🔄 Refresh", command=self.refresh_list)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Main content area (paned window)
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left frame - Account list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Account list with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.accounts_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        font=('Courier', 10), selectmode=tk.SINGLE)
        self.accounts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.accounts_list.bind('<<ListboxSelect>>', self.on_account_select)
        
        scrollbar.config(command=self.accounts_list.yview)
        
        # Right frame - Account details and actions
        right_frame = ttk.Frame(paned, padding="10")
        paned.add(right_frame, weight=1)
        
        # Details display
        ttk.Label(right_frame, text="Account Details", font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.details_text = tk.Text(right_frame, height=10, width=35, font=('Courier', 10))
        self.details_text.pack(fill=tk.X, pady=5)
        self.details_text.config(state=tk.DISABLED)
        
        # Action buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.copy_btn = ttk.Button(btn_frame, text="📋 Copy Password", 
                                   command=self.copy_password, state=tk.DISABLED)
        self.copy_btn.pack(fill=tk.X, pady=2)
        
        self.toggle_btn = ttk.Button(btn_frame, text="👁️ Show Password", 
                                     command=self.toggle_password, state=tk.DISABLED)
        self.toggle_btn.pack(fill=tk.X, pady=2)
        
        # Edit button
        self.edit_btn = ttk.Button(btn_frame, text="✏️ Edit Account", 
                                   command=self.edit_account, state=tk.DISABLED)
        self.edit_btn.pack(fill=tk.X, pady=2)
        
        # Strength meter
        self.strength_frame = ttk.Frame(right_frame)
        self.strength_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.strength_frame, text="Password Strength:").pack()
        self.strength_bar = ttk.Progressbar(self.strength_frame, length=200, mode='determinate')
        self.strength_bar.pack(pady=5)
        self.strength_label = ttk.Label(self.strength_frame, text="")
        self.strength_label.pack()
        
        # Delete button (with confirmation)
        self.delete_btn = ttk.Button(right_frame, text="🗑️ Delete Account", 
                                     command=self.delete_account, state=tk.DISABLED)
        self.delete_btn.pack(fill=tk.X, pady=2)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def refresh_list(self):
        """Refresh the account list"""
        self.accounts_list.delete(0, tk.END)
        
        # Sort accounts alphabetically for display
        sorted_nicknames = sorted(accounts.keys())
        
        for nickname in sorted_nicknames:
            data = accounts[nickname]
            display_text = f"{nickname} - {data['app']} [{data['category']}]"
            self.accounts_list.insert(tk.END, display_text)
        
        self.status_var.set(f"Total: {len(accounts)} accounts")
    
    def filter_list(self, *args):
        """Filter accounts based on search term and category"""
        search_term = self.search_var.get().lower()
        category_filter = self.category_var.get()
        
        self.accounts_list.delete(0, tk.END)
        
        # Sort accounts alphabetically for display
        sorted_nicknames = sorted(accounts.keys())
        
        for nickname in sorted_nicknames:
            data = accounts[nickname]
            
            # Apply category filter
            if category_filter != "All":
                if category_filter == "Other":
                    if data['category'].lower() in ["academic", "personal", "internship"]:
                        continue
                elif data['category'] != category_filter:
                    continue
            
            # Apply search filter
            if search_term:
                if (search_term not in nickname.lower() and 
                    search_term not in data['app'].lower()):
                    continue
            
            display_text = f"{nickname} - {data['app']} [{data['category']}]"
            self.accounts_list.insert(tk.END, display_text)
    
    def on_account_select(self, event):
        """Handle account selection"""
        selection = self.accounts_list.curselection()
        if not selection:
            return
        
        # Get the selected account nickname
        display_text = self.accounts_list.get(selection[0])
        nickname = display_text.split(" - ")[0]
        
        if nickname in accounts:
            self.current_account = nickname
            self.display_account_details(nickname)
            
            # Enable buttons
            self.copy_btn.config(state=tk.NORMAL)
            self.toggle_btn.config(state=tk.NORMAL)
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
    
    def display_account_details(self, nickname):
        """Display account details in the text area"""
        data = accounts[nickname]
        
        # Show/hide password based on toggle
        password_display = data['password'] if self.show_passwords else "•" * len(data['password'])
        
        details = f"Nickname: {nickname}\n"
        details += f"App: {data['app']}\n"
        details += f"Category: {data['category']}\n"
        details += f"Password: {password_display}\n"
        details += f"Created: {data.get('created', 'Unknown')}\n"
        details += f"Modified: {data.get('last_modified', 'Unknown')}"
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)
        
        # Update strength meter
        score, _ = check_password_strength(data['password'])
        self.strength_bar['value'] = (score / 5) * 100
        
        strength_texts = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        self.strength_label.config(text=strength_texts[score])
        
        # Update toggle button text
        if self.show_passwords:
            self.toggle_btn.config(text="👁️ Hide Password")
        else:
            self.toggle_btn.config(text="👁️ Show Password")
    
    def copy_password(self):
        """Copy password to clipboard using pyperclip"""
        if self.current_account and self.current_account in accounts:
            password = accounts[self.current_account]['password']
            try:
                pyperclip.copy(password)
                self.status_var.set("✓ Password copied to clipboard!")
            except Exception as e:
                self.status_var.set(f"❌ Copy failed: {str(e)}")
    
    def toggle_password(self):
        """Toggle password visibility"""
        self.show_passwords = not self.show_passwords
        if self.current_account:
            self.display_account_details(self.current_account)
    
    def edit_account(self):
        """Edit the selected account"""
        if not self.current_account:
            return
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Account")
        edit_window.geometry("450x350")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Get current data
        current_data = accounts[self.current_account]
        
        # Create form
        ttk.Label(edit_window, text="Edit Account", font=('Arial', 14, 'bold')).pack(pady=10)
        
        frame = ttk.Frame(edit_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nickname (read-only)
        ttk.Label(frame, text="Nickname:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=self.current_account, font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # App name
        ttk.Label(frame, text="App Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        app_var = tk.StringVar(value=current_data['app'])
        app_entry = ttk.Entry(frame, textvariable=app_var, width=30)
        app_entry.grid(row=1, column=1, pady=5)
        
        # Category
        ttk.Label(frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value=current_data['category'])
        category_combo = ttk.Combobox(frame, textvariable=category_var,
                                       values=["Academic", "Personal", "Internship", "Other"],
                                       state="readonly", width=27)
        category_combo.grid(row=2, column=1, pady=5)
        
        # Password
        ttk.Label(frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        password_var = tk.StringVar(value=current_data['password'])
        password_entry = ttk.Entry(frame, textvariable=password_var, width=30, show="•")
        password_entry.grid(row=3, column=1, pady=5)
        
        # Show password checkbox
        show_pwd_var = tk.BooleanVar()
        def toggle_password_visibility():
            if show_pwd_var.get():
                password_entry.config(show="")
            else:
                password_entry.config(show="•")
        
        ttk.Checkbutton(frame, text="Show password", variable=show_pwd_var, 
                       command=toggle_password_visibility).grid(row=4, column=0, columnspan=2, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_changes():
            # Update the account
            accounts[self.current_account]['app'] = app_var.get()
            accounts[self.current_account]['category'] = category_var.get()
            accounts[self.current_account]['password'] = password_var.get()
            accounts[self.current_account]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            save_accounts()
            self.display_account_details(self.current_account)
            self.refresh_list()
            edit_window.destroy()
            self.status_var.set("✓ Account updated")
        
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_account(self):
        """Delete current account with confirmation"""
        if not self.current_account:
            return
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{self.current_account}'?\n\nThis cannot be undone."
        )
        
        if result:
            del accounts[self.current_account]
            save_accounts()
            self.current_account = None
            self.refresh_list()
            
            # Clear details
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.config(state=tk.DISABLED)
            
            # Disable buttons
            self.copy_btn.config(state=tk.DISABLED)
            self.toggle_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            
            # Reset strength meter
            self.strength_bar['value'] = 0
            self.strength_label.config(text="")
            
            self.status_var.set("✓ Account deleted")

def launch_gui():
    """Launch enhanced GUI"""
    root = tk.Tk()
    app = GateKeeperGUI(root)
    root.mainloop()

# Show introduction menu
show_intro()

while True:
    print(f"\nGATEKEEPER MENU")
    print(SEPARATOR)
    print("1. Add Account")
    print("2. View Accounts")
    print("3. Access Account")
    print("4. Check Password Reuse")
    print("5. Launch GUI")
    print("6. Exit")

    choice = input("\nChoice: ")

    if choice == "1":
        add_account()
    elif choice == "2":
        view_accounts()
    elif choice == "3":
        access_account()
    elif choice == "4":
        show_password_reuse()
    elif choice == "5":
        launch_gui()
    elif choice == "6":
        print("\nGoodbye!\n")
        break
    else:
        print("Invalid option")
