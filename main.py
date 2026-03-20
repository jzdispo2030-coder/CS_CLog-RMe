#AI tools were used responsibly to support learning and development, not to replace understanding.

import json
import os
import random
import string
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Pyperclip is included directly in the project (see pyperclip.py file)
# Licensed under BSD-3-Clause - see LICENSE-pyperclip.txt
import pyperclip

from password_checker import check_password_strength, get_password_feedback, estimate_crack_time

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

def generate_password(length=20):
    """Generate a strong random password - now longer by default"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
    
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        score, _ = check_password_strength(password)
        if score >= 8:  # Aim for very strong passwords
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
# DARK MODE COLORS
# ============================================================================

class DarkTheme:
    bg_dark = "#1e1e1e"
    bg_medium = "#2d2d2d"
    bg_light = "#3c3c3c"
    fg_light = "#ffffff"
    fg_dim = "#cccccc"
    accent_blue = "#007acc"
    accent_green = "#2ecc71"
    accent_red = "#e74c3c"
    accent_orange = "#f39c12"
    accent_purple = "#9b59b6"
    border = "#555555"
    selection = "#264f78"
    
    # Strength colors (for dark mode)
    strength_colors = {
        "Excellent": "#2ecc71",
        "Very Strong": "#27ae60",
        "Strong": "#3498db",
        "Good": "#f39c12",
        "Fair": "#f1c40f",
        "Weak": "#e67e22",
        "Very Weak": "#e74c3c"
    }

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class GateKeeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GateKeeper Password Manager")
        self.root.geometry("1000x800")
        
        # Apply dark mode to root
        self.root.configure(bg=DarkTheme.bg_dark)
        
        # Password visibility toggle
        self.show_passwords = False
        
        # Current selected account
        self.current_account = None
        
        # Configure styles for dark mode
        self.setup_styles()
        
        self.setup_menu()
        self.setup_ui()
        self.show_intro()
        self.refresh_list()
    
    def setup_styles(self):
        """Configure ttk styles for dark mode"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('.', 
                       background=DarkTheme.bg_dark,
                       foreground=DarkTheme.fg_light,
                       fieldbackground=DarkTheme.bg_medium,
                       troughcolor=DarkTheme.bg_light,
                       selectbackground=DarkTheme.selection,
                       selectforeground=DarkTheme.fg_light)
        
        style.configure('TLabel', background=DarkTheme.bg_dark, foreground=DarkTheme.fg_light)
        style.configure('TFrame', background=DarkTheme.bg_dark)
        style.configure('TLabelframe', background=DarkTheme.bg_dark, foreground=DarkTheme.fg_light)
        style.configure('TLabelframe.Label', background=DarkTheme.bg_dark, foreground=DarkTheme.fg_light)
        
        style.configure('TButton', 
                       background=DarkTheme.bg_light,
                       foreground=DarkTheme.fg_light,
                       borderwidth=1,
                       focusthickness=3,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', DarkTheme.accent_blue),
                           ('pressed', DarkTheme.bg_medium)],
                 foreground=[('active', DarkTheme.fg_light)])
        
        style.configure('TEntry', 
                       fieldbackground=DarkTheme.bg_medium,
                       foreground=DarkTheme.fg_light,
                       insertcolor=DarkTheme.fg_light)
        
        style.configure('TCombobox', 
                       fieldbackground=DarkTheme.bg_medium,
                       foreground=DarkTheme.fg_light,
                       selectbackground=DarkTheme.selection)
        
        style.configure('TScrollbar',
                       background=DarkTheme.bg_light,
                       troughcolor=DarkTheme.bg_medium,
                       arrowcolor=DarkTheme.fg_light)
        
        style.configure('TProgressbar',
                       background=DarkTheme.accent_green,
                       troughcolor=DarkTheme.bg_medium)
        
        style.configure('TMenubar', background=DarkTheme.bg_dark, foreground=DarkTheme.fg_light)
        style.configure('TMenu', background=DarkTheme.bg_medium, foreground=DarkTheme.fg_light)
        
        # Configure PanedWindow
        style.configure('TPanedwindow', background=DarkTheme.border)
    
    def setup_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg=DarkTheme.bg_medium, fg=DarkTheme.fg_light,
                         activebackground=DarkTheme.accent_blue, activeforeground=DarkTheme.fg_light)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.fg_light,
                           activebackground=DarkTheme.accent_blue, activeforeground=DarkTheme.fg_light)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Account", command=self.add_account_dialog, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.fg_light,
                           activebackground=DarkTheme.accent_blue, activeforeground=DarkTheme.fg_light)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh List", command=self.refresh_list)
        view_menu.add_separator()
        view_menu.add_command(label="Show All", command=lambda: self.set_category_filter("All"))
        view_menu.add_command(label="Show Academic", command=lambda: self.set_category_filter("Academic"))
        view_menu.add_command(label="Show Personal", command=lambda: self.set_category_filter("Personal"))
        view_menu.add_command(label="Show Internship", command=lambda: self.set_category_filter("Internship"))
        view_menu.add_command(label="Show Other", command=lambda: self.set_category_filter("Other"))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.fg_light,
                            activebackground=DarkTheme.accent_blue, activeforeground=DarkTheme.fg_light)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Password Reuse Report", command=self.show_password_reuse)
        tools_menu.add_command(label="Generate Strong Password", command=self.show_password_generator)
        tools_menu.add_command(label="Password Health Check", command=self.show_password_health)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.fg_light,
                           activebackground=DarkTheme.accent_blue, activeforeground=DarkTheme.fg_light)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Local Storage Warning", command=self.show_storage_warning)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.add_account_dialog())
    
    def setup_ui(self):
        # Top frame for welcome and stats
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        self.welcome_label = ttk.Label(top_frame, text="GateKeeper Password Manager", 
                                       font=('Arial', 18, 'bold'))
        self.welcome_label.pack()
        
        self.stats_label = ttk.Label(top_frame, text="", font=('Arial', 11))
        self.stats_label.pack()
        
        # Warning frame
        warning_frame = ttk.Frame(top_frame)
        warning_frame.pack(fill=tk.X, pady=5)
        
        self.warning_text = tk.Text(warning_frame, height=2, width=80, font=('Arial', 9), 
                                    bg=DarkTheme.bg_medium, fg=DarkTheme.accent_red, 
                                    wrap=tk.WORD, bd=1, relief=tk.SUNKEN)
        self.warning_text.pack(fill=tk.X)
        self.warning_text.insert(1.0, "⚠️ LOCAL STORAGE ONLY: Accounts saved on this device only. Data lost if program files are deleted.")
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
        ttk.Label(filter_frame, text="🔍 Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_list)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Category filter
        ttk.Label(filter_frame, text="📂 Category:").pack(side=tk.LEFT, padx=(20,5))
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
        ttk.Label(left_frame, text="Your Accounts", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        
        # Account list with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.accounts_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        font=('Courier', 10), selectmode=tk.SINGLE, height=20,
                                        bg=DarkTheme.bg_medium, fg=DarkTheme.fg_light,
                                        selectbackground=DarkTheme.selection,
                                        selectforeground=DarkTheme.fg_light,
                                        bd=1, relief=tk.SUNKEN)
        self.accounts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.accounts_list.bind('<<ListboxSelect>>', self.on_account_select)
        self.accounts_list.bind('<Double-Button-1>', lambda e: self.inspect_password())
        
        scrollbar.config(command=self.accounts_list.yview)
        
        # Right frame - Account details and actions
        right_frame = ttk.Frame(paned, padding="15")
        paned.add(right_frame, weight=1)
        
        # Details header
        details_header = ttk.Frame(right_frame)
        details_header.pack(fill=tk.X)
        
        ttk.Label(details_header, text="Account Details", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Details text with scrollbar
        details_frame = ttk.Frame(right_frame)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        details_scrollbar = ttk.Scrollbar(details_frame)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = tk.Text(details_frame, yscrollcommand=details_scrollbar.set,
                                    height=10, width=40, font=('Courier', 10), wrap=tk.WORD,
                                    bg=DarkTheme.bg_medium, fg=DarkTheme.fg_light,
                                    insertbackground=DarkTheme.fg_light,
                                    bd=1, relief=tk.SUNKEN)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.details_text.config(state=tk.DISABLED)
        
        details_scrollbar.config(command=self.details_text.yview)
        
        # Enhanced Strength Meter Frame
        strength_frame = ttk.LabelFrame(right_frame, text="Password Strength Analysis", padding="10")
        strength_frame.pack(fill=tk.X, pady=10)
        
        # Strength bar and label
        bar_frame = ttk.Frame(strength_frame)
        bar_frame.pack(fill=tk.X, pady=5)
        
        self.strength_bar = ttk.Progressbar(bar_frame, length=300, mode='determinate')
        self.strength_bar.pack(side=tk.LEFT, padx=5)
        
        self.strength_label = ttk.Label(bar_frame, text="", font=('Arial', 10, 'bold'))
        self.strength_label.pack(side=tk.LEFT, padx=10)
        
        # Crack time estimate
        time_frame = ttk.Frame(strength_frame)
        time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(time_frame, text="⏱️ Estimated crack time:", font=('Arial', 9)).pack(side=tk.LEFT)
        self.crack_time_label = ttk.Label(time_frame, text="", font=('Arial', 9, 'bold'))
        self.crack_time_label.pack(side=tk.LEFT, padx=5)
        
        # Strengths list
        strengths_frame = ttk.Frame(strength_frame)
        strengths_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(strengths_frame, text="✅ Strengths:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.strengths_list = tk.Text(strengths_frame, height=2, width=40, font=('Arial', 8), 
                                      wrap=tk.WORD, bg=DarkTheme.bg_medium, fg=DarkTheme.accent_green,
                                      bd=1, relief=tk.SUNKEN)
        self.strengths_list.pack(fill=tk.X, pady=2)
        self.strengths_list.config(state=tk.DISABLED)
        
        # Issues list
        issues_frame = ttk.Frame(strength_frame)
        issues_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(issues_frame, text="⚠️ Issues to fix:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.issues_list = tk.Text(issues_frame, height=2, width=40, font=('Arial', 8),
                                   wrap=tk.WORD, bg=DarkTheme.bg_medium, fg=DarkTheme.accent_red,
                                   bd=1, relief=tk.SUNKEN)
        self.issues_list.pack(fill=tk.X, pady=2)
        self.issues_list.config(state=tk.DISABLED)
        
        # ============================================================================
        # SCROLLABLE BUTTON AREA
        # ============================================================================
        button_container = ttk.Frame(right_frame)
        button_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create canvas and scrollbar for buttons
        button_canvas = tk.Canvas(button_container, bg=DarkTheme.bg_dark, highlightthickness=0)
        button_scrollbar = ttk.Scrollbar(button_container, orient="vertical", command=button_canvas.yview)
        button_scrollable_frame = ttk.Frame(button_canvas)
        
        button_scrollable_frame.bind(
            "<Configure>",
            lambda e: button_canvas.configure(scrollregion=button_canvas.bbox("all"))
        )
        
        button_canvas.create_window((0, 0), window=button_scrollable_frame, anchor="n")
        button_canvas.configure(yscrollcommand=button_scrollbar.set)
        
        button_canvas.pack(side="left", fill="both", expand=True)
        button_scrollbar.pack(side="right", fill="y")
        
        # Action buttons inside scrollable frame
        btn_frame = ttk.Frame(button_scrollable_frame)
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # First row
        row1_frame = ttk.Frame(btn_frame)
        row1_frame.pack(fill=tk.X, pady=3)
        
        self.inspect_btn = ttk.Button(row1_frame, text="🔍 Inspect Password", 
                                   command=self.inspect_password)
        self.inspect_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        self.copy_btn = ttk.Button(row1_frame, text="📋 Copy Password", 
                                   command=self.copy_password)
        self.copy_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Second row
        row2_frame = ttk.Frame(btn_frame)
        row2_frame.pack(fill=tk.X, pady=3)
        
        self.toggle_btn = ttk.Button(row2_frame, text="👁️ Show Password", 
                                     command=self.toggle_password, state=tk.DISABLED)
        self.toggle_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        self.edit_btn = ttk.Button(row2_frame, text="✏️ Edit Account", 
                                   command=self.edit_account, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Third row
        row3_frame = ttk.Frame(btn_frame)
        row3_frame.pack(fill=tk.X, pady=3)
        
        self.delete_btn = ttk.Button(row3_frame, text="🗑️ Delete Account", 
                                     command=self.delete_account, state=tk.DISABLED)
        self.delete_btn.pack(fill=tk.X, padx=2)
        
        # Add some padding at the bottom for scrolling
        ttk.Frame(btn_frame, height=20).pack()
        
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
            self.status_var.set(f"⚠️ {len(reused)} reused password(s) detected - Check Tools menu")
        
        # Random tip of the day
        tips = [
            "💡 Tip: Use 16+ characters for excellent password strength",
            "💡 Tip: Mix uppercase, lowercase, numbers, and symbols",
            "💡 Tip: Never reuse passwords across different accounts",
            "💡 Tip: Longer passwords are stronger than complex short ones",
            "💡 Tip: Use the Inspect Password button for detailed analysis",
            "💡 Tip: Check password health in the Tools menu",
            "💡 Tip: Double-click an account to inspect its password",
            "💡 Tip: Scroll down to see all action buttons"
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
            
            # Enable all buttons
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
        
        # Format details with better spacing
        details = f"📝 Nickname: {nickname}\n"
        details += f"📱 App: {data['app']}\n"
        details += f"📂 Category: {data['category']}\n"
        details += f"🔑 Password: {password_display}\n"
        details += f"📅 Created: {data.get('created', 'Unknown')}\n"
        details += f"🕒 Modified: {data.get('last_modified', 'Unknown')}"
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)
        
        # Get enhanced password feedback
        feedback = get_password_feedback(data['password'])
        
        # Update strength meter
        self.strength_bar['value'] = (feedback['score'] / 10) * 100
        self.strength_label.config(text=f"{feedback['category']} ({feedback['score']:.1f}/10)", 
                                   foreground=DarkTheme.strength_colors.get(feedback['category'], DarkTheme.fg_light))
        
        # Update crack time estimate
        crack_time = estimate_crack_time(data['password'])
        self.crack_time_label.config(text=crack_time)
        
        # Update strengths list
        self.strengths_list.config(state=tk.NORMAL)
        self.strengths_list.delete(1.0, tk.END)
        if feedback['strengths']:
            for s in feedback['strengths']:
                self.strengths_list.insert(tk.END, f"• {s}\n")
        else:
            self.strengths_list.insert(tk.END, "• No notable strengths\n")
        self.strengths_list.config(state=tk.DISABLED)
        
        # Update issues list
        self.issues_list.config(state=tk.NORMAL)
        self.issues_list.delete(1.0, tk.END)
        if feedback['issues']:
            for issue in feedback['issues']:
                self.issues_list.insert(tk.END, f"• {issue}\n")
        else:
            self.issues_list.insert(tk.END, "• No issues found - Excellent!\n")
        self.issues_list.config(state=tk.DISABLED)
        
        # Update toggle button text
        if self.show_passwords:
            self.toggle_btn.config(text="👁️ Hide Password")
        else:
            self.toggle_btn.config(text="👁️ Show Password")
    
    def inspect_password(self):
        """Open detailed password inspector with actionable tips"""
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        data = accounts[self.current_account]
        feedback = get_password_feedback(data['password'])
        
        # Create inspector window with dark mode
        inspector = tk.Toplevel(self.root)
        inspector.title(f"Password Inspector - {self.current_account}")
        inspector.geometry("600x700")
        inspector.configure(bg=DarkTheme.bg_dark)
        inspector.transient(self.root)
        inspector.grab_set()
        inspector.focus_set()
        
        # Header with score
        header_frame = ttk.Frame(inspector, padding="15")
        header_frame.pack(fill=tk.X)
        
        # Score display with color
        score_frame = ttk.Frame(header_frame)
        score_frame.pack(pady=5)
        
        score_color = DarkTheme.strength_colors.get(feedback['category'], DarkTheme.fg_light)
        score_label = tk.Label(score_frame, text=f"{feedback['score']:.1f}/10", 
                               font=('Arial', 24, 'bold'), fg=score_color, bg=DarkTheme.bg_dark)
        score_label.pack()
        
        ttk.Label(header_frame, text=f"Password Strength: {feedback['category']}", 
                  font=('Arial', 14, 'bold')).pack()
        
        # Notebook for tabs
        notebook = ttk.Notebook(inspector)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Analysis
        analysis_frame = ttk.Frame(notebook, padding="10")
        notebook.add(analysis_frame, text="Analysis")
        
        # Password info
        info_frame = ttk.LabelFrame(analysis_frame, text="Password Information", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Length: {len(data['password'])} characters", 
                  font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Crack Time: {estimate_crack_time(data['password'])}", 
                  font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        
        # Character breakdown
        chars_frame = ttk.LabelFrame(analysis_frame, text="Character Breakdown", padding="10")
        chars_frame.pack(fill=tk.X, pady=5)
        
        has_lower = bool(re.search(r"[a-z]", data['password']))
        has_upper = bool(re.search(r"[A-Z]", data['password']))
        has_digit = bool(re.search(r"[0-9]", data['password']))
        has_symbol = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", data['password']))
        
        ttk.Label(chars_frame, text=f"✓ Lowercase: {'Yes' if has_lower else 'No'}", 
                  foreground='#2ecc71' if has_lower else '#e74c3c').pack(anchor=tk.W, pady=2)
        ttk.Label(chars_frame, text=f"✓ Uppercase: {'Yes' if has_upper else 'No'}", 
                  foreground='#2ecc71' if has_upper else '#e74c3c').pack(anchor=tk.W, pady=2)
        ttk.Label(chars_frame, text=f"✓ Numbers: {'Yes' if has_digit else 'No'}", 
                  foreground='#2ecc71' if has_digit else '#e74c3c').pack(anchor=tk.W, pady=2)
        ttk.Label(chars_frame, text=f"✓ Symbols: {'Yes' if has_symbol else 'No'}", 
                  foreground='#2ecc71' if has_symbol else '#e74c3c').pack(anchor=tk.W, pady=2)
        
        # Tab 2: Issues & Fixes
        issues_frame = ttk.Frame(notebook, padding="10")
        notebook.add(issues_frame, text="Issues & Fixes")
        
        if feedback['issues']:
            # Create canvas with scrollbar for many issues
            canvas = tk.Canvas(issues_frame, bg=DarkTheme.bg_dark, highlightthickness=0)
            scrollbar = ttk.Scrollbar(issues_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            for i, issue in enumerate(feedback['issues'], 1):
                issue_card = ttk.LabelFrame(scrollable_frame, text=f"Issue {i}", padding="10")
                issue_card.pack(fill=tk.X, pady=5, padx=5)
                
                ttk.Label(issue_card, text=issue, wraplength=450, font=('Arial', 10)).pack(anchor=tk.W, pady=5)
                
                # Suggest fix based on issue
                if "uppercase" in issue.lower():
                    ttk.Label(issue_card, text="💡 Fix: Add capital letters (A-Z)", 
                              foreground="#3498db").pack(anchor=tk.W)
                elif "lowercase" in issue.lower():
                    ttk.Label(issue_card, text="💡 Fix: Add lowercase letters (a-z)", 
                              foreground="#3498db").pack(anchor=tk.W)
                elif "number" in issue.lower():
                    ttk.Label(issue_card, text="💡 Fix: Add numbers (0-9)", 
                              foreground="#3498db").pack(anchor=tk.W)
                elif "symbol" in issue.lower():
                    ttk.Label(issue_card, text="💡 Fix: Add symbols (!@#$%)", 
                              foreground="#3498db").pack(anchor=tk.W)
                elif "short" in issue.lower():
                    ttk.Label(issue_card, text="💡 Fix: Make password longer (12+ chars)", 
                              foreground="#3498db").pack(anchor=tk.W)
                elif "common" in issue.lower():
                    ttk.Label(issue_card, text="💡 Fix: Avoid common words or patterns", 
                              foreground="#3498db").pack(anchor=tk.W)
                elif "repeated" in issue.lower():
                    ttk.Label(issue_card, text="💡 Fix: Use more unique characters", 
                              foreground="#3498db").pack(anchor=tk.W)
        else:
            ttk.Label(issues_frame, text="✅ No issues found! Great password!", 
                      font=('Arial', 14)).pack(pady=50)
        
        # Tab 3: Suggestions
        suggestions_frame = ttk.Frame(notebook, padding="10")
        notebook.add(suggestions_frame, text="Suggestions")
        
        # Generate suggestions based on password
        ttk.Label(suggestions_frame, text="💡 Improvement Ideas:", 
                  font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=10)
        
        suggestions = []
        if len(data['password']) < 12:
            suggestions.append("• Increase length to 12+ characters for better security")
        if len(data['password']) < 16:
            suggestions.append("• For excellent security, use 16+ characters")
        if not has_upper or not has_lower:
            suggestions.append("• Mix uppercase and lowercase letters")
        if not has_digit:
            suggestions.append("• Add numbers to increase complexity")
        if not has_symbol:
            suggestions.append("• Add symbols (!@#$%) for extra security")
        if len(set(data['password'])) < len(data['password']) * 0.6:
            suggestions.append("• Use more unique characters, avoid repetition")
        
        if suggestions:
            for suggestion in suggestions:
                ttk.Label(suggestions_frame, text=suggestion, 
                         wraplength=500, font=('Arial', 10)).pack(anchor=tk.W, pady=3)
        else:
            ttk.Label(suggestions_frame, text="Your password looks great! No suggestions needed.", 
                     font=('Arial', 11)).pack(pady=20)
        
        # Tab 4: Quick Actions
        actions_frame = ttk.Frame(notebook, padding="10")
        notebook.add(actions_frame, text="Quick Actions")
        
        ttk.Label(actions_frame, text="What would you like to do?", 
                  font=('Arial', 12, 'bold')).pack(pady=10)
        
        action_btn_frame = ttk.Frame(actions_frame)
        action_btn_frame.pack(pady=20)
        
        ttk.Button(action_btn_frame, text="🔄 Generate New Password", 
                  command=lambda: self.suggest_better_password(data['password'], inspector),
                  width=25).pack(pady=5)
        
        ttk.Button(action_btn_frame, text="📋 Copy to Clipboard", 
                  command=lambda: self.copy_password_from_inspector(inspector),
                  width=25).pack(pady=5)
        
        ttk.Button(action_btn_frame, text="✏️ Edit Account", 
                  command=lambda: [inspector.destroy(), self.edit_account()],
                  width=25).pack(pady=5)
        
        # Close button at bottom
        ttk.Button(inspector, text="Close", command=inspector.destroy, width=20).pack(pady=10)
    
    def copy_password_from_inspector(self, inspector):
        """Copy password from inspector window"""
        if self.current_account:
            password = accounts[self.current_account]['password']
            try:
                pyperclip.copy(password)
                self.status_var.set("✓ Password copied to clipboard!")
                messagebox.showinfo("Success", "Password copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy: {str(e)}")
    
    def suggest_better_password(self, current_password, parent_window):
        """Suggest better passwords"""
        suggestions = []
        for _ in range(3):
            suggestions.append(generate_password(16))
        
        # Create suggestion dialog with dark mode
        dialog = tk.Toplevel(parent_window)
        dialog.title("Password Suggestions")
        dialog.geometry("500x400")
        dialog.configure(bg=DarkTheme.bg_dark)
        dialog.transient(parent_window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Try one of these strong passwords:", 
                  font=('Arial', 12, 'bold')).pack(pady=15)
        
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        for i, pwd in enumerate(suggestions):
            pwd_frame = ttk.LabelFrame(frame, text=f"Option {i+1}", padding="10")
            pwd_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(pwd_frame, text=pwd, font=('Courier', 10)).pack(side=tk.LEFT, padx=5)
            ttk.Button(pwd_frame, text="Copy & Use", 
                      command=lambda p=pwd: self.use_suggested_password(p, dialog)).pack(side=tk.RIGHT)
        
        ttk.Button(dialog, text="Cancel", command=dialog.destroy, width=15).pack(pady=15)
    
    def use_suggested_password(self, password, dialog):
        """Use a suggested password"""
        try:
            pyperclip.copy(password)
            dialog.destroy()
            
            result = messagebox.askyesno(
                "Use This Password?",
                f"Password copied to clipboard!\n\nPassword: {password}\n\n" +
                "Would you like to update the current account with this password?"
            )
            
            if result and self.current_account:
                accounts[self.current_account]['password'] = password
                accounts[self.current_account]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_accounts()
                self.display_account_details(self.current_account)
                self.status_var.set("✓ Password updated!")
                messagebox.showinfo("Success", "Account updated with new password!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
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
        dialog.geometry("550x600")
        dialog.configure(bg=DarkTheme.bg_dark)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Add New Account", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Main frame with scrollbar for better UX
        canvas = tk.Canvas(dialog, bg=DarkTheme.bg_dark, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        frame = ttk.Frame(scrollable_frame, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nickname
        ttk.Label(frame, text="Nickname:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        nickname_var = tk.StringVar()
        nickname_entry = ttk.Entry(frame, textvariable=nickname_var, width=35, font=('Arial', 10))
        nickname_entry.grid(row=0, column=1, pady=8, padx=10)
        
        # App name
        ttk.Label(frame, text="App Name:", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        app_var = tk.StringVar()
        app_entry = ttk.Entry(frame, textvariable=app_var, width=35, font=('Arial', 10))
        app_entry.grid(row=1, column=1, pady=8, padx=10)
        
        # Category
        ttk.Label(frame, text="Category:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        category_var = tk.StringVar(value="Personal")
        category_combo = ttk.Combobox(frame, textvariable=category_var,
                                       values=["Academic", "Personal", "Internship", "Other"],
                                       state="readonly", width=32, font=('Arial', 10))
        category_combo.grid(row=2, column=1, pady=8, padx=10)
        
        # Password
        ttk.Label(frame, text="Password:", font=('Arial', 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        
        password_frame = ttk.Frame(frame)
        password_frame.grid(row=3, column=1, pady=8, padx=10, sticky=tk.W)
        
        password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=password_var, width=25, show="•", font=('Arial', 10))
        password_entry.pack(side=tk.LEFT)
        
        # Generate button
        def generate_and_set():
            pwd = generate_password()
            password_var.set(pwd)
            password_entry.config(show="")
            show_pwd_var.set(True)
            update_strength()
        
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
        
        # Live strength meter for new password
        strength_preview_frame = ttk.LabelFrame(frame, text="Password Strength Preview", padding="10")
        strength_preview_frame.grid(row=5, column=0, columnspan=2, pady=15, sticky=tk.EW)
        
        preview_bar = ttk.Progressbar(strength_preview_frame, length=350, mode='determinate')
        preview_bar.pack(pady=5)
        
        preview_label = ttk.Label(strength_preview_frame, text="", font=('Arial', 10, 'bold'))
        preview_label.pack()
        
        preview_crack = ttk.Label(strength_preview_frame, text="", font=('Arial', 8))
        preview_crack.pack()
        
        def update_strength(*args):
            pwd = password_var.get()
            if pwd:
                feedback = get_password_feedback(pwd)
                preview_bar['value'] = (feedback['score'] / 10) * 100
                preview_label.config(text=f"{feedback['category']} ({feedback['score']:.1f}/10)", 
                                    foreground=DarkTheme.strength_colors.get(feedback['category'], DarkTheme.fg_light))
                crack_time = estimate_crack_time(pwd)
                preview_crack.config(text=f"⏱️ Crack time: {crack_time}")
            else:
                preview_bar['value'] = 0
                preview_label.config(text="Enter a password")
                preview_crack.config(text="")
        
        # Trace password changes
        password_var.trace('w', update_strength)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
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
                    existing_nick != nickname):
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
        
        ttk.Button(button_frame, text="Save", command=save_account, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)
        
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
        edit_window.geometry("550x600")
        edit_window.configure(bg=DarkTheme.bg_dark)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Get current data
        current_data = accounts[self.current_account]
        
        ttk.Label(edit_window, text="Edit Account", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Main frame with scrollbar
        canvas = tk.Canvas(edit_window, bg=DarkTheme.bg_dark, highlightthickness=0)
        scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        frame = ttk.Frame(scrollable_frame, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nickname (read-only)
        ttk.Label(frame, text="Nickname:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        ttk.Label(frame, text=self.current_account, font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky=tk.W, pady=8, padx=10)
        
        # App name
        ttk.Label(frame, text="App Name:", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        app_var = tk.StringVar(value=current_data['app'])
        app_entry = ttk.Entry(frame, textvariable=app_var, width=35, font=('Arial', 10))
        app_entry.grid(row=1, column=1, pady=8, padx=10)
        
        # Category
        ttk.Label(frame, text="Category:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        category_var = tk.StringVar(value=current_data['category'])
        category_combo = ttk.Combobox(frame, textvariable=category_var,
                                       values=["Academic", "Personal", "Internship", "Other"],
                                       state="readonly", width=32, font=('Arial', 10))
        category_combo.grid(row=2, column=1, pady=8, padx=10)
        
        # Password
        ttk.Label(frame, text="Password:", font=('Arial', 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        
        password_frame = ttk.Frame(frame)
        password_frame.grid(row=3, column=1, pady=8, padx=10, sticky=tk.W)
        
        password_var = tk.StringVar(value=current_data['password'])
        password_entry = ttk.Entry(password_frame, textvariable=password_var, width=25, show="•", font=('Arial', 10))
        password_entry.pack(side=tk.LEFT)
        
        def generate_and_set():
            pwd = generate_password()
            password_var.set(pwd)
            password_entry.config(show="")
            show_pwd_var.set(True)
            update_strength()
        
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
        
        # Live strength meter
        strength_preview_frame = ttk.LabelFrame(frame, text="Password Strength Preview", padding="10")
        strength_preview_frame.grid(row=5, column=0, columnspan=2, pady=15, sticky=tk.EW)
        
        preview_bar = ttk.Progressbar(strength_preview_frame, length=350, mode='determinate')
        preview_bar.pack(pady=5)
        
        preview_label = ttk.Label(strength_preview_frame, text="", font=('Arial', 10, 'bold'))
        preview_label.pack()
        
        preview_crack = ttk.Label(strength_preview_frame, text="", font=('Arial', 8))
        preview_crack.pack()
        
        def update_strength(*args):
            pwd = password_var.get()
            if pwd:
                feedback = get_password_feedback(pwd)
                preview_bar['value'] = (feedback['score'] / 10) * 100
                preview_label.config(text=f"{feedback['category']} ({feedback['score']:.1f}/10)", 
                                    foreground=DarkTheme.strength_colors.get(feedback['category'], DarkTheme.fg_light))
                crack_time = estimate_crack_time(pwd)
                preview_crack.config(text=f"⏱️ Crack time: {crack_time}")
            else:
                preview_bar['value'] = 0
                preview_label.config(text="Enter a password")
                preview_crack.config(text="")
        
        # Initial update
        update_strength()
        password_var.trace('w', update_strength)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
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
        
        ttk.Button(button_frame, text="Save", command=save_changes, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy, width=15).pack(side=tk.LEFT, padx=10)
    
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
            self.toggle_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            
            # Reset strength displays
            self.strength_bar['value'] = 0
            self.strength_label.config(text="")
            self.crack_time_label.config(text="")
            
            self.strengths_list.config(state=tk.NORMAL)
            self.strengths_list.delete(1.0, tk.END)
            self.strengths_list.config(state=tk.DISABLED)
            
            self.issues_list.config(state=tk.NORMAL)
            self.issues_list.delete(1.0, tk.END)
            self.issues_list.config(state=tk.DISABLED)
            
            self.status_var.set("✓ Account deleted")
    
    def show_password_reuse(self):
        """Show password reuse report in a new window"""
        reused = detect_password_reuse()
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Password Reuse Report")
        report_window.geometry("650x550")
        report_window.configure(bg=DarkTheme.bg_dark)
        report_window.transient(self.root)
        
        ttk.Label(report_window, text="Password Reuse Report", font=('Arial', 16, 'bold')).pack(pady=10)
        
        if not reused:
            ttk.Label(report_window, text="✅ No password reuse detected!", font=('Arial', 12)).pack(pady=30)
        else:
            # Create text widget with scrollbar
            frame = ttk.Frame(report_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(frame, yscrollcommand=scrollbar.set, wrap=tk.WORD, font=('Courier', 10),
                                  bg=DarkTheme.bg_medium, fg=DarkTheme.fg_light,
                                  bd=1, relief=tk.SUNKEN)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=text_widget.yview)
            
            # Add content
            text_widget.insert(tk.END, f"⚠️ Found {len(reused)} reused password(s):\n\n")
            
            for i, item in enumerate(reused, 1):
                text_widget.insert(tk.END, f"\n{i}. Password: {item['password']}\n")
                text_widget.insert(tk.END, f"   Used in {item['count']} accounts:\n")
                for acc in item['accounts']:
                    # Get strength for each account
                    feedback = get_password_feedback(accounts[acc]['password'])
                    text_widget.insert(tk.END, f"   • {acc} ({accounts[acc]['app']}) - {feedback['category']}\n")
                text_widget.insert(tk.END, "\n" + "─"*50 + "\n")
            
            text_widget.config(state=tk.DISABLED)
        
        ttk.Button(report_window, text="Close", command=report_window.destroy, width=20).pack(pady=20)
    
    def show_password_generator(self):
        """Show password generator tool"""
        pwd = generate_password(24)  # Generate an extra strong password
        feedback = get_password_feedback(pwd)
        
        result = messagebox.askyesno(
            "Password Generator",
            f"🔐 Generated Password:\n\n{pwd}\n\n" +
            f"Strength: {feedback['category']} ({feedback['score']:.1f}/10)\n" +
            f"⏱️ Crack time: {estimate_crack_time(pwd)}\n\n" +
            f"Copy to clipboard?"
        )
        
        if result:
            try:
                pyperclip.copy(pwd)
                self.status_var.set("✓ Password copied to clipboard!")
                messagebox.showinfo("Success", "Password copied to clipboard!")
            except Exception as e:
                self.status_var.set(f"❌ Copy failed: {str(e)}")
                messagebox.showerror("Error", f"Failed to copy password: {str(e)}")
    
    def show_password_health(self):
        """Show overall password health dashboard"""
        if not accounts:
            messagebox.showinfo("Password Health", "No accounts to analyze.")
            return
        
        health_window = tk.Toplevel(self.root)
        health_window.title("Password Health Dashboard")
        health_window.geometry("650x550")
        health_window.configure(bg=DarkTheme.bg_dark)
        health_window.transient(self.root)
        
        ttk.Label(health_window, text="Password Health Dashboard", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Calculate statistics
        total = len(accounts)
        scores = []
        categories = []
        
        for data in accounts.values():
            feedback = get_password_feedback(data['password'])
            scores.append(feedback['score'])
            categories.append(feedback['category'])
        
        avg_score = sum(scores) / total if total > 0 else 0
        
        # Category counts
        cat_counts = {
            "Excellent": categories.count("Excellent"),
            "Very Strong": categories.count("Very Strong"),
            "Strong": categories.count("Strong"),
            "Good": categories.count("Good"),
            "Fair": categories.count("Fair"),
            "Weak": categories.count("Weak"),
            "Very Weak": categories.count("Very Weak")
        }
        
        # Create stats frame
        stats_frame = ttk.LabelFrame(health_window, text="Statistics", padding="15")
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(stats_frame, text=f"Total Accounts: {total}", font=('Arial', 11)).pack(anchor=tk.W, pady=2)
        ttk.Label(stats_frame, text=f"Average Strength: {avg_score:.1f}/10", font=('Arial', 11)).pack(anchor=tk.W, pady=2)
        
        # Create breakdown frame
        breakdown_frame = ttk.LabelFrame(health_window, text="Strength Breakdown", padding="15")
        breakdown_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create a canvas for scrolling if needed
        canvas = tk.Canvas(breakdown_frame, bg=DarkTheme.bg_dark, highlightthickness=0)
        scrollbar = ttk.Scrollbar(breakdown_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add strength categories
        colors = {
            "Excellent": "#2ecc71",
            "Very Strong": "#27ae60",
            "Strong": "#3498db",
            "Good": "#f39c12",
            "Fair": "#f1c40f",
            "Weak": "#e67e22",
            "Very Weak": "#e74c3c"
        }
        
        for cat, count in cat_counts.items():
            if count > 0:
                frame = ttk.Frame(scrollable_frame)
                frame.pack(fill=tk.X, pady=5)
                
                color_box = tk.Canvas(frame, width=20, height=20, bg=colors[cat], highlightthickness=0)
                color_box.pack(side=tk.LEFT, padx=5)
                
                ttk.Label(frame, text=f"{cat}: {count} account(s)", font=('Arial', 10)).pack(side=tk.LEFT)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(health_window, text="Close", command=health_window.destroy, width=20).pack(pady=20)
    
    def show_about(self):
        """Show about dialog"""
        about_text = "🔐 GateKeeper Password Manager\n\n"
        about_text += "Version 2.5.0\n\n"
        about_text += "Your personal password manager\n"
        about_text += "Securely store and manage all your accounts\n\n"
        about_text += "✨ Features:\n"
        about_text += "• Advanced password strength analysis (0-10 scale)\n"
        about_text += "• Password Inspector with actionable tips\n"
        about_text += "• Crack time estimation\n"
        about_text += "• Password reuse detection\n"
        about_text += "• Health dashboard\n"
        about_text += "• Built-in password generator\n"
        about_text += "• Dark mode for comfortable viewing\n\n"
        about_text += "© 2026 GateKeeper Team\n"
        about_text += "AI tools used responsibly to support learning"
        
        messagebox.showinfo("About GateKeeper", about_text)
    
    def show_storage_warning(self):
        """Show storage warning"""
        warning_text = "⚠️ LOCAL STORAGE ONLY ⚠️\n\n"
        warning_text += "Your accounts are saved ONLY on this device.\n"
        warning_text += "If you delete this program or its files,\n"
        warning_text += "ALL your saved accounts will be PERMANENTLY LOST.\n\n"
        warning_text += "📁 Location: " + os.path.abspath(FILENAME) + "\n\n"
        warning_text += "💾 To backup: Copy the accounts.json file to a safe location."
        
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
