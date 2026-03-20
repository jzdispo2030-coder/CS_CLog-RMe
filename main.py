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
        self.root.geometry("1300x750")
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
        """Create minimal menu bar"""
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
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.text_primary,
                           activebackground=DarkTheme.accent_primary, activeforeground=DarkTheme.text_primary,
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
        tools_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.text_primary,
                            activebackground=DarkTheme.accent_primary, activeforeground=DarkTheme.text_primary,
                            borderwidth=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Password Reuse", command=self.show_password_reuse)
        tools_menu.add_command(label="Generate Password", command=self.show_password_generator)
        tools_menu.add_command(label="Health Dashboard", command=self.show_password_health)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=DarkTheme.bg_medium, fg=DarkTheme.text_primary,
                           activebackground=DarkTheme.accent_primary, activeforeground=DarkTheme.text_primary,
                           borderwidth=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Storage", command=self.show_storage_warning)
        
        # Keyboard shortcuts
        self.root.bind('<Command-n>', lambda e: self.add_account_dialog())
        self.root.bind('<Control-n>', lambda e: self.add_account_dialog())
    
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
        
        # ====================================================================
        # ACTION BUTTONS
        # ====================================================================
        actions_card = ttk.Frame(right_column, style='Card.TFrame', padding="20")
        actions_card.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(actions_card, text="Quick Actions", style='Subheading.TLabel').pack(anchor=tk.W, pady=(0, 15))
        
        # Button grid
        button_grid = ttk.Frame(actions_card)
        button_grid.pack(fill=tk.X)
        
        # Row 1
        row1 = ttk.Frame(button_grid)
        row1.pack(fill=tk.X, pady=3)
        
        self.inspect_btn = ModernButton(row1, text="🔍 Inspect", command=self.inspect_password,
                                        bg=DarkTheme.accent_info, width=110, height=35)
        self.inspect_btn.pack(side=tk.LEFT, padx=3)
        
        self.copy_btn = ModernButton(row1, text="📋 Copy", command=self.copy_password,
                                     bg=DarkTheme.accent_success, width=110, height=35)
        self.copy_btn.pack(side=tk.LEFT, padx=3)
        
        # Row 2
        row2 = ttk.Frame(button_grid)
        row2.pack(fill=tk.X, pady=3)
        
        self.toggle_btn = ModernButton(row2, text="👁️ Show", command=self.toggle_password,
                                       bg=DarkTheme.text_muted, width=110, height=35, state=tk.DISABLED)
        self.toggle_btn.pack(side=tk.LEFT, padx=3)
        
        self.edit_btn = ModernButton(row2, text="✏️ Edit", command=self.edit_account,
                                     bg=DarkTheme.accent_warning, width=110, height=35, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=3)
        
        # Row 3
        row3 = ttk.Frame(button_grid)
        row3.pack(fill=tk.X, pady=3)
        
        self.delete_btn = ModernButton(row3, text="🗑️ Delete", command=self.delete_account,
                                       bg=DarkTheme.accent_danger, width=226, height=35, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=3)
        
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
            "Check Tools menu for security reports"
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
        inspector.title(f"Inspector — {self.current_account}")
        inspector.geometry("550x600")
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
        
        # Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Analysis tab
        analysis = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(analysis, text="Analysis")
        
        ttk.Label(analysis, text="Character Types", style='Subheading.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
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
            f.pack(fill=tk.X, pady=3)
            ttk.Label(f, text=label, width=10).pack(side=tk.LEFT)
            status = "✓" if present else "✗"
            color = DarkTheme.accent_success if present else DarkTheme.accent_danger
            ttk.Label(f, text=status, foreground=color).pack(side=tk.LEFT)
        
        # Issues tab
        issues_tab = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(issues_tab, text="Issues")
        
        if feedback['issues']:
            for issue in feedback['issues']:
                f = ttk.Frame(issues_tab)
                f.pack(fill=tk.X, pady=3)
                ttk.Label(f, text="•", foreground=DarkTheme.accent_danger).pack(side=tk.LEFT, padx=(0, 5))
                ttk.Label(f, text=issue, wraplength=400).pack(side=tk.LEFT)
        else:
            ttk.Label(issues_tab, text="No issues found", 
                     foreground=DarkTheme.accent_success).pack(pady=20)
        
        # Close button
        btn_frame = ttk.Frame(main_frame, style='Deep.TFrame')
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="Close", command=inspector.destroy).pack()
    
    def add_account_dialog(self):
        """Open dialog to add a new account"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Account")
        dialog.geometry("480x550")
        dialog.configure(bg=DarkTheme.bg_deep)
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, style='Deep.TFrame', padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Create New Account", 
                 font=("Segoe UI", 16, "bold"),
                 foreground=DarkTheme.accent_primary).pack(anchor=tk.W, pady=(0, 20))
        
        # Form fields
        nickname_var = tk.StringVar()
        app_var = tk.StringVar()
        category_var = tk.StringVar(value="Personal")
        password_var = tk.StringVar()
        
        fields = [
            ("Nickname", nickname_var),
            ("App Name", app_var)
        ]
        
        for label, var in fields:
            ttk.Label(main_frame, text=label, style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
            entry = ModernEntry(main_frame, textvariable=var)
            entry.pack(fill=tk.X)
        
        # Category
        ttk.Label(main_frame, text="Category", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        category_combo = ttk.Combobox(main_frame, textvariable=category_var,
                                      values=["Academic", "Personal", "Internship", "Other"],
                                      state="readonly", font=DarkTheme.body_font)
        category_combo.pack(fill=tk.X)
        
        # Password
        ttk.Label(main_frame, text="Password", style='Muted.TLabel').pack(anchor=tk.W, pady=(10, 2))
        
        pwd_frame = ttk.Frame(main_frame)
        pwd_frame.pack(fill=tk.X)
        
        password_entry = ModernEntry(pwd_frame, textvariable=password_var, show="•")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(pwd_frame, text="Generate", 
                  command=lambda: password_var.set(generate_password()),
                  width=10).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(25, 0))
        
        def save():
            nickname = nickname_var.get().strip()
            app = app_var.get().strip()
            category = category_var.get()
            password = password_var.get().strip()
            
            if not nickname or not app or not password:
                messagebox.showerror("Error", "All fields are required")
                return
            
            if category.lower() in ["academic", "personal", "internship"]:
                category = category.lower().capitalize()
            else:
                category = "Other"
            
            if nickname in accounts:
                if not messagebox.askyesno("Duplicate", f"'{nickname}' already exists. Overwrite?"):
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
        
        ttk.Button(btn_frame, text="Save", command=save, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def edit_account(self):
        messagebox.showinfo("Edit", "Edit feature coming soon!")
    
    def delete_account(self):
        if not self.current_account:
            return
        
        if messagebox.askyesno("Delete Account", f"Delete '{self.current_account}'?\n\nThis cannot be undone."):
            del accounts[self.current_account]
            save_accounts()
            self.current_account = None
            self.refresh_list()
            self.status_var.set("✓ Account deleted")
    
    def show_password_reuse(self):
        reused = detect_password_reuse()
        if not reused:
            messagebox.showinfo("Password Reuse", "✅ No reused passwords found!")
        else:
            msg = f"⚠️ Found {len(reused)} reused passwords:\n\n"
            for item in reused:
                msg += f"• {item['password']} ({item['count']} accounts)\n"
            messagebox.showwarning("Password Reuse", msg)
    
    def show_password_generator(self):
        pwd = generate_password(24)
        feedback = get_password_feedback(pwd)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Generated Password")
        dialog.geometry("400x200")
        dialog.configure(bg=DarkTheme.bg_deep)
        dialog.transient(self.root)
        
        frame = ttk.Frame(dialog, style='Deep.TFrame', padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Strong Password Generated", 
                 font=DarkTheme.subheading_font).pack(pady=(0, 15))
        
        pwd_label = tk.Label(frame, text=pwd, font=("Consolas", 12),
                            bg=DarkTheme.bg_input, fg=DarkTheme.text_primary,
                            relief="solid", bd=1, padx=10, pady=10)
        pwd_label.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame, text=f"Strength: {feedback['category']}", 
                 foreground=DarkTheme.strength_colors.get(feedback['category'])).pack()
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(15, 0))
        
        ttk.Button(btn_frame, text="Copy", 
                  command=lambda: [pyperclip.copy(pwd), dialog.destroy()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_password_health(self):
        if not accounts:
            messagebox.showinfo("Health Dashboard", "No accounts to analyze")
            return
        
        scores = []
        for data in accounts.values():
            score, _ = check_password_strength(data['password'])
            scores.append(score)
        
        avg = sum(scores) / len(scores)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Health Dashboard")
        dialog.geometry("400x300")
        dialog.configure(bg=DarkTheme.bg_deep)
        dialog.transient(self.root)
        
        frame = ttk.Frame(dialog, style='Deep.TFrame', padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Password Health", 
                 font=DarkTheme.heading_font,
                 foreground=DarkTheme.accent_primary).pack(pady=(0, 20))
        
        ttk.Label(frame, text=f"Total Accounts: {len(accounts)}", 
                 font=DarkTheme.body_font).pack(anchor=tk.W, pady=2)
        ttk.Label(frame, text=f"Average Strength: {avg:.1f}/10", 
                 font=DarkTheme.body_font).pack(anchor=tk.W, pady=2)
        
        ttk.Button(frame, text="Close", command=dialog.destroy).pack(pady=20)
    
    def show_about(self):
        about_text = "GateKeeper 2.5\n\n"
        about_text += "A secure password manager\n"
        about_text += "for students and professionals\n\n"
        about_text += "• Dark mode for eye comfort\n"
        about_text += "• Advanced password analysis\n"
        about_text += "• Local storage for privacy"
        
        messagebox.showinfo("About GateKeeper", about_text)
    
    def show_storage_warning(self):
        msg = f"Accounts are stored locally at:\n{os.path.abspath(FILENAME)}\n\n"
        msg += "This file contains all your passwords.\n"
        msg += "Back it up to prevent data loss."
        messagebox.showwarning("Storage Information", msg)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    root = tk.Tk()
    app = GateKeeperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
