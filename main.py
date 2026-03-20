#AI tools were used responsibly to support learning and development, not to replace understanding.

import json
import os
import random
import string
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont

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
    """Generate a strong random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
    
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        score, _ = check_password_strength(password)
        if score >= 8:
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
# MODERN MINIMALIST THEME
# ============================================================================

class ModernTheme:
    # Color palette - clean and minimal
    bg_primary = "#ffffff"           # Pure white background
    bg_secondary = "#f8f9fa"         # Light gray for cards
    bg_tertiary = "#e9ecef"          # Slightly darker gray for hover
    accent = "#4361ee"                # Vibrant blue for primary actions
    accent_light = "#4895ef"          # Lighter blue for hover
    accent_success = "#06d6a0"        # Teal for success
    accent_warning = "#ff9e00"         # Orange for warnings
    accent_danger = "#ef476f"          # Pink/red for danger
    text_primary = "#212529"           # Almost black for primary text
    text_secondary = "#6c757d"         # Gray for secondary text
    text_light = "#adb5bd"              # Light gray for disabled
    border = "#dee2e6"                  # Light gray borders
    card_shadow = "#00000010"            # Subtle shadow
    
    # Fonts - clean, modern, professional
    heading_font = ("Segoe UI", 16, "bold")
    subheading_font = ("Segoe UI", 12, "bold")
    body_font = ("Segoe UI", 10)
    small_font = ("Segoe UI", 9)
    monospace_font = ("Consolas", 10) if os.name == 'nt' else ("Menlo", 10)
    
    # Strength colors
    strength_colors = {
        "Excellent": "#06d6a0",
        "Very Strong": "#1b9e5c",
        "Strong": "#4361ee",
        "Good": "#ff9e00",
        "Fair": "#f9c74f",
        "Weak": "#f9844a",
        "Very Weak": "#ef476f"
    }

# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class ModernButton(tk.Canvas):
    """Custom modern button with hover effects"""
    def __init__(self, master, text, command=None, bg=ModernTheme.accent, fg="white", 
                 width=120, height=35, corner_radius=8, font=ModernTheme.body_font, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=ModernTheme.bg_primary)
        self.command = command
        self.text = text
        self.bg = bg
        self.fg = fg
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.font = font
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw_button(self.bg)
    
    def draw_button(self, color):
        self.delete("all")
        # Rounded rectangle
        self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius, fill=color, outline="")
        # Text
        self.create_text(self.width//2, self.height//2, text=self.text, fill=self.fg, font=self.font)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        self.draw_button(self.lighten_color(self.bg))
    
    def on_leave(self, event):
        self.draw_button(self.bg)
    
    def on_click(self, event):
        if self.command:
            self.command()
    
    def lighten_color(self, color):
        """Lighten a hex color for hover effect"""
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = min(255, r + 20)
            g = min(255, g + 20)
            b = min(255, b + 20)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

class ModernEntry(ttk.Entry):
    """Styled entry widget"""
    def __init__(self, master, **kwargs):
        super().__init__(master, font=ModernTheme.body_font, **kwargs)
        style = ttk.Style()
        style.configure("Modern.TEntry", 
                       fieldbackground="white",
                       bordercolor=ModernTheme.border,
                       lightcolor=ModernTheme.border,
                       darkcolor=ModernTheme.border,
                       borderwidth=1,
                       relief="solid",
                       padding=5)
        self.configure(style="Modern.TEntry")

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class GateKeeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GateKeeper")
        self.root.geometry("1200x700")
        self.root.configure(bg=ModernTheme.bg_primary)
        
        # Center the window
        self.center_window()
        
        # Password visibility toggle
        self.show_passwords = False
        
        # Current selected account
        self.current_account = None
        
        self.setup_styles()
        self.setup_menu()
        self.setup_ui()
        self.show_intro()
        self.refresh_list()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('.', 
                       background=ModernTheme.bg_primary,
                       foreground=ModernTheme.text_primary,
                       fieldbackground="white",
                       troughcolor=ModernTheme.bg_secondary,
                       selectbackground=ModernTheme.accent_light,
                       selectforeground="white")
        
        style.configure('TLabel', 
                       background=ModernTheme.bg_primary, 
                       foreground=ModernTheme.text_primary,
                       font=ModernTheme.body_font)
        
        style.configure('Heading.TLabel', 
                       font=ModernTheme.heading_font,
                       foreground=ModernTheme.text_primary)
        
        style.configure('Subheading.TLabel', 
                       font=ModernTheme.subheading_font,
                       foreground=ModernTheme.text_primary)
        
        style.configure('TFrame', background=ModernTheme.bg_primary)
        style.configure('Card.TFrame', 
                       background=ModernTheme.bg_secondary,
                       relief="solid",
                       borderwidth=1,
                       bordercolor=ModernTheme.border)
        
        style.configure('TLabelframe', 
                       background=ModernTheme.bg_primary,
                       foreground=ModernTheme.text_primary,
                       bordercolor=ModernTheme.border,
                       lightcolor=ModernTheme.border,
                       darkcolor=ModernTheme.border)
        
        style.configure('TLabelframe.Label', 
                       background=ModernTheme.bg_primary,
                       foreground=ModernTheme.text_primary,
                       font=ModernTheme.subheading_font)
        
        style.configure('TEntry', 
                       fieldbackground="white",
                       bordercolor=ModernTheme.border,
                       borderwidth=1,
                       padding=5)
        
        style.configure('TCombobox', 
                       fieldbackground="white",
                       bordercolor=ModernTheme.border,
                       borderwidth=1,
                       padding=5)
        
        style.configure('TScrollbar',
                       background=ModernTheme.bg_tertiary,
                       troughcolor=ModernTheme.bg_secondary,
                       arrowcolor=ModernTheme.text_primary,
                       borderwidth=0)
        
        style.configure('TProgressbar',
                       background=ModernTheme.accent,
                       troughcolor=ModernTheme.bg_secondary,
                       borderwidth=0)
        
        style.configure('TMenubar', 
                       background=ModernTheme.bg_primary,
                       foreground=ModernTheme.text_primary)
        
        style.configure('TMenu', 
                       background=ModernTheme.bg_secondary,
                       foreground=ModernTheme.text_primary,
                       borderwidth=0)
        
        style.map('TMenu',
                 background=[('active', ModernTheme.accent_light)],
                 foreground=[('active', 'white')])
    
    def setup_menu(self):
        """Create minimal menu bar"""
        menubar = tk.Menu(self.root, bg=ModernTheme.bg_primary, fg=ModernTheme.text_primary,
                         activebackground=ModernTheme.accent_light, activeforeground="white",
                         borderwidth=0, relief="flat")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.bg_secondary, fg=ModernTheme.text_primary,
                           activebackground=ModernTheme.accent_light, activeforeground="white",
                           borderwidth=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Account", command=self.add_account_dialog, accelerator="⌘N")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.bg_secondary, fg=ModernTheme.text_primary,
                           activebackground=ModernTheme.accent_light, activeforeground="white",
                           borderwidth=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_list)
        view_menu.add_separator()
        view_menu.add_command(label="All Accounts", command=lambda: self.set_category_filter("All"))
        view_menu.add_command(label="Academic", command=lambda: self.set_category_filter("Academic"))
        view_menu.add_command(label="Personal", command=lambda: self.set_category_filter("Personal"))
        view_menu.add_command(label="Internship", command=lambda: self.set_category_filter("Internship"))
        view_menu.add_command(label="Other", command=lambda: self.set_category_filter("Other"))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.bg_secondary, fg=ModernTheme.text_primary,
                            activebackground=ModernTheme.accent_light, activeforeground="white",
                            borderwidth=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Password Reuse Report", command=self.show_password_reuse)
        tools_menu.add_command(label="Generate Password", command=self.show_password_generator)
        tools_menu.add_command(label="Health Dashboard", command=self.show_password_health)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=ModernTheme.bg_secondary, fg=ModernTheme.text_primary,
                           activebackground=ModernTheme.accent_light, activeforeground="white",
                           borderwidth=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Storage Warning", command=self.show_storage_warning)
        
        # Keyboard shortcuts
        self.root.bind('<Command-n>', lambda e: self.add_account_dialog())
        self.root.bind('<Control-n>', lambda e: self.add_account_dialog())
    
    def setup_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ====================================================================
        # HEADER SECTION
        # ====================================================================
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo/Title
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text="GateKeeper", font=("Segoe UI", 24, "bold"), 
                 foreground=ModernTheme.accent).pack(anchor=tk.W)
        ttk.Label(title_frame, text="password manager", font=("Segoe UI", 10), 
                 foreground=ModernTheme.text_secondary).pack(anchor=tk.W)
        
        # Stats card
        stats_card = ttk.Frame(header_frame, style='Card.TFrame', padding="15")
        stats_card.pack(side=tk.RIGHT)
        
        self.stats_label = ttk.Label(stats_card, text="0 accounts", font=ModernTheme.subheading_font,
                                     foreground=ModernTheme.text_primary)
        self.stats_label.pack()
        
        # Warning banner
        warning_frame = ttk.Frame(main_container, style='Card.TFrame', padding="10")
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.warning_text = tk.Text(warning_frame, height=1, font=ModernTheme.small_font,
                                    bg=ModernTheme.bg_secondary, fg=ModernTheme.accent_warning,
                                    wrap=tk.WORD, bd=0, highlightthickness=0)
        self.warning_text.pack(fill=tk.X)
        self.warning_text.insert(1.0, "⚠️  Local storage only — accounts saved on this device")
        self.warning_text.config(state=tk.DISABLED)
        
        # ====================================================================
        # SEARCH AND FILTER SECTION
        # ====================================================================
        search_frame = ttk.Frame(main_container)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Search bar with icon
        search_container = ttk.Frame(search_frame)
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_container, text="🔍", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_list)
        search_entry = ModernEntry(search_container, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Category filter
        category_container = ttk.Frame(search_frame)
        category_container.pack(side=tk.RIGHT, padx=(20, 0))
        
        ttk.Label(category_container, text="Category:", font=ModernTheme.body_font,
                 foreground=ModernTheme.text_secondary).pack(side=tk.LEFT, padx=(0, 10))
        
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(category_container, textvariable=self.category_var,
                                       values=["All", "Academic", "Personal", "Internship", "Other"],
                                       state="readonly", width=15, font=ModernTheme.body_font)
        category_combo.pack(side=tk.LEFT)
        category_combo.bind('<<ComboboxSelected>>', self.filter_list)
        
        # ====================================================================
        # MAIN CONTENT - Two column layout
        # ====================================================================
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Accounts list
        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Section header with add button
        left_header = ttk.Frame(left_column)
        left_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left_header, text="Your Accounts", font=ModernTheme.subheading_font).pack(side=tk.LEFT)
        
        add_btn = ModernButton(left_header, text="+ New", command=self.add_account_dialog,
                               bg=ModernTheme.accent, width=80, height=30, corner_radius=6)
        add_btn.pack(side=tk.RIGHT)
        
        # Accounts list with custom styling
        list_container = ttk.Frame(left_column, style='Card.TFrame')
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a custom listbox with modern styling
        list_frame = ttk.Frame(list_container)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.accounts_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                        font=ModernTheme.monospace_font,
                                        bg="white", fg=ModernTheme.text_primary,
                                        selectbackground=ModernTheme.accent_light,
                                        selectforeground="white",
                                        bd=0, highlightthickness=0,
                                        activestyle="none",
                                        relief="flat")
        self.accounts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.accounts_list.bind('<<ListboxSelect>>', self.on_account_select)
        self.accounts_list.bind('<Double-Button-1>', lambda e: self.inspect_password())
        
        scrollbar.config(command=self.accounts_list.yview)
        
        # Right column - Details and actions
        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Details card
        details_card = ttk.Frame(right_column, style='Card.TFrame', padding="15")
        details_card.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(details_card, text="Account Details", font=ModernTheme.subheading_font).pack(anchor=tk.W, pady=(0, 10))
        
        # Details text
        details_container = ttk.Frame(details_card)
        details_container.pack(fill=tk.BOTH, expand=True)
        
        details_scrollbar = ttk.Scrollbar(details_container)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = tk.Text(details_container, yscrollcommand=details_scrollbar.set,
                                    height=8, font=ModernTheme.monospace_font,
                                    bg="white", fg=ModernTheme.text_primary,
                                    bd=0, highlightthickness=0,
                                    relief="flat", padx=10, pady=10)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.details_text.config(state=tk.DISABLED)
        
        details_scrollbar.config(command=self.details_text.yview)
        
        # Strength meter
        strength_frame = ttk.Frame(details_card)
        strength_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(strength_frame, text="Password Strength", font=ModernTheme.small_font,
                 foreground=ModernTheme.text_secondary).pack(anchor=tk.W)
        
        meter_frame = ttk.Frame(strength_frame)
        meter_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.strength_bar = ttk.Progressbar(meter_frame, length=200, mode='determinate')
        self.strength_bar.pack(side=tk.LEFT)
        
        self.strength_label = ttk.Label(meter_frame, text="", font=ModernTheme.body_font)
        self.strength_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.crack_time_label = ttk.Label(strength_frame, text="", font=ModernTheme.small_font,
                                         foreground=ModernTheme.text_secondary)
        self.crack_time_label.pack(anchor=tk.W, pady=(5, 0))
        
        # ====================================================================
        # ACTION BUTTONS - Minimal and clean
        # ====================================================================
        actions_card = ttk.Frame(right_column, style='Card.TFrame', padding="15")
        actions_card.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(actions_card, text="Actions", font=ModernTheme.subheading_font).pack(anchor=tk.W, pady=(0, 10))
        
        # Button grid
        button_grid = ttk.Frame(actions_card)
        button_grid.pack(fill=tk.X)
        
        # Row 1
        row1 = ttk.Frame(button_grid)
        row1.pack(fill=tk.X, pady=2)
        
        self.inspect_btn = ModernButton(row1, text="🔍 Inspect", command=self.inspect_password,
                                        bg=ModernTheme.accent, width=100, height=32)
        self.inspect_btn.pack(side=tk.LEFT, padx=2)
        
        self.copy_btn = ModernButton(row1, text="📋 Copy", command=self.copy_password,
                                     bg=ModernTheme.accent_success, width=100, height=32)
        self.copy_btn.pack(side=tk.LEFT, padx=2)
        
        # Row 2
        row2 = ttk.Frame(button_grid)
        row2.pack(fill=tk.X, pady=2)
        
        self.toggle_btn = ModernButton(row2, text="👁️ Show", command=self.toggle_password,
                                       bg=ModernTheme.text_secondary, width=100, height=32, state=tk.DISABLED)
        self.toggle_btn.pack(side=tk.LEFT, padx=2)
        
        self.edit_btn = ModernButton(row2, text="✏️ Edit", command=self.edit_account,
                                     bg=ModernTheme.accent_warning, width=100, height=32, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Row 3
        row3 = ttk.Frame(button_grid)
        row3.pack(fill=tk.X, pady=2)
        
        self.delete_btn = ModernButton(row3, text="🗑️ Delete", command=self.delete_account,
                                       bg=ModernTheme.accent_danger, width=204, height=32, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Tip of the day
        tip_card = ttk.Frame(right_column, style='Card.TFrame', padding="10")
        tip_card.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(tip_card, text="💡 Tip", font=ModernTheme.small_font,
                 foreground=ModernTheme.text_secondary).pack(anchor=tk.W)
        
        self.tip_label = ttk.Label(tip_card, text="", font=ModernTheme.small_font,
                                   wraplength=300, justify=tk.LEFT)
        self.tip_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Status bar
        status_bar = ttk.Frame(self.root, style='Card.TFrame', padding="5")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(status_bar, textvariable=self.status_var, font=ModernTheme.small_font,
                 foreground=ModernTheme.text_secondary).pack(side=tk.LEFT)
    
    def show_intro(self):
        """Show introduction information"""
        account_count = len(accounts)
        self.stats_label.config(text=f"{account_count} accounts")
        
        reused = detect_password_reuse()
        if reused:
            self.status_var.set(f"⚠️ {len(reused)} reused passwords detected")
        
        tips = [
            "Use 16+ characters for excellent security",
            "Mix uppercase, lowercase, numbers, and symbols",
            "Never reuse passwords across accounts",
            "Longer passwords are stronger than complex short ones",
            "Double-click an account to inspect it",
            "Check Tools > Health Dashboard for overview"
        ]
        self.tip_label.config(text=random.choice(tips))
    
    def set_category_filter(self, category):
        self.category_var.set(category)
        self.filter_list()
    
    def refresh_list(self):
        self.accounts_list.delete(0, tk.END)
        sorted_nicknames = sorted(accounts.keys())
        
        for nickname in sorted_nicknames:
            data = accounts[nickname]
            display_text = f"{nickname} — {data['app']}  [{data['category']}]"
            self.accounts_list.insert(tk.END, display_text)
        
        self.show_intro()
    
    def filter_list(self, *args):
        search_term = self.search_var.get().lower()
        category_filter = self.category_var.get()
        
        self.accounts_list.delete(0, tk.END)
        sorted_nicknames = sorted(accounts.keys())
        
        for nickname in sorted_nicknames:
            data = accounts[nickname]
            
            if category_filter != "All":
                if category_filter == "Other":
                    if data['category'].lower() in ["academic", "personal", "internship"]:
                        continue
                elif data['category'] != category_filter:
                    continue
            
            if search_term:
                if (search_term not in nickname.lower() and 
                    search_term not in data['app'].lower()):
                    continue
            
            display_text = f"{nickname} — {data['app']}  [{data['category']}]"
            self.accounts_list.insert(tk.END, display_text)
    
    def on_account_select(self, event):
        selection = self.accounts_list.curselection()
        if not selection:
            return
        
        display_text = self.accounts_list.get(selection[0])
        nickname = display_text.split(" — ")[0]
        
        if nickname in accounts:
            self.current_account = nickname
            self.display_account_details(nickname)
            
            # Enable buttons
            self.toggle_btn.configure(state=tk.NORMAL)
            self.edit_btn.configure(state=tk.NORMAL)
            self.delete_btn.configure(state=tk.NORMAL)
    
    def display_account_details(self, nickname):
        data = accounts[nickname]
        
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
        
        feedback = get_password_feedback(data['password'])
        
        self.strength_bar['value'] = (feedback['score'] / 10) * 100
        self.strength_label.config(text=f"{feedback['category']}",
                                   foreground=ModernTheme.strength_colors.get(feedback['category'], ModernTheme.text_primary))
        
        crack_time = estimate_crack_time(data['password'])
        self.crack_time_label.config(text=f"⏱️  {crack_time} to crack")
        
        if self.show_passwords:
            self.toggle_btn.configure(text="👁️ Hide")
        else:
            self.toggle_btn.configure(text="👁️ Show")
    
    def toggle_password(self):
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        if not self.show_passwords:
            result = messagebox.askyesno(
                "Security Confirmation",
                "Reveal this password?\n\nMake sure no one is looking at your screen."
            )
            if result:
                self.show_passwords = True
            else:
                return
        else:
            self.show_passwords = False
        
        if self.current_account:
            self.display_account_details(self.current_account)
    
    def copy_password(self):
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        if not self.show_passwords:
            messagebox.showwarning(
                "Password Hidden", 
                "Click 'Show' first to reveal the password before copying."
            )
            return
        
        password = accounts[self.current_account]['password']
        try:
            pyperclip.copy(password)
            self.status_var.set("✓ Password copied")
            messagebox.showinfo("Success", "Password copied to clipboard!")
        except Exception as e:
            self.status_var.set("✗ Copy failed")
            messagebox.showerror("Error", f"Failed to copy: {str(e)}")
    
    def inspect_password(self):
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        data = accounts[self.current_account]
        feedback = get_password_feedback(data['password'])
        
        inspector = tk.Toplevel(self.root)
        inspector.title(f"Inspector — {self.current_account}")
        inspector.geometry("500x600")
        inspector.configure(bg=ModernTheme.bg_primary)
        inspector.transient(self.root)
        inspector.grab_set()
        
        # Modern inspector window
        main_frame = ttk.Frame(inspector, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with score
        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 20))
        
        score_color = ModernTheme.strength_colors.get(feedback['category'], ModernTheme.accent)
        score_label = tk.Label(header, text=f"{feedback['score']:.1f}", 
                               font=("Segoe UI", 36, "bold"), fg=score_color, bg=ModernTheme.bg_primary)
        score_label.pack(side=tk.LEFT, padx=(0, 20))
        
        info = ttk.Frame(header)
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(info, text=feedback['category'], font=("Segoe UI", 16, "bold"),
                 foreground=score_color).pack(anchor=tk.W)
        ttk.Label(info, text=f"Length: {len(data['password'])} chars", 
                 font=ModernTheme.small_font).pack(anchor=tk.W)
        
        # Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Analysis tab
        analysis = ttk.Frame(notebook, padding="15")
        notebook.add(analysis, text="Analysis")
        
        ttk.Label(analysis, text="Character Types", font=ModernTheme.subheading_font).pack(anchor=tk.W, pady=(0, 10))
        
        has_lower = bool(re.search(r"[a-z]", data['password']))
        has_upper = bool(re.search(r"[A-Z]", data['password']))
        has_digit = bool(re.search(r"[0-9]", data['password']))
        has_symbol = bool(re.search(r"[!@#$%^&*()]", data['password']))
        
        types = [
            ("Lowercase", has_lower),
            ("Uppercase", has_upper),
            ("Numbers", has_digit),
            ("Symbols", has_symbol)
        ]
        
        for label, present in types:
            f = ttk.Frame(analysis)
            f.pack(fill=tk.X, pady=2)
            ttk.Label(f, text=label, width=10).pack(side=tk.LEFT)
            status = "✓" if present else "✗"
            color = ModernTheme.accent_success if present else ModernTheme.accent_danger
            ttk.Label(f, text=status, foreground=color).pack(side=tk.LEFT)
        
        # Issues tab
        issues_tab = ttk.Frame(notebook, padding="15")
        notebook.add(issues_tab, text="Issues")
        
        if feedback['issues']:
            for issue in feedback['issues']:
                frame = ttk.Frame(issues_tab)
                frame.pack(fill=tk.X, pady=2)
                ttk.Label(frame, text="•", foreground=ModernTheme.accent_danger).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(frame, text=issue, wraplength=350).pack(side=tk.LEFT)
        else:
            ttk.Label(issues_tab, text="No issues found", foreground=ModernTheme.accent_success).pack()
        
        # Close button
        ttk.Button(main_frame, text="Close", command=inspector.destroy).pack(pady=20)
    
    def add_account_dialog(self):
        """Open dialog to add a new account"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Account")
        dialog.geometry("450x500")
        dialog.configure(bg=ModernTheme.bg_primary)
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="New Account", font=("Segoe UI", 16, "bold"),
                 foreground=ModernTheme.accent).pack(anchor=tk.W, pady=(0, 20))
        
        # Form fields
        fields = [
            ("Nickname", "nickname_var"),
            ("App Name", "app_var"),
            ("Category", "category_var")
        ]
        
        nickname_var = tk.StringVar()
        app_var = tk.StringVar()
        category_var = tk.StringVar(value="Personal")
        password_var = tk.StringVar()
        
        for i, (label, var_name) in enumerate(fields):
            ttk.Label(main_frame, text=label, font=ModernTheme.small_font,
                     foreground=ModernTheme.text_secondary).pack(anchor=tk.W, pady=(10, 2))
            
            if label == "Category":
                combo = ttk.Combobox(main_frame, textvariable=category_var,
                                     values=["Academic", "Personal", "Internship", "Other"],
                                     state="readonly", font=ModernTheme.body_font)
                combo.pack(fill=tk.X)
            else:
                entry = ModernEntry(main_frame, textvariable=locals()[var_name])
                entry.pack(fill=tk.X)
        
        # Password field
        ttk.Label(main_frame, text="Password", font=ModernTheme.small_font,
                 foreground=ModernTheme.text_secondary).pack(anchor=tk.W, pady=(10, 2))
        
        pwd_frame = ttk.Frame(main_frame)
        pwd_frame.pack(fill=tk.X)
        
        password_entry = ModernEntry(pwd_frame, textvariable=password_var, show="•")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(pwd_frame, text="Generate", command=lambda: password_var.set(generate_password()),
                  width=10).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save():
            nickname = nickname_var.get().strip()
            app = app_var.get().strip()
            category = category_var.get()
            password = password_var.get().strip()
            
            if not nickname or not app or not password:
                messagebox.showerror("Error", "All fields required")
                return
            
            if category.lower() in ["academic", "personal", "internship"]:
                category = category.lower().capitalize()
            else:
                category = "Other"
            
            if nickname in accounts:
                if not messagebox.askyesno("Duplicate", f"'{nickname}' exists. Overwrite?"):
                    return
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            accounts[nickname] = {
                "app": app, "category": category, "password": password,
                "created": current_time, "last_modified": current_time
            }
            save_accounts()
            self.refresh_list()
            dialog.destroy()
            self.status_var.set(f"✓ Added {nickname}")
        
        ttk.Button(btn_frame, text="Save", command=save).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=2)
    
    def edit_account(self):
        if not self.current_account:
            return
        messagebox.showinfo("Edit", "Edit feature coming soon!")
    
    def delete_account(self):
        if not self.current_account:
            return
        
        if messagebox.askyesno("Delete", f"Delete '{self.current_account}'?"):
            del accounts[self.current_account]
            save_accounts()
            self.current_account = None
            self.refresh_list()
            self.status_var.set("✓ Account deleted")
    
    def show_password_reuse(self):
        reused = detect_password_reuse()
        msg = "No reused passwords found!" if not reused else f"Found {len(reused)} reused passwords"
        messagebox.showinfo("Password Reuse", msg)
    
    def show_password_generator(self):
        pwd = generate_password(24)
        feedback = get_password_feedback(pwd)
        messagebox.showinfo("Generated Password", f"{pwd}\n\nStrength: {feedback['category']}")
    
    def show_password_health(self):
        if not accounts:
            messagebox.showinfo("Health", "No accounts to analyze")
            return
        messagebox.showinfo("Health", "Health dashboard coming soon!")
    
    def show_about(self):
        about = "GateKeeper 2.5\n\nA modern password manager\nfor students and professionals"
        messagebox.showinfo("About", about)
    
    def show_storage_warning(self):
        msg = f"Accounts stored locally at:\n{os.path.abspath(FILENAME)}"
        messagebox.showwarning("Storage Warning", msg)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    root = tk.Tk()
    app = GateKeeperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
