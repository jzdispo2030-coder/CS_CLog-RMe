#AI tools were used responsibly to support learning and development, not to replace understanding.

import json
import os
import random
import string
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Pyperclip is included directly in the project (see pyperclip.py file)
# Licensed under BSD-3-Clause - see LICENSE-pyperclip.txt
import pyperclip

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

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class GateKeeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GateKeeper Password Manager")
        self.root.geometry("900x700")
        
        # Password visibility toggle
        self.show_passwords = False
        
        # Track if user has verified show password
        self.password_revealed = False
        
        # Current selected account
        self.current_account = None
        
        self.setup_menu()
        self.setup_ui()
        self.show_intro()
        self.refresh_list()
    
    def setup_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Account", command=self.add_account_dialog, accelerator="Ctrl+N")
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh List", command=self.refresh_list)
        view_menu.add_separator()
        view_menu.add_command(label="Show All", command=lambda: self.set_category_filter("All"))
        view_menu.add_command(label="Show Academic", command=lambda: self.set_category_filter("Academic"))
        view_menu.add_command(label="Show Personal", command=lambda: self.set_category_filter("Personal"))
        view_menu.add_command(label="Show Internship", command=lambda: self.set_category_filter("Internship"))
        view_menu.add_command(label="Show Other", command=lambda: self.set_category_filter("Other"))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Password Reuse Report", command=self.show_password_reuse)
        tools_menu.add_command(label="Generate Password", command=self.show_password_generator)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Local Storage Warning", command=self.show_storage_warning)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.add_account_dialog())
    
    def setup_ui(self):
        # Top frame for welcome and stats
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        self.welcome_label = ttk.Label(top_frame, text="GateKeeper Password Manager", font=('Arial', 16, 'bold'))
        self.welcome_label.pack()
        
        self.stats_label = ttk.Label(top_frame, text="", font=('Arial', 10))
        self.stats_label.pack()
        
        # Warning frame
        warning_frame = ttk.Frame(top_frame)
        warning_frame.pack(fill=tk.X, pady=5)
        
        self.warning_text = tk.Text(warning_frame, height=3, width=80, font=('Arial', 9), fg='red', wrap=tk.WORD)
        self.warning_text.pack(fill=tk.X)
        self.warning_text.insert(1.0, "⚠️ LOCAL STORAGE ONLY: Accounts are saved on this device only. Data will be lost if program files are deleted.")
        self.warning_text.config(state=tk.DISABLED)
        
        # Tip of the day
        self.tip_label = ttk.Label(top_frame, text="", font=('Arial', 9, 'italic'))
        self.tip_label.pack(pady=5)
        
        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)
        
        # Search and filter frame
        filter_frame = ttk.Frame(self.root, padding="10")
        filter_frame.pack(fill=tk.X)
        
        # Search bar
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_list)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Category filter
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=(20,5))
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, 
                                       values=["All", "Academic", "Personal", "Internship", "Other"],
                                       state="readonly", width=15)
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.filter_list)
        
        # Add account button
        add_btn = ttk.Button(filter_frame, text="➕ Add Account", command=self.add_account_dialog)
        add_btn.pack(side=tk.RIGHT, padx=5)
        
        # Main content area
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left frame - Account list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Account list label
        ttk.Label(left_frame, text="Your Accounts", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=5)
        
        # Account list with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.accounts_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        font=('Courier', 10), selectmode=tk.SINGLE, height=20)
        self.accounts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.accounts_list.bind('<<ListboxSelect>>', self.on_account_select)
        self.accounts_list.bind('<Double-Button-1>', lambda e: self.view_account_details())
        
        scrollbar.config(command=self.accounts_list.yview)
        
        # Right frame - Account details and actions
        right_frame = ttk.Frame(paned, padding="10")
        paned.add(right_frame, weight=1)
        
        # Details display
        ttk.Label(right_frame, text="Account Details", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Security notice
        security_frame = ttk.Frame(right_frame)
        security_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(security_frame, text="🔒 ", font=('Arial', 10)).pack(side=tk.LEFT)
        self.security_label = ttk.Label(security_frame, text="Click 'Show Password' to reveal", font=('Arial', 9, 'italic'), foreground='gray')
        self.security_label.pack(side=tk.LEFT)
        
        # Details text with scrollbar
        details_frame = ttk.Frame(right_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        details_scrollbar = ttk.Scrollbar(details_frame)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = tk.Text(details_frame, yscrollcommand=details_scrollbar.set,
                                    height=12, width=35, font=('Courier', 10), wrap=tk.WORD)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.details_text.config(state=tk.DISABLED)
        
        details_scrollbar.config(command=self.details_text.yview)
        
        # Action buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # First row of buttons
        row1_frame = ttk.Frame(btn_frame)
        row1_frame.pack(fill=tk.X, pady=2)
        
        self.view_btn = ttk.Button(row1_frame, text="👁️ View Details", 
                                   command=self.view_account_details, state=tk.NORMAL)
        self.view_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        self.copy_btn = ttk.Button(row1_frame, text="📋 Copy Password", 
                                   command=self.copy_password, state=tk.NORMAL)
        self.copy_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Second row of buttons
        row2_frame = ttk.Frame(btn_frame)
        row2_frame.pack(fill=tk.X, pady=2)
        
        self.toggle_btn = ttk.Button(row2_frame, text="👁️ Show Password", 
                                     command=self.toggle_password, state=tk.DISABLED)
        self.toggle_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        self.edit_btn = ttk.Button(row2_frame, text="✏️ Edit Account", 
                                   command=self.edit_account, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Third row - Delete button
        row3_frame = ttk.Frame(btn_frame)
        row3_frame.pack(fill=tk.X, pady=2)
        
        self.delete_btn = ttk.Button(row3_frame, text="🗑️ Delete Account", 
                                     command=self.delete_account, state=tk.DISABLED)
        self.delete_btn.pack(fill=tk.X, padx=2)
        
        # Strength meter
        self.strength_frame = ttk.Frame(right_frame)
        self.strength_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.strength_frame, text="Password Strength:").pack()
        self.strength_bar = ttk.Progressbar(self.strength_frame, length=300, mode='determinate')
        self.strength_bar.pack(pady=5)
        self.strength_label = ttk.Label(self.strength_frame, text="")
        self.strength_label.pack()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_intro(self):
        """Show introduction information"""
        # Update stats
        account_count = len(accounts)
        self.stats_label.config(text=f"📊 {account_count} saved account(s)")
        
        # Check for reused passwords
        reused = detect_password_reuse()
        if reused:
            self.status_var.set(f"⚠️ {len(reused)} reused password(s) detected")
        
        # Random tip of the day
        tips = [
            "💡 Tip: Use 12+ characters for strong passwords",
            "💡 Tip: Mix uppercase, lowercase, numbers, symbols",
            "💡 Tip: Never reuse passwords across accounts",
            "💡 Tip: Search accounts by typing in the search box",
            "💡 Tip: Double-click an account to view details",
            "💡 Tip: You must click 'Show Password' to reveal passwords",
            "💡 Tip: Use Ctrl+N to quickly add a new account",
            "💡 Tip: Check Tools menu for password reports"
        ]
        self.tip_label.config(text=random.choice(tips))
    
    def set_category_filter(self, category):
        """Set category filter from menu"""
        self.category_var.set(category)
        self.filter_list()
    
    def refresh_list(self):
        """Refresh the account list"""
        self.accounts_list.delete(0, tk.END)
        
        # Sort accounts alphabetically for display
        sorted_nicknames = sorted(accounts.keys())
        
        for nickname in sorted_nicknames:
            data = accounts[nickname]
            display_text = f"{nickname} - {data['app']} [{data['category']}]"
            self.accounts_list.insert(tk.END, display_text)
        
        self.show_intro()
    
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
            
            # Enable ALL buttons when account is selected
            self.view_btn.config(state=tk.NORMAL)
            self.copy_btn.config(state=tk.NORMAL)
            self.toggle_btn.config(state=tk.NORMAL)
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
    
    def display_account_details(self, nickname):
        """Display account details in the text area"""
        data = accounts[nickname]
        
        # Show/hide password based on toggle
        if self.show_passwords:
            password_display = data['password']
        else:
            password_display = "•" * len(data['password'])
        
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
        
        # Update strength meter - FIXED: Handle score 0-5 correctly
        score, _ = check_password_strength(data['password'])
        # Convert score 0-5 to percentage 0-100
        self.strength_bar['value'] = (score / 5) * 100
        
        # FIXED: Map score to correct text (0-5)
        if score == 0:
            strength_text = "Very Weak"
        elif score == 1:
            strength_text = "Weak"
        elif score == 2:
            strength_text = "Fair"
        elif score == 3:
            strength_text = "Good"
        elif score == 4:
            strength_text = "Strong"
        elif score == 5:
            strength_text = "Very Strong"
        else:
            strength_text = "Unknown"
        
        self.strength_label.config(text=strength_text)
        
        # Update toggle button text
        if self.show_passwords:
            self.toggle_btn.config(text="👁️ Hide Password")
            self.security_label.config(text="Password revealed - you can now view/copy", foreground='green')
        else:
            self.toggle_btn.config(text="👁️ Show Password")
            self.security_label.config(text="Click 'Show Password' to reveal", foreground='gray')
    
    def view_account_details(self):
        """Show account details in a new window"""
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        # Check if password has been revealed
        if not self.show_passwords:
            messagebox.showwarning(
                "Password Hidden", 
                "🔒 Password is hidden.\n\nPlease click 'Show Password' first to reveal the password before viewing details."
            )
            return
        
        data = accounts[self.current_account]
        
        details = f"🔐 Account Details\n"
        details += "═" * 40 + "\n\n"
        details += f"📝 Nickname: {self.current_account}\n"
        details += f"📱 App: {data['app']}\n"
        details += f"📂 Category: {data['category']}\n"
        details += f"🔑 Password: {data['password']}\n"
        details += f"📅 Created: {data.get('created', 'Unknown')}\n"
        details += f"🕒 Modified: {data.get('last_modified', 'Unknown')}"
        
        messagebox.showinfo("Account Details", details)
    
    def copy_password(self):
        """Copy password to clipboard using pyperclip"""
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        # Check if password has been revealed
        if not self.show_passwords:
            messagebox.showwarning(
                "Password Hidden", 
                "🔒 Password is hidden.\n\nPlease click 'Show Password' first to reveal the password before copying."
            )
            return
        
        password = accounts[self.current_account]['password']
        try:
            pyperclip.copy(password)
            self.status_var.set("✓ Password copied to clipboard!")
            
            # Show success message
            messagebox.showinfo("Success", "Password copied to clipboard!")
        except Exception as e:
            self.status_var.set(f"❌ Copy failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to copy password: {str(e)}")
    
    def toggle_password(self):
        """Toggle password visibility"""
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        if not self.show_passwords:
            # Ask for confirmation before revealing password
            result = messagebox.askyesno(
                "Security Confirmation",
                "Are you sure you want to reveal this password?\n\nMake sure no one is looking at your screen."
            )
            
            if result:
                self.show_passwords = True
            else:
                return
        else:
            self.show_passwords = False
        
        if self.current_account:
            self.display_account_details(self.current_account)
    
    def add_account_dialog(self):
        """Open dialog to add a new account"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Account")
        dialog.geometry("450x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Add New Account", font=('Arial', 14, 'bold')).pack(pady=10)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nickname
        ttk.Label(frame, text="Nickname:").grid(row=0, column=0, sticky=tk.W, pady=5)
        nickname_var = tk.StringVar()
        nickname_entry = ttk.Entry(frame, textvariable=nickname_var, width=30)
        nickname_entry.grid(row=0, column=1, pady=5)
        
        # App name
        ttk.Label(frame, text="App Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        app_var = tk.StringVar()
        app_entry = ttk.Entry(frame, textvariable=app_var, width=30)
        app_entry.grid(row=1, column=1, pady=5)
        
        # Category
        ttk.Label(frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value="Personal")
        category_combo = ttk.Combobox(frame, textvariable=category_var,
                                       values=["Academic", "Personal", "Internship", "Other"],
                                       state="readonly", width=27)
        category_combo.grid(row=2, column=1, pady=5)
        
        # Password option
        ttk.Label(frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        password_frame = ttk.Frame(frame)
        password_frame.grid(row=3, column=1, pady=5)
        
        password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=password_var, width=20, show="•")
        password_entry.pack(side=tk.LEFT)
        
        def generate_and_set():
            password_var.set(generate_password())
            password_entry.config(show="")
            show_pwd_var.set(True)
        
        ttk.Button(password_frame, text="Generate", command=generate_and_set).pack(side=tk.LEFT, padx=5)
        
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
        
        def save_account():
            nickname = nickname_var.get().strip()
            app = app_var.get().strip()
            category = category_var.get()
            password = password_var.get().strip()
            
            if not nickname or not app or not password:
                messagebox.showerror("Error", "All fields are required!")
                return
            
            # Normalize category
            if category.lower() in ["academic", "personal", "internship"]:
                category = category.lower().capitalize()
            else:
                category = "Other"
            
            # Check if nickname already exists
            if nickname in accounts:
                result = messagebox.askyesno(
                    "Duplicate Nickname",
                    f"An account with nickname '{nickname}' already exists.\n\nDo you want to overwrite it?"
                )
                if not result:
                    return
            
            # Check for duplicate data
            duplicate_found = False
            duplicate_nicknames = []
            
            for existing_nick, existing_data in accounts.items():
                if (existing_data["app"] == app and 
                    existing_data["category"] == category and 
                    existing_data["password"] == password and
                    existing_nick != nickname):  # Don't compare with itself if overwriting
                    duplicate_found = True
                    duplicate_nicknames.append(existing_nick)
            
            if duplicate_found:
                dup_list = "\n".join([f"  • {dup}" for dup in duplicate_nicknames])
                result = messagebox.askyesno(
                    "Duplicate Found",
                    f"⚠️ An account with the exact same data already exists under:\n{dup_list}\n\nSave anyway?"
                )
                if not result:
                    return
            
            # Save account
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            accounts[nickname] = {
                "app": app,
                "category": category,
                "password": password,
                "created": current_time,
                "last_modified": current_time
            }
            
            save_accounts()
            self.refresh_list()
            dialog.destroy()
            self.status_var.set(f"✓ Account '{nickname}' saved")
        
        ttk.Button(button_frame, text="Save", command=save_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on nickname entry
        nickname_entry.focus()
    
    def edit_account(self):
        """Edit the selected account"""
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Account")
        edit_window.geometry("450x450")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Get current data
        current_data = accounts[self.current_account]
        
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
        
        password_frame = ttk.Frame(frame)
        password_frame.grid(row=3, column=1, pady=5)
        
        password_var = tk.StringVar(value=current_data['password'])
        password_entry = ttk.Entry(password_frame, textvariable=password_var, width=20, show="•")
        password_entry.pack(side=tk.LEFT)
        
        def generate_and_set():
            password_var.set(generate_password())
            password_entry.config(show="")
            show_pwd_var.set(True)
        
        ttk.Button(password_frame, text="Generate", command=generate_and_set).pack(side=tk.LEFT, padx=5)
        
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
            messagebox.showwarning("No Selection", "Please select an account first.")
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
            
            # Reset password visibility
            self.show_passwords = False
            
            # Disable buttons
            self.view_btn.config(state=tk.NORMAL)  # Keep enabled but will show warning
            self.copy_btn.config(state=tk.NORMAL)  # Keep enabled but will show warning
            self.toggle_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            
            # Reset strength meter
            self.strength_bar['value'] = 0
            self.strength_label.config(text="")
            
            # Reset security label
            self.security_label.config(text="Click 'Show Password' to reveal", foreground='gray')
            
            self.status_var.set("✓ Account deleted")
    
    def show_password_reuse(self):
        """Show password reuse report in a new window"""
        reused = detect_password_reuse()
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Password Reuse Report")
        report_window.geometry("500x400")
        report_window.transient(self.root)
        
        ttk.Label(report_window, text="Password Reuse Report", font=('Arial', 14, 'bold')).pack(pady=10)
        
        if not reused:
            ttk.Label(report_window, text="✅ No password reuse detected!").pack(pady=20)
        else:
            # Create text widget with scrollbar
            frame = ttk.Frame(report_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(frame, yscrollcommand=scrollbar.set, wrap=tk.WORD)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=text_widget.yview)
            
            # Add content
            text_widget.insert(tk.END, f"⚠️ Found {len(reused)} reused password(s):\n\n")
            
            for item in reused:
                text_widget.insert(tk.END, f"Password: {item['password']}\n")
                text_widget.insert(tk.END, f"Used in {item['count']} accounts:\n")
                for acc in item['accounts']:
                    text_widget.insert(tk.END, f"  • {acc} ({accounts[acc]['app']})\n")
                text_widget.insert(tk.END, "\n" + "-"*40 + "\n\n")
            
            text_widget.config(state=tk.DISABLED)
        
        ttk.Button(report_window, text="Close", command=report_window.destroy).pack(pady=10)
    
    def show_password_generator(self):
        """Show password generator tool"""
        pwd = generate_password()
        
        result = messagebox.askyesno(
            "Password Generator",
            f"Generated password:\n\n{pwd}\n\nCopy to clipboard?"
        )
        
        if result:
            try:
                pyperclip.copy(pwd)
                self.status_var.set("✓ Password copied to clipboard!")
                messagebox.showinfo("Success", "Password copied to clipboard!")
            except Exception as e:
                self.status_var.set(f"❌ Copy failed: {str(e)}")
                messagebox.showerror("Error", f"Failed to copy password: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = "GateKeeper Password Manager\n\n"
        about_text += "Version 2.3.0\n\n"
        about_text += "Your personal password manager\n"
        about_text += "Securely store and manage all your accounts\n\n"
        about_text += "© 2026 GateKeeper Team\n"
        about_text += "AI tools used responsibly to support learning"
        
        messagebox.showinfo("About GateKeeper", about_text)
    
    def show_storage_warning(self):
        """Show storage warning"""
        warning_text = "⚠️ LOCAL STORAGE ONLY ⚠️\n\n"
        warning_text += "Your accounts are saved ONLY on this device.\n"
        warning_text += "If you delete this program or its files,\n"
        warning_text += "ALL your saved accounts will be PERMANENTLY LOST.\n\n"
        warning_text += "Consider backing up your accounts.json file\n"
        warning_text += "if you need to keep your data safe."
        
        messagebox.showwarning("Storage Warning", warning_text)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point - launches GUI directly"""
    root = tk.Tk()
    app = GateKeeperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
