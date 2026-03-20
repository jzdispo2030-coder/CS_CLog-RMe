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
# SOPHISTICATED DARK THEME
# ============================================================================

class DarkTheme:
    # Deep, rich dark colors - easy on the eyes
    bg_deep = "#0a0c0f"           # Very deep background
    bg_dark = "#14181c"           # Main background
    bg_medium = "#1e2329"          # Card background
    bg_light = "#2c313a"           # Hover/selected state
    bg_input = "#23282e"           # Input fields
    
    # Accent colors - muted but visible
    accent_primary = "#5f9ea0"      # Muted teal (cadet blue)
    accent_success = "#2e8b57"      # Sea green
    accent_warning = "#cd853f"      # Peru orange
    accent_danger = "#b22222"       # Firebrick
    accent_info = "#4682b4"          # Steel blue
    
    # Text colors - high contrast but not harsh
    text_primary = "#e6edf3"        # Almost white
    text_secondary = "#9aa8b9"       # Soft gray-blue
    text_muted = "#6c7a8d"           # Muted gray
    text_disabled = "#4a5568"        # Dark gray
    
    # Borders and accents
    border = "#2e353e"               # Subtle border
    border_light = "#3d4550"         # Lighter border
    
    # Strength colors - distinct but not neon
    strength_colors = {
        "Excellent": "#2e8b57",      # Sea green
        "Very Strong": "#3cb371",     # Medium sea green
        "Strong": "#4682b4",          # Steel blue
        "Good": "#cd853f",             # Peru orange
        "Fair": "#b8860b",             # Dark goldenrod
        "Weak": "#b22222",              # Firebrick
        "Very Weak": "#8b0000"          # Dark red
    }
    
    # Fonts - clean and readable
    heading_font = ("Segoe UI", 16, "bold")
    subheading_font = ("Segoe UI", 12, "bold")
    body_font = ("Segoe UI", 10)
    small_font = ("Segoe UI", 9)
    monospace_font = ("Consolas", 10) if os.name == 'nt' else ("Menlo", 10)

# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class ModernButton(tk.Canvas):
    """Custom modern button with hover effects"""
    def __init__(self, master, text, command=None, bg=DarkTheme.accent_primary, fg=DarkTheme.text_primary, 
                 width=120, height=35, corner_radius=8, font=DarkTheme.body_font, state=tk.NORMAL, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=DarkTheme.bg_dark)
        self.command = command
        self.text = text
        self.bg = bg
        self.fg = fg
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.font = font
        self.state = state
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw_button(self.bg if state == tk.NORMAL else DarkTheme.text_disabled)
    
    def draw_button(self, color):
        self.delete("all")
        # Rounded rectangle
        self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius, 
                                 fill=color, outline="")
        # Text
        text_color = self.fg if self.state == tk.NORMAL else DarkTheme.text_muted
        self.create_text(self.width//2, self.height//2, text=self.text, 
                        fill=text_color, font=self.font)
    
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
        if self.state == tk.NORMAL:
            self.draw_button(self.lighten_color(self.bg))
    
    def on_leave(self, event):
        if self.state == tk.NORMAL:
            self.draw_button(self.bg)
        else:
            self.draw_button(DarkTheme.text_disabled)
    
    def on_click(self, event):
        if self.state == tk.NORMAL and self.command:
            self.command()
    
    def configure(self, **kwargs):
        if 'state' in kwargs:
            self.state = kwargs['state']
            self.draw_button(self.bg if self.state == tk.NORMAL else DarkTheme.text_disabled)
        if 'text' in kwargs:
            self.text = kwargs['text']
            self.draw_button(self.bg if self.state == tk.NORMAL else DarkTheme.text_disabled)
    
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
    """Styled entry widget for dark mode"""
    def __init__(self, master, **kwargs):
        super().__init__(master, font=DarkTheme.body_font, **kwargs)
        style = ttk.Style()
        style.configure("Dark.TEntry", 
                       fieldbackground=DarkTheme.bg_input,
                       foreground=DarkTheme.text_primary,
                       insertcolor=DarkTheme.text_primary,
                       bordercolor=DarkTheme.border,
                       lightcolor=DarkTheme.border,
                       darkcolor=DarkTheme.border,
                       borderwidth=1,
                       relief="solid",
                       padding=8)
        self.configure(style="Dark.TEntry")

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class GateKeeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GateKeeper")
        self.root.geometry("1400x850")
        self.root.configure(bg=DarkTheme.bg_deep)
        
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
        """Configure ttk styles for dark mode"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Base colors
        style.configure('.', 
                       background=DarkTheme.bg_dark,
                       foreground=DarkTheme.text_primary,
                       fieldbackground=DarkTheme.bg_input,
                       troughcolor=DarkTheme.bg_light,
                       selectbackground=DarkTheme.accent_primary,
                       selectforeground=DarkTheme.text_primary)
        
        # Labels
        style.configure('TLabel', 
                       background=DarkTheme.bg_dark,
                       foreground=DarkTheme.text_primary,
                       font=DarkTheme.body_font)
        
        style.configure('Heading.TLabel', 
                       font=DarkTheme.heading_font,
                       foreground=DarkTheme.accent_primary)
        
        style.configure('Subheading.TLabel', 
                       font=DarkTheme.subheading_font,
                       foreground=DarkTheme.text_primary)
        
        style.configure('Muted.TLabel',
                       foreground=DarkTheme.text_muted,
                       font=DarkTheme.small_font)
        
        # Frames
        style.configure('TFrame', background=DarkTheme.bg_dark)
        style.configure('Deep.TFrame', background=DarkTheme.bg_deep)
        style.configure('Card.TFrame', 
                       background=DarkTheme.bg_medium,
                       relief="solid",
                       borderwidth=1,
                       bordercolor=DarkTheme.border)
        
        # LabelFrames
        style.configure('TLabelframe', 
                       background=DarkTheme.bg_dark,
                       foreground=DarkTheme.text_primary,
                       bordercolor=DarkTheme.border)
        
        style.configure('TLabelframe.Label', 
                       background=DarkTheme.bg_dark,
                       foreground=DarkTheme.text_secondary,
                       font=DarkTheme.small_font)
        
        # Entry fields
        style.configure('TEntry', 
                       fieldbackground=DarkTheme.bg_input,
                       foreground=DarkTheme.text_primary,
                       insertcolor=DarkTheme.text_primary,
                       bordercolor=DarkTheme.border,
                       borderwidth=1,
                       padding=8)
        
        # Combobox
        style.configure('TCombobox', 
                       fieldbackground=DarkTheme.bg_input,
                       foreground=DarkTheme.text_primary,
                       selectbackground=DarkTheme.accent_primary,
                       selectforeground=DarkTheme.text_primary,
                       bordercolor=DarkTheme.border,
                       arrowcolor=DarkTheme.text_secondary)
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', DarkTheme.bg_input)],
                 selectbackground=[('readonly', DarkTheme.accent_primary)])
        
        # Scrollbar
        style.configure('TScrollbar',
                       background=DarkTheme.bg_light,
                       troughcolor=DarkTheme.bg_medium,
                       arrowcolor=DarkTheme.text_secondary,
                       borderwidth=0)
        
        # Progressbar
        style.configure('TProgressbar',
                       background=DarkTheme.accent_primary,
                       troughcolor=DarkTheme.bg_light,
                       borderwidth=0)
        
        # Menu
        style.configure('TMenubar', 
                       background=DarkTheme.bg_deep,
                       foreground=DarkTheme.text_primary)
        
        style.configure('TMenu', 
                       background=DarkTheme.bg_medium,
                       foreground=DarkTheme.text_primary,
                       borderwidth=0)
        
        style.map('TMenu',
                 background=[('active', DarkTheme.accent_primary)],
                 foreground=[('active', DarkTheme.text_primary)])
    
    def setup_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg=DarkTheme.bg_deep, fg=DarkTheme.text_primary,
                         activebackground=DarkTheme.accent_primary, activeforeground=DarkTheme.text_primary,
                         borderwidth=0, relief="flat")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.text_primary,
                           activebackground=DarkTheme.accent_primary, activeforeground=DarkTheme.text_primary,
                           borderwidth=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Account", command=self.add_account_dialog, accelerator="⌘N")
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="⌘Q")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.text_primary,
                           activebackground=DarkTheme.accent_primary, activeforeground=DarkTheme.text_primary,
                           borderwidth=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh List", command=self.refresh_list, accelerator="⌘R")
        view_menu.add_separator()
        view_menu.add_command(label="All Accounts", command=lambda: self.set_category_filter("All"))
        view_menu.add_command(label="Academic", command=lambda: self.set_category_filter("Academic"))
        view_menu.add_command(label="Personal", command=lambda: self.set_category_filter("Personal"))
        view_menu.add_command(label="Internship", command=lambda: self.set_category_filter("Internship"))
        view_menu.add_command(label="Other", command=lambda: self.set_category_filter("Other"))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.text_primary,
                            activebackground=DarkTheme.accent_primary, activeforeground=DarkTheme.text_primary,
                            borderwidth=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Password Reuse Report", command=self.show_password_reuse)
        tools_menu.add_command(label="Generate Strong Password", command=self.show_password_generator)
        tools_menu.add_command(label="Password Health Dashboard", command=self.show_password_health)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.text_primary,
                           activebackground=DarkTheme.accent_primary, activeforeground=DarkTheme.text_primary,
                           borderwidth=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About GateKeeper", command=self.show_about)
        help_menu.add_command(label="Storage Information", command=self.show_storage_warning)
        
        # Keyboard shortcuts
        self.root.bind('<Command-n>', lambda e: self.add_account_dialog())
        self.root.bind('<Control-n>', lambda e: self.add_account_dialog())
        self.root.bind('<Command-r>', lambda e: self.refresh_list())
        self.root.bind('<Control-r>', lambda e: self.refresh_list())
        self.root.bind('<Command-q>', lambda e: self.root.quit())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
    
    def setup_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, style='Deep.TFrame', padding="25")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ====================================================================
        # HEADER SECTION
        # ====================================================================
        header_frame = ttk.Frame(main_container, style='Deep.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Title and stats
        title_frame = ttk.Frame(header_frame, style='Deep.TFrame')
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text="GateKeeper", style='Heading.TLabel').pack(anchor=tk.W)
        ttk.Label(title_frame, text="secure password manager", style='Muted.TLabel').pack(anchor=tk.W)
        
        # Stats card
        stats_card = ttk.Frame(header_frame, style='Card.TFrame', padding="15")
        stats_card.pack(side=tk.RIGHT)
        
        self.stats_label = ttk.Label(stats_card, text="0 accounts", 
                                     font=DarkTheme.subheading_font,
                                     foreground=DarkTheme.text_primary)
        self.stats_label.pack()
        
        # Warning banner
        warning_card = ttk.Frame(main_container, style='Card.TFrame', padding="12")
        warning_card.pack(fill=tk.X, pady=(0, 25))
        
        self.warning_text = tk.Text(warning_card, height=1, font=DarkTheme.small_font,
                                    bg=DarkTheme.bg_medium, fg=DarkTheme.accent_warning,
                                    wrap=tk.WORD, bd=0, highlightthickness=0)
        self.warning_text.pack(fill=tk.X)
        self.warning_text.insert(1.0, "⚠️  Local storage only — accounts are saved on this device")
        self.warning_text.config(state=tk.DISABLED)
        
        # ====================================================================
        # SEARCH AND FILTER SECTION
        # ====================================================================
        search_frame = ttk.Frame(main_container, style='Deep.TFrame')
        search_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Search bar with icon
        search_container = ttk.Frame(search_frame, style='Deep.TFrame')
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_container, text="🔍", font=("Segoe UI", 12),
                 background=DarkTheme.bg_deep).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_list)
        search_entry = ModernEntry(search_container, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Category filter
        category_container = ttk.Frame(search_frame, style='Deep.TFrame')
        category_container.pack(side=tk.RIGHT, padx=(20, 0))
        
        ttk.Label(category_container, text="Category:", style='Muted.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(category_container, textvariable=self.category_var,
                                       values=["All", "Academic", "Personal", "Internship", "Other"],
                                       state="readonly", width=15, font=DarkTheme.body_font)
        category_combo.pack(side=tk.LEFT)
        category_combo.bind('<<ComboboxSelected>>', self.filter_list)
        
        # ====================================================================
        # MAIN CONTENT - Two column layout
        # ====================================================================
        content_frame = ttk.Frame(main_container, style='Deep.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Accounts list
        left_column = ttk.Frame(content_frame, style='Deep.TFrame')
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Section header with add button
        left_header = ttk.Frame(left_column, style='Deep.TFrame')
        left_header.pack(fill=tk.X, pady=(0, 12))
        
        ttk.Label(left_header, text="Your Accounts", style='Subheading.TLabel').pack(side=tk.LEFT)
        
        add_btn = ModernButton(left_header, text="+ New", command=self.add_account_dialog,
                               bg=DarkTheme.accent_primary, width=80, height=32, corner_radius=6)
        add_btn.pack(side=tk.RIGHT)
        
        # Accounts list card
        list_card = ttk.Frame(left_column, style='Card.TFrame')
        list_card.pack(fill=tk.BOTH, expand=True)
        
        list_container = ttk.Frame(list_card, padding="1")
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.accounts_list = tk.Listbox(list_container, yscrollcommand=scrollbar.set,
                                        font=DarkTheme.monospace_font,
                                        bg=DarkTheme.bg_input,
                                        fg=DarkTheme.text_primary,
                                        selectbackground=DarkTheme.accent_primary,
                                        selectforeground=DarkTheme.text_primary,
                                        bd=0, highlightthickness=0,
                                        activestyle="none",
                                        relief="flat")
        self.accounts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.accounts_list.bind('<<ListboxSelect>>', self.on_account_select)
        self.accounts_list.bind('<Double-Button-1>', lambda e: self.inspect_password())
        
        scrollbar.config(command=self.accounts_list.yview)
        
        # Right column - Details and actions
        right_column = ttk.Frame(content_frame, style='Deep.TFrame')
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        # Details card
        details_card = ttk.Frame(right_column, style='Card.TFrame', padding="20")
        details_card.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(details_card, text="Account Details", style='Subheading.TLabel').pack(anchor=tk.W, pady=(0, 15))
        
        # Details text
        details_container = ttk.Frame(details_card)
        details_container.pack(fill=tk.BOTH, expand=True)
        
        details_scrollbar = ttk.Scrollbar(details_container)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = tk.Text(details_container, yscrollcommand=details_scrollbar.set,
                                    height=8, font=DarkTheme.monospace_font,
                                    bg=DarkTheme.bg_input, fg=DarkTheme.text_primary,
                                    bd=0, highlightthickness=0,
                                    relief="flat", padx=12, pady=12)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.details_text.config(state=tk.DISABLED)
        
        details_scrollbar.config(command=self.details_text.yview)
        
        # Strength meter
        strength_frame = ttk.Frame(details_card)
        strength_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(strength_frame, text="Password Strength", style='Muted.TLabel').pack(anchor=tk.W)
        
        meter_frame = ttk.Frame(strength_frame)
        meter_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.strength_bar = ttk.Progressbar(meter_frame, length=200, mode='determinate')
        self.strength_bar.pack(side=tk.LEFT)
        
        self.strength_label = ttk.Label(meter_frame, text="", font=DarkTheme.body_font,
                                        foreground=DarkTheme.text_primary)
        self.strength_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Crack time
        self.crack_time_label = ttk.Label(strength_frame, text="", style='Muted.TLabel')
        self.crack_time_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Strengths list
        strengths_frame = ttk.Frame(strength_frame)
        strengths_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(strengths_frame, text="✅ Strengths:", style='Muted.TLabel').pack(anchor=tk.W)
        self.strengths_list = tk.Text(strengths_frame, height=2, width=40, font=DarkTheme.small_font,
                                      wrap=tk.WORD, bg=DarkTheme.bg_input, fg=DarkTheme.accent_success,
                                      bd=1, relief="solid", highlightthickness=0)
        self.strengths_list.pack(fill=tk.X, pady=5)
        self.strengths_list.config(state=tk.DISABLED)
        
        # Issues list
        issues_frame = ttk.Frame(strength_frame)
        issues_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(issues_frame, text="⚠️ Issues to fix:", style='Muted.TLabel').pack(anchor=tk.W)
        self.issues_list = tk.Text(issues_frame, height=2, width=40, font=DarkTheme.small_font,
                                  wrap=tk.WORD, bg=DarkTheme.bg_input, fg=DarkTheme.accent_danger,
                                  bd=1, relief="solid", highlightthickness=0)
        self.issues_list.pack(fill=tk.X, pady=5)
        self.issues_list.config(state=tk.DISABLED)
        
        # ====================================================================
        # ACTION BUTTONS - SCROLLABLE AREA
        # ====================================================================
        button_container = ttk.Frame(right_column)
        button_container.pack(fill=tk.X, pady=(15, 0))
        
        # Create canvas and scrollbar for buttons
        button_canvas = tk.Canvas(button_container, bg=DarkTheme.bg_deep, highlightthickness=0, height=150)
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
        btn_card = ttk.Frame(button_scrollable_frame, style='Card.TFrame', padding="15")
        btn_card.pack(fill=tk.X, expand=True)
        
        ttk.Label(btn_card, text="Quick Actions", style='Subheading.TLabel').pack(anchor=tk.W, pady=(0, 12))
        
        # Button grid
        button_grid = ttk.Frame(btn_card)
        button_grid.pack(fill=tk.X)
        
        # Row 1
        row1 = ttk.Frame(button_grid)
        row1.pack(fill=tk.X, pady=3)
        
        self.inspect_btn = ModernButton(row1, text="🔍 Inspect", command=self.inspect_password,
                                        bg=DarkTheme.accent_info, width=120, height=35)
        self.inspect_btn.pack(side=tk.LEFT, padx=3)
        
        self.copy_btn = ModernButton(row1, text="📋 Copy", command=self.copy_password,
                                     bg=DarkTheme.accent_success, width=120, height=35)
        self.copy_btn.pack(side=tk.LEFT, padx=3)
        
        # Row 2
        row2 = ttk.Frame(button_grid)
        row2.pack(fill=tk.X, pady=3)
        
        self.toggle_btn = ModernButton(row2, text="👁️ Show", command=self.toggle_password,
                                       bg=DarkTheme.text_muted, width=120, height=35, state=tk.DISABLED)
        self.toggle_btn.pack(side=tk.LEFT, padx=3)
        
        self.edit_btn = ModernButton(row2, text="✏️ Edit", command=self.edit_account,
                                     bg=DarkTheme.accent_warning, width=120, height=35, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=3)
        
        # Row 3
        row3 = ttk.Frame(button_grid)
        row3.pack(fill=tk.X, pady=3)
        
        self.delete_btn = ModernButton(row3, text="🗑️ Delete", command=self.delete_account,
                                       bg=DarkTheme.accent_danger, width=246, height=35, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=3)
        
        # Add some padding at the bottom
        ttk.Frame(btn_card, height=10).pack()
        
        # ====================================================================
        # TIP CARD
        # ====================================================================
        tip_card = ttk.Frame(right_column, style='Card.TFrame', padding="15")
        tip_card.pack(fill=tk.X, pady=(15, 0))
        
        tip_header = ttk.Frame(tip_card)
        tip_header.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(tip_header, text="💡 Tip", font=DarkTheme.body_font,
                 foreground=DarkTheme.accent_info).pack(side=tk.LEFT)
        
        self.tip_label = ttk.Label(tip_card, text="", style='Muted.TLabel',
                                   wraplength=350, justify=tk.LEFT)
        self.tip_label.pack(anchor=tk.W)
        
        # ====================================================================
        # STATUS BAR
        # ====================================================================
        status_bar = ttk.Frame(self.root, style='Card.TFrame', padding="8")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(status_bar, textvariable=self.status_var, style='Muted.TLabel').pack(side=tk.LEFT)
    
    def show_intro(self):
        """Show introduction information"""
        account_count = len(accounts)
        self.stats_label.config(text=f"{account_count} accounts")
        
        reused = detect_password_reuse()
        if reused:
            self.status_var.set(f"⚠️  {len(reused)} reused passwords detected")
        
        tips = [
            "Use 16+ characters for maximum security",
            "Mix uppercase, lowercase, numbers, and symbols",
            "Never reuse passwords across accounts",
            "Longer passwords are stronger than complex ones",
            "Double-click any account to inspect it",
            "Check Tools menu for security reports",
            "Use the scrollbar to see all action buttons"
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
        self.strength_label.config(text=feedback['category'],
                                   foreground=DarkTheme.strength_colors.get(feedback['category'], DarkTheme.text_primary))
        
        crack_time = estimate_crack_time(data['password'])
        self.crack_time_label.config(text=f"⏱️  Estimated crack time: {crack_time}")
        
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
        
        if self.show_passwords:
            self.toggle_btn.configure(text="👁️ Hide")
        else:
            self.toggle_btn.configure(text="👁️ Show")
    
    def toggle_password(self):
        if not self.current_account:
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
        
        # Create inspector window
        inspector = tk.Toplevel(self.root)
        inspector.title(f"Password Inspector — {self.current_account}")
        inspector.geometry("600x700")
        inspector.configure(bg=DarkTheme.bg_deep)
        inspector.transient(self.root)
        inspector.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(inspector, style='Deep.TFrame', padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with score
        header = ttk.Frame(main_frame, style='Deep.TFrame')
        header.pack(fill=tk.X, pady=(0, 20))
        
        score_color = DarkTheme.strength_colors.get(feedback['category'], DarkTheme.accent_primary)
        score_label = tk.Label(header, text=f"{feedback['score']:.1f}", 
                               font=("Segoe UI", 40, "bold"), 
                               fg=score_color, 
                               bg=DarkTheme.bg_deep)
        score_label.pack(side=tk.LEFT, padx=(0, 20))
        
        info = ttk.Frame(header, style='Deep.TFrame')
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(info, text=feedback['category'], font=("Segoe UI", 16, "bold"),
                 foreground=score_color).pack(anchor=tk.W)
        ttk.Label(info, text=f"Length: {len(data['password'])} characters", 
                 style='Muted.TLabel').pack(anchor=tk.W)
        ttk.Label(info, text=f"Crack time: {estimate_crack_time(data['password'])}", 
                 style='Muted.TLabel').pack(anchor=tk.W)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Tab 1: Analysis
        analysis = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(analysis, text="Analysis")
        
        ttk.Label(analysis, text="Character Types", style='Subheading.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        has_lower = bool(re.search(r"[a-z]", data['password']))
        has_upper = bool(re.search(r"[A-Z]", data['password']))
        has_digit = bool(re.search(r"[0-9]", data['password']))
        has_symbol = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", data['password']))
        
        types = [
            ("Lowercase (a-z)", has_lower),
            ("Uppercase (A-Z)", has_upper),
            ("Numbers (0-9)", has_digit),
            ("Symbols (!@#$%)", has_symbol)
        ]
        
        for label, present in types:
            f = ttk.Frame(analysis)
            f.pack(fill=tk.X, pady=3)
            ttk.Label(f, text=label, width=20).pack(side=tk.LEFT)
            status = "✓ Yes" if present else "✗ No"
            color = DarkTheme.accent_success if present else DarkTheme.accent_danger
            ttk.Label(f, text=status, foreground=color).pack(side=tk.LEFT)
        
        # Tab 2: Strengths
        strengths_tab = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(strengths_tab, text="Strengths")
        
        if feedback['strengths']:
            for strength in feedback['strengths']:
                f = ttk.Frame(strengths_tab)
                f.pack(fill=tk.X, pady=3)
                ttk.Label(f, text="✅", foreground=DarkTheme.accent_success).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(f, text=strength, wraplength=450).pack(side=tk.LEFT)
        else:
            ttk.Label(strengths_tab, text="No notable strengths found", 
                     style='Muted.TLabel').pack(pady=20)
        
        # Tab 3: Issues
        issues_tab = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(issues_tab, text="Issues")
        
        if feedback['issues']:
            for issue in feedback['issues']:
                f = ttk.Frame(issues_tab)
                f.pack(fill=tk.X, pady=3)
                ttk.Label(f, text="⚠️", foreground=DarkTheme.accent_danger).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(f, text=issue, wraplength=450).pack(side=tk.LEFT)
                
                # Suggest fix based on issue
                if "uppercase" in issue.lower():
                    ttk.Label(issues_tab, text="  💡 Fix: Add capital letters (A-Z)", 
                             foreground=DarkTheme.accent_info).pack(anchor=tk.W, padx=(25, 0))
                elif "lowercase" in issue.lower():
                    ttk.Label(issues_tab, text="  💡 Fix: Add lowercase letters (a-z)", 
                             foreground=DarkTheme.accent_info).pack(anchor=tk.W, padx=(25, 0))
                elif "number" in issue.lower():
                    ttk.Label(issues_tab, text="  💡 Fix: Add numbers (0-9)", 
                             foreground=DarkTheme.accent_info).pack(anchor=tk.W, padx=(25, 0))
                elif "symbol" in issue.lower():
                    ttk.Label(issues_tab, text="  💡 Fix: Add symbols (!@#$%)", 
                             foreground=DarkTheme.accent_info).pack(anchor=tk.W, padx=(25, 0))
                elif "short" in issue.lower():
                    ttk.Label(issues_tab, text="  💡 Fix: Make password longer (12+ chars)", 
                             foreground=DarkTheme.accent_info).pack(anchor=tk.W, padx=(25, 0))
                elif "common" in issue.lower():
                    ttk.Label(issues_tab, text="  💡 Fix: Avoid common words or patterns", 
                             foreground=DarkTheme.accent_info).pack(anchor=tk.W, padx=(25, 0))
        else:
            ttk.Label(issues_tab, text="No issues found - Excellent password!", 
                     foreground=DarkTheme.accent_success).pack(pady=20)
        
        # Tab 4: Suggestions
        suggestions_tab = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(suggestions_tab, text="Suggestions")
        
        ttk.Label(suggestions_tab, text="Improvement Ideas", 
                 style='Subheading.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
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
                f = ttk.Frame(suggestions_tab)
                f.pack(fill=tk.X, pady=2)
                ttk.Label(f, text="💡", foreground=DarkTheme.accent_info).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(f, text=suggestion, wraplength=450).pack(side=tk.LEFT)
        else:
            ttk.Label(suggestions_tab, text="Your password looks great! No suggestions needed.", 
                     style='Muted.TLabel').pack(pady=20)
        
        # Tab 5: Quick Actions
        actions_tab = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(actions_tab, text="Quick Actions")
        
        ttk.Label(actions_tab, text="What would you like to do?", 
                 style='Subheading.TLabel').pack(pady=(0, 15))
        
        action_frame = ttk.Frame(actions_tab)
        action_frame.pack(pady=10)
        
        ttk.Button(action_frame, text="🔄 Generate New Password", 
                  command=lambda: self.suggest_better_password(data['password'], inspector),
                  width=25).pack(pady=5)
        
        ttk.Button(action_frame, text="📋 Copy to Clipboard", 
                  command=lambda: self.copy_password_from_inspector(inspector),
                  width=25).pack(pady=5)
        
        ttk.Button(action_frame, text="✏️ Edit Account", 
                  command=lambda: [inspector.destroy(), self.edit_account()],
                  width=25).pack(pady=5)
        
        # Close button
        btn_frame = ttk.Frame(main_frame, style='Deep.TFrame')
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(btn_frame, text="Close", command=inspector.destroy, width=15).pack()
    
    def copy_password_from_inspector(self, inspector):
        """Copy password from inspector window"""
        if self.current_account:
            password = accounts[self.current_account]['password']
            try:
                pyperclip.copy(password)
                self.status_var.set("✓ Password copied")
                messagebox.showinfo("Success", "Password copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy: {str(e)}")
    
    def suggest_better_password(self, current_password, parent_window):
        """Suggest better passwords"""
        suggestions = []
        for _ in range(3):
            suggestions.append(generate_password(16))
        
        # Create suggestion dialog
        dialog = tk.Toplevel(parent_window)
        dialog.title("Password Suggestions")
        dialog.geometry("500x400")
        dialog.configure(bg=DarkTheme.bg_deep)
        dialog.transient(parent_window)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, style='Deep.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Try one of these strong passwords:", 
                 font=DarkTheme.subheading_font).pack(pady=(0, 15))
        
        for i, pwd in enumerate(suggestions):
            frame = ttk.Frame(main_frame, style='Card.TFrame', padding="10")
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"Option {i+1}:", 
                     font=DarkTheme.small_font).pack(anchor=tk.W)
            
            pwd_frame = ttk.Frame(frame)
            pwd_frame.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Label(pwd_frame, text=pwd, font=DarkTheme.monospace_font).pack(side=tk.LEFT)
            ttk.Button(pwd_frame, text="Use", 
                      command=lambda p=pwd: self.use_suggested_password(p, dialog)).pack(side=tk.RIGHT)
        
        ttk.Button(main_frame, text="Cancel", command=dialog.destroy).pack(pady=15)
    
    def use_suggested_password(self, password, dialog):
        """Use a suggested password"""
        try:
            pyperclip.copy(password)
            dialog.destroy()
            
            result = messagebox.askyesno(
                "Use This Password?",
                f"Password copied to clipboard!\n\nWould you like to update the current account with this password?"
            )
            
            if result and self.current_account:
                accounts[self.current_account]['password'] = password
                accounts[self.current_account]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_accounts()
                self.display_account_details(self.current_account)
                self.status_var.set("✓ Password updated")
                messagebox.showinfo("Success", "Account updated with new password!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def add_account_dialog(self):
        """Open dialog to add a new account"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Account")
        dialog.geometry("500x650")
        dialog.configure(bg=DarkTheme.bg_deep)
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, style='Deep.TFrame', padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable frame for form
        canvas = tk.Canvas(main_frame, bg=DarkTheme.bg_deep, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
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
        form_frame = ttk.Frame(scrollable_frame, style='Deep.TFrame', padding="0 0 10 0")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Create New Account", 
                 font=("Segoe UI", 16, "bold"),
                 foreground=DarkTheme.accent_primary).pack(anchor=tk.W, pady=(0, 20))
        
        # Nickname
        ttk.Label(form_frame, text="Nickname", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        nickname_var = tk.StringVar()
        nickname_entry = ModernEntry(form_frame, textvariable=nickname_var)
        nickname_entry.pack(fill=tk.X)
        
        # App name
        ttk.Label(form_frame, text="App Name", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        app_var = tk.StringVar()
        app_entry = ModernEntry(form_frame, textvariable=app_var)
        app_entry.pack(fill=tk.X)
        
        # Category
        ttk.Label(form_frame, text="Category", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        category_var = tk.StringVar(value="Personal")
        category_combo = ttk.Combobox(form_frame, textvariable=category_var,
                                      values=["Academic", "Personal", "Internship", "Other"],
                                      state="readonly", font=DarkTheme.body_font)
        category_combo.pack(fill=tk.X)
        
        # Password
        ttk.Label(form_frame, text="Password", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        
        pwd_frame = ttk.Frame(form_frame)
        pwd_frame.pack(fill=tk.X)
        
        password_var = tk.StringVar()
        password_entry = ModernEntry(pwd_frame, textvariable=password_var, show="•")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def generate_and_set():
            pwd = generate_password()
            password_var.set(pwd)
            password_entry.configure(show="")
            show_pwd_var.set(True)
            update_strength()
        
        ttk.Button(pwd_frame, text="Generate", command=generate_and_set,
                  width=10).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Show password checkbox
        show_pwd_var = tk.BooleanVar()
        def toggle_password_visibility():
            if show_pwd_var.get():
                password_entry.configure(show="")
            else:
                password_entry.configure(show="•")
        
        ttk.Checkbutton(form_frame, text="Show password", variable=show_pwd_var,
                       command=toggle_password_visibility).pack(anchor=tk.W, pady=5)
        
        # Live strength meter
        preview_frame = ttk.LabelFrame(form_frame, text="Password Strength Preview", 
                                       padding="10", style='Card.TFrame')
        preview_frame.pack(fill=tk.X, pady=(15, 0))
        
        preview_bar = ttk.Progressbar(preview_frame, length=300, mode='determinate')
        preview_bar.pack(pady=5)
        
        preview_label = ttk.Label(preview_frame, text="", font=DarkTheme.body_font)
        preview_label.pack()
        
        preview_crack = ttk.Label(preview_frame, text="", style='Muted.TLabel')
        preview_crack.pack()
        
        def update_strength(*args):
            pwd = password_var.get()
            if pwd:
                feedback = get_password_feedback(pwd)
                preview_bar['value'] = (feedback['score'] / 10) * 100
                preview_label.config(text=f"{feedback['category']} ({feedback['score']:.1f}/10)",
                                    foreground=DarkTheme.strength_colors.get(feedback['category'], DarkTheme.text_primary))
                crack_time = estimate_crack_time(pwd)
                preview_crack.config(text=f"⏱️  {crack_time} to crack")
            else:
                preview_bar['value'] = 0
                preview_label.config(text="Enter a password")
                preview_crack.config(text="")
        
        password_var.trace('w', update_strength)
        
        # Bottom padding
        ttk.Frame(form_frame, height=20).pack()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        def save():
            nickname = nickname_var.get().strip()
            app = app_var.get().strip()
            category = category_var.get()
            password = password_var.get().strip()
            
            if not nickname or not app or not password:
                messagebox.showerror("Error", "All fields are required")
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
            self.status_var.set(f"✓ Added {nickname}")
        
        ttk.Button(btn_frame, text="Save", command=save, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
        
        # Focus on nickname entry
        nickname_entry.focus()
    
    def edit_account(self):
        """Edit the selected account"""
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        # Get current data
        current_data = accounts[self.current_account]
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Account — {self.current_account}")
        edit_window.geometry("500x600")
        edit_window.configure(bg=DarkTheme.bg_deep)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        main_frame = ttk.Frame(edit_window, style='Deep.TFrame', padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable frame
        canvas = tk.Canvas(main_frame, bg=DarkTheme.bg_deep, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
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
        form_frame = ttk.Frame(scrollable_frame, style='Deep.TFrame', padding="0 0 10 0")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Edit Account", 
                 font=("Segoe UI", 16, "bold"),
                 foreground=DarkTheme.accent_primary).pack(anchor=tk.W, pady=(0, 20))
        
        # Nickname (read-only)
        ttk.Label(form_frame, text="Nickname", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        ttk.Label(form_frame, text=self.current_account, font=DarkTheme.body_font,
                 foreground=DarkTheme.text_primary).pack(anchor=tk.W)
        
        # App name
        ttk.Label(form_frame, text="App Name", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        app_var = tk.StringVar(value=current_data['app'])
        app_entry = ModernEntry(form_frame, textvariable=app_var)
        app_entry.pack(fill=tk.X)
        
        # Category
        ttk.Label(form_frame, text="Category", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        category_var = tk.StringVar(value=current_data['category'])
        category_combo = ttk.Combobox(form_frame, textvariable=category_var,
                                      values=["Academic", "Personal", "Internship", "Other"],
                                      state="readonly", font=DarkTheme.body_font)
        category_combo.pack(fill=tk.X)
        
        # Password
        ttk.Label(form_frame, text="Password", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        
        pwd_frame = ttk.Frame(form_frame)
        pwd_frame.pack(fill=tk.X)
        
        password_var = tk.StringVar(value=current_data['password'])
        password_entry = ModernEntry(pwd_frame, textvariable=password_var, show="•")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def generate_and_set():
            pwd = generate_password()
            password_var.set(pwd)
            password_entry.configure(show="")
            show_pwd_var.set(True)
            update_strength()
        
        ttk.Button(pwd_frame, text="Generate", command=generate_and_set,
                  width=10).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Show password checkbox
        show_pwd_var = tk.BooleanVar()
        def toggle_password_visibility():
            if show_pwd_var.get():
                password_entry.configure(show="")
            else:
                password_entry.configure(show="•")
        
        ttk.Checkbutton(form_frame, text="Show password", variable=show_pwd_var,
                       command=toggle_password_visibility).pack(anchor=tk.W, pady=5)
        
        # Live strength meter
        preview_frame = ttk.LabelFrame(form_frame, text="Password Strength Preview", 
                                       padding="10", style='Card.TFrame')
        preview_frame.pack(fill=tk.X, pady=(15, 0))
        
        preview_bar = ttk.Progressbar(preview_frame, length=300, mode='determinate')
        preview_bar.pack(pady=5)
        
        preview_label = ttk.Label(preview_frame, text="", font=DarkTheme.body_font)
        preview_label.pack()
        
        preview_crack = ttk.Label(preview_frame, text="", style='Muted.TLabel')
        preview_crack.pack()
        
        def update_strength(*args):
            pwd = password_var.get()
            if pwd:
                feedback = get_password_feedback(pwd)
                preview_bar['value'] = (feedback['score'] / 10) * 100
                preview_label.config(text=f"{feedback['category']} ({feedback['score']:.1f}/10)",
                                    foreground=DarkTheme.strength_colors.get(feedback['category'], DarkTheme.text_primary))
                crack_time = estimate_crack_time(pwd)
                preview_crack.config(text=f"⏱️  {crack_time} to crack")
            else:
                preview_bar['value'] = 0
                preview_label.config(text="Enter a password")
                preview_crack.config(text="")
        
        # Initial update
        update_strength()
        password_var.trace('w', update_strength)
        
        # Bottom padding
        ttk.Frame(form_frame, height=20).pack()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
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
        
        ttk.Button(btn_frame, text="Save", command=save_changes, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=edit_window.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def delete_account(self):
        """Delete current account with confirmation"""
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        
        result = messagebox.askyesno(
            "Delete Account",
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
            self.toggle_btn.configure(state=tk.DISABLED)
            self.edit_btn.configure(state=tk.DISABLED)
            self.delete_btn.configure(state=tk.DISABLED)
            
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
        """Show password reuse report"""
        reused = detect_password_reuse()
        
        if not reused:
            messagebox.showinfo("Password Reuse", "✅ No reused passwords found!")
            return
        
        # Create report window
        report_window = tk.Toplevel(self.root)
        report_window.title("Password Reuse Report")
        report_window.geometry("600x500")
        report_window.configure(bg=DarkTheme.bg_deep)
        report_window.transient(self.root)
        
        main_frame = ttk.Frame(report_window, style='Deep.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Password Reuse Report", 
                 font=DarkTheme.heading_font,
                 foreground=DarkTheme.accent_primary).pack(pady=(0, 15))
        
        ttk.Label(main_frame, text=f"Found {len(reused)} reused password(s):", 
                 style='Subheading.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, wrap=tk.WORD,
                              font=DarkTheme.body_font,
                              bg=DarkTheme.bg_input, fg=DarkTheme.text_primary,
                              bd=0, highlightthickness=0, padx=10, pady=10)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text_widget.yview)
        
        for i, item in enumerate(reused, 1):
            text_widget.insert(tk.END, f"\n{i}. Password: {item['password']}\n", "password")
            text_widget.tag_config("password", foreground=DarkTheme.accent_danger, font=DarkTheme.monospace_font)
            text_widget.insert(tk.END, f"   Used in {item['count']} accounts:\n")
            for acc in item['accounts']:
                text_widget.insert(tk.END, f"   • {acc} ({accounts[acc]['app']})\n")
            text_widget.insert(tk.END, "\n" + "─"*50 + "\n")
        
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(main_frame, text="Close", command=report_window.destroy).pack(pady=15)
    
    def show_password_generator(self):
        """Show password generator tool"""
        pwd = generate_password(24)
        feedback = get_password_feedback(pwd)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Password Generator")
        dialog.geometry("450x300")
        dialog.configure(bg=DarkTheme.bg_deep)
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, style='Deep.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Generated Password", 
                 font=DarkTheme.subheading_font,
                 foreground=DarkTheme.accent_primary).pack(pady=(0, 15))
        
        # Password display
        pwd_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="15")
        pwd_frame.pack(fill=tk.X)
        
        ttk.Label(pwd_frame, text=pwd, font=DarkTheme.monospace_font).pack()
        
        # Strength info
        ttk.Label(main_frame, text=f"Strength: {feedback['category']} ({feedback['score']:.1f}/10)",
                 foreground=DarkTheme.strength_colors.get(feedback['category'], DarkTheme.text_primary)).pack(pady=10)
        
        ttk.Label(main_frame, text=f"⏱️  Crack time: {estimate_crack_time(pwd)}",
                 style='Muted.TLabel').pack()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        def copy_and_close():
            try:
                pyperclip.copy(pwd)
                self.status_var.set("✓ Password copied")
                dialog.destroy()
                messagebox.showinfo("Success", "Password copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy: {str(e)}")
        
        ttk.Button(btn_frame, text="Copy to Clipboard", command=copy_and_close, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)
    
    def show_password_health(self):
        """Show overall password health dashboard"""
        if not accounts:
            messagebox.showinfo("Health Dashboard", "No accounts to analyze")
            return
        
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
        
        # Create health dashboard window
        health_window = tk.Toplevel(self.root)
        health_window.title("Password Health Dashboard")
        health_window.geometry("550x500")
        health_window.configure(bg=DarkTheme.bg_deep)
        health_window.transient(self.root)
        
        main_frame = ttk.Frame(health_window, style='Deep.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Password Health Dashboard", 
                 font=DarkTheme.heading_font,
                 foreground=DarkTheme.accent_primary).pack(pady=(0, 20))
        
        # Stats cards
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Total accounts card
        total_card = ttk.Frame(stats_frame, style='Card.TFrame', padding="15")
        total_card.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ttk.Label(total_card, text="Total Accounts", style='Muted.TLabel').pack()
        ttk.Label(total_card, text=str(total), font=("Segoe UI", 24, "bold"),
                 foreground=DarkTheme.text_primary).pack()
        
        # Average strength card
        avg_card = ttk.Frame(stats_frame, style='Card.TFrame', padding="15")
        avg_card.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
        
        ttk.Label(avg_card, text="Avg Strength", style='Muted.TLabel').pack()
        ttk.Label(avg_card, text=f"{avg_score:.1f}/10", font=("Segoe UI", 24, "bold"),
                 foreground=DarkTheme.strength_colors.get(
                     "Excellent" if avg_score >= 9 else
                     "Very Strong" if avg_score >= 7.5 else
                     "Strong" if avg_score >= 6 else
                     "Good" if avg_score >= 4.5 else
                     "Fair" if avg_score >= 3 else
                     "Weak" if avg_score >= 1.5 else "Very Weak",
                     DarkTheme.text_primary)).pack()
        
        # Strength breakdown
        breakdown_frame = ttk.LabelFrame(main_frame, text="Strength Breakdown", 
                                         style='Card.TFrame', padding="15")
        breakdown_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for scrolling if needed
        canvas = tk.Canvas(breakdown_frame, bg=DarkTheme.bg_medium, highlightthickness=0)
        scrollbar = ttk.Scrollbar(breakdown_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add strength categories
        for cat, count in cat_counts.items():
            if count > 0:
                frame = ttk.Frame(scrollable_frame)
                frame.pack(fill=tk.X, pady=3)
                
                # Color indicator
                color_box = tk.Canvas(frame, width=20, height=20, 
                                      bg=DarkTheme.strength_colors.get(cat, DarkTheme.accent_primary),
                                      highlightthickness=0)
                color_box.pack(side=tk.LEFT, padx=5)
                
                ttk.Label(frame, text=f"{cat}: {count} account(s)", 
                         font=DarkTheme.body_font).pack(side=tk.LEFT)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        ttk.Button(main_frame, text="Close", command=health_window.destroy).pack(pady=15)
    
    def show_about(self):
        """Show about dialog"""
        about_text = "🔐 GateKeeper Password Manager\n\n"
        about_text += "Version 2.5.0\n\n"
        about_text += "A secure password manager for students and professionals\n\n"
        about_text += "✨ Features:\n"
        about_text += "• Advanced password strength analysis (0-10 scale)\n"
        about_text += "• Password Inspector with actionable tips\n"
        about_text += "• Crack time estimation\n"
        about_text += "• Password reuse detection\n"
        about_text += "• Health dashboard with statistics\n"
        about_text += "• Built-in password generator\n"
        about_text += "• Dark mode for eye comfort\n\n"
        about_text += "© 2026 GateKeeper Team\n"
        about_text += "AI tools used responsibly to support learning"
        
        messagebox.showinfo("About GateKeeper", about_text)
    
    def show_storage_warning(self):
        """Show storage warning"""
        warning_text = "⚠️ LOCAL STORAGE ONLY ⚠️\n\n"
        warning_text += "Your accounts are saved ONLY on this device.\n"
        warning_text += f"Location: {os.path.abspath(FILENAME)}\n\n"
        warning_text += "If you delete this program or its files,\n"
        warning_text += "ALL your saved accounts will be PERMANENTLY LOST.\n\n"
        warning_text += "💾 To backup: Copy the accounts.json file to a safe location."
        
        messagebox.showwarning("Storage Information", warning_text)

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
