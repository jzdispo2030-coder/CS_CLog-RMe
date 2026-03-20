#AI tools were used responsibly to support learning and development, not to replace understanding.

import json
import os
import random
import string
import re
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import math

# Pyperclip is included directly in the project
import pyperclip

from password_checker import check_password_strength, get_password_feedback, estimate_crack_time

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_FILE = "gatekeeper_config.json"
WINDOW_CONFIG = "window_config.json"
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
# CONFIGURATION MANAGEMENT
# ============================================================================

class Config:
    DEFAULT_CONFIG = {
        'start_minimized': False,
        'show_tray_icon': True,
        'remember_window_position': True,
        'auto_save': True,
        'default_category': 'Personal'
    }
    
    @classmethod
    def load(cls):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return {**cls.DEFAULT_CONFIG, **config}
            except:
                return cls.DEFAULT_CONFIG.copy()
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save(cls, config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    
    @classmethod
    def load_window_position(cls):
        if os.path.exists(WINDOW_CONFIG):
            try:
                with open(WINDOW_CONFIG, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    @classmethod
    def save_window_position(cls, x, y, width, height):
        with open(WINDOW_CONFIG, 'w') as f:
            json.dump({'x': x, 'y': y, 'width': width, 'height': height}, f, indent=4)

# ============================================================================
# SYSTEM TRAY (OPTIONAL)
# ============================================================================

TRAY_AVAILABLE = False
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    pass

# ============================================================================
# MODERN DARK THEME
# ============================================================================

class ModernTheme:
    bg_primary = "#0a0c0f"
    bg_secondary = "#14181c"
    bg_card = "#1e2329"
    bg_input = "#23282e"
    bg_hover = "#2c313a"
    accent = "#5f9ea0"
    accent_success = "#2e8b57"
    accent_warning = "#cd853f"
    accent_danger = "#b22222"
    accent_info = "#4682b4"
    text_primary = "#e6edf3"
    text_secondary = "#9aa8b9"
    text_muted = "#6c7a8d"
    border = "#2e353e"
    
    strength_colors = {
        "Excellent": "#2e8b57", "Very Strong": "#3cb371", "Strong": "#4682b4",
        "Good": "#cd853f", "Fair": "#b8860b", "Weak": "#b22222", "Very Weak": "#8b0000"
    }
    
    heading_font = ("Segoe UI", 18, "bold")
    subheading_font = ("Segoe UI", 12, "bold")
    body_font = ("Segoe UI", 10)
    small_font = ("Segoe UI", 9)
    monospace_font = ("Consolas", 10) if os.name == 'nt' else ("Menlo", 10)

# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command=None, bg=ModernTheme.accent, fg=ModernTheme.text_primary,
                 width=120, height=35, radius=10, font=ModernTheme.body_font, state=tk.NORMAL, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=ModernTheme.bg_secondary)
        self.command = command
        self.text = text
        self.bg = bg
        self.fg = fg
        self.width = width
        self.height = height
        self.radius = radius
        self.font = font
        self.state = state
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.draw_button(bg if state == tk.NORMAL else ModernTheme.text_muted)
    
    def draw_button(self, color):
        self.delete("all")
        points = [self.radius, 0, self.width-self.radius, 0, self.width, 0, self.width, self.radius,
                  self.width, self.height-self.radius, self.width, self.height,
                  self.width-self.radius, self.height, self.radius, self.height,
                  0, self.height, 0, self.height-self.radius, 0, self.radius, 0, 0]
        self.create_polygon(points, smooth=True, fill=color, outline="")
        text_color = self.fg if self.state == tk.NORMAL else ModernTheme.text_muted
        self.create_text(self.width//2, self.height//2, text=self.text, fill=text_color, font=self.font)
    
    def on_enter(self, event):
        if self.state == tk.NORMAL:
            self.draw_button(self.lighten_color(self.bg))
    
    def on_leave(self, event):
        if self.state == tk.NORMAL:
            self.draw_button(self.bg)
        else:
            self.draw_button(ModernTheme.text_muted)
    
    def on_click(self, event):
        if self.state == tk.NORMAL and self.command:
            self.command()
    
    def lighten_color(self, color):
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = min(255, r + 30)
            g = min(255, g + 30)
            b = min(255, b + 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    def configure(self, **kwargs):
        if 'state' in kwargs:
            self.state = kwargs['state']
            self.draw_button(self.bg if self.state == tk.NORMAL else ModernTheme.text_muted)
        if 'text' in kwargs:
            self.text = kwargs['text']
            self.draw_button(self.bg if self.state == tk.NORMAL else ModernTheme.text_muted)

class StrengthCircle(tk.Canvas):
    def __init__(self, master, score=0, size=60, **kwargs):
        super().__init__(master, width=size, height=size, bg=ModernTheme.bg_card,
                        highlightthickness=0, **kwargs)
        self.size = size
        self.score = score
        self.draw()
    
    def draw(self):
        self.delete("all")
        center = self.size // 2
        radius = self.size // 2 - 5
        self.create_oval(center - radius, center - radius, center + radius, center + radius,
                        outline=ModernTheme.border, width=2, fill="")
        angle = (self.score / 10) * 360
        self.create_arc(center - radius, center - radius, center + radius, center + radius,
                       start=90, extent=-angle, outline=self.get_color(), width=3, style="arc")
        self.create_text(center, center, text=f"{self.score:.1f}", fill=ModernTheme.text_primary,
                        font=("Segoe UI", int(self.size * 0.2), "bold"))
    
    def get_color(self):
        if self.score >= 9: return ModernTheme.strength_colors["Excellent"]
        elif self.score >= 7.5: return ModernTheme.strength_colors["Very Strong"]
        elif self.score >= 6: return ModernTheme.strength_colors["Strong"]
        elif self.score >= 4.5: return ModernTheme.strength_colors["Good"]
        elif self.score >= 3: return ModernTheme.strength_colors["Fair"]
        elif self.score >= 1.5: return ModernTheme.strength_colors["Weak"]
        else: return ModernTheme.strength_colors["Very Weak"]
    
    def update_score(self, score):
        self.score = score
        self.draw()

class AccountCard(tk.Frame):
    def __init__(self, master, nickname, data, on_click=None, **kwargs):
        super().__init__(master, bg=ModernTheme.bg_card, relief="flat", bd=1,
                        highlightbackground=ModernTheme.border, highlightthickness=1, **kwargs)
        self.nickname = nickname
        self.data = data
        self.on_click = on_click
        self.pack(fill=tk.X, pady=5, padx=10)
        self.bind("<Button-1>", self.click)
        self.setup_ui()
    
    def setup_ui(self):
        feedback = get_password_feedback(self.data['password'])
        circle = StrengthCircle(self, score=feedback['score'], size=50)
        circle.pack(side=tk.LEFT, padx=10, pady=10)
        
        info_frame = tk.Frame(self, bg=ModernTheme.bg_card)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        name_label = tk.Label(info_frame, text=self.nickname, bg=ModernTheme.bg_card,
                             fg=ModernTheme.text_primary, font=ModernTheme.subheading_font, anchor=tk.W)
        name_label.pack(anchor=tk.W)
        
        category_label = tk.Label(info_frame, text=self.data['category'], bg=ModernTheme.bg_card,
                                 fg=ModernTheme.text_muted, font=ModernTheme.small_font, anchor=tk.W)
        category_label.pack(anchor=tk.W)
        
        app_label = tk.Label(info_frame, text=f"📱 {self.data['app']}", bg=ModernTheme.bg_card,
                            fg=ModernTheme.text_secondary, font=ModernTheme.small_font, anchor=tk.W)
        app_label.pack(anchor=tk.W)
        
        right_frame = tk.Frame(self, bg=ModernTheme.bg_card)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        created = self.data.get('created', 'Unknown').split()[0]
        date_label = tk.Label(right_frame, text=f"📅 {created}", bg=ModernTheme.bg_card,
                             fg=ModernTheme.text_muted, font=ModernTheme.small_font)
        date_label.pack(anchor=tk.E)
        
        strength_text = f"{feedback['category']} — {feedback['score']:.1f}/10"
        strength_label = tk.Label(right_frame, text=strength_text, bg=ModernTheme.bg_card,
                                  fg=ModernTheme.strength_colors.get(feedback['category'], ModernTheme.text_secondary),
                                  font=ModernTheme.small_font)
        strength_label.pack(anchor=tk.E)
    
    def click(self, event):
        if self.on_click:
            self.on_click(self.nickname)

# ============================================================================
# SPLASH SCREEN
# ============================================================================

class SplashScreen(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry("450x300")
        self.configure(bg=ModernTheme.bg_secondary)
        self.overrideredirect(True)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(self, bg=ModernTheme.bg_secondary)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        logo_label = tk.Label(main_frame, text="🔐", bg=ModernTheme.bg_secondary,
                              fg=ModernTheme.accent, font=("Segoe UI", 64))
        logo_label.pack(pady=(40, 10))
        
        name_label = tk.Label(main_frame, text="GateKeeper", bg=ModernTheme.bg_secondary,
                              fg=ModernTheme.text_primary, font=("Segoe UI", 24, "bold"))
        name_label.pack()
        
        tagline_label = tk.Label(main_frame, text="secure password manager", 
                                 bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted,
                                 font=("Segoe UI", 11))
        tagline_label.pack(pady=(5, 20))
        
        self.progress = ttk.Progressbar(main_frame, length=300, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        self.update()
    
    def close(self):
        self.progress.stop()
        self.destroy()

# ============================================================================
# DIALOGS
# ============================================================================

class PasswordInspector(tk.Toplevel):
    """Detailed password inspector with multiple tabs"""
    def __init__(self, parent, nickname, password):
        super().__init__(parent)
        self.parent = parent
        self.nickname = nickname
        self.password = password
        self.feedback = get_password_feedback(password)
        
        self.title(f"Password Inspector — {nickname}")
        self.geometry("600x550")
        self.configure(bg=ModernTheme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (600 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (550 // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = tk.Frame(self, bg=ModernTheme.bg_secondary, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
        header.pack(fill=tk.X, pady=(0, 15))
        
        score_color = ModernTheme.strength_colors.get(self.feedback['category'], ModernTheme.accent)
        score_label = tk.Label(header, text=f"{self.feedback['score']:.1f}", 
                               font=("Segoe UI", 32, "bold"), fg=score_color, bg=ModernTheme.bg_secondary)
        score_label.pack(side=tk.LEFT, padx=(0, 20))
        
        info = tk.Frame(header, bg=ModernTheme.bg_secondary)
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(info, text=self.feedback['category'], font=("Segoe UI", 14, "bold"),
                fg=score_color, bg=ModernTheme.bg_secondary).pack(anchor=tk.W)
        tk.Label(info, text=f"Length: {len(self.password)} characters", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.text_muted).pack(anchor=tk.W)
        tk.Label(info, text=f"Crack time: {estimate_crack_time(self.password)}", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.text_muted).pack(anchor=tk.W)
        
        # Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Character Analysis
        analysis_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(analysis_tab, text="Character Analysis")
        
        has_lower = bool(re.search(r"[a-z]", self.password))
        has_upper = bool(re.search(r"[A-Z]", self.password))
        has_digit = bool(re.search(r"[0-9]", self.password))
        has_symbol = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", self.password))
        
        types = [("Lowercase (a-z)", has_lower), ("Uppercase (A-Z)", has_upper),
                 ("Numbers (0-9)", has_digit), ("Symbols (!@#$%)", has_symbol)]
        
        for label, present in types:
            f = tk.Frame(analysis_tab, bg=ModernTheme.bg_secondary)
            f.pack(fill=tk.X, pady=3, padx=10)
            tk.Label(f, text=label, width=18, bg=ModernTheme.bg_secondary,
                    fg=ModernTheme.text_secondary).pack(side=tk.LEFT)
            status = "✓ Yes" if present else "✗ No"
            color = ModernTheme.accent_success if present else ModernTheme.accent_danger
            tk.Label(f, text=status, bg=ModernTheme.bg_secondary, fg=color).pack(side=tk.LEFT)
        
        # Tab 2: Strengths
        strengths_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(strengths_tab, text="Strengths")
        
        strengths_text = tk.Text(strengths_tab, bg=ModernTheme.bg_input, fg=ModernTheme.accent_success,
                                 bd=0, padx=10, pady=10, font=ModernTheme.small_font, wrap=tk.WORD)
        strengths_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        if self.feedback['strengths']:
            for s in self.feedback['strengths']:
                strengths_text.insert(tk.END, f"✓ {s}\n")
        else:
            strengths_text.insert(tk.END, "No notable strengths found")
        strengths_text.config(state=tk.DISABLED)
        
        # Tab 3: Issues & Fixes
        issues_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(issues_tab, text="Issues & Fixes")
        
        issues_text = tk.Text(issues_tab, bg=ModernTheme.bg_input, fg=ModernTheme.accent_danger,
                              bd=0, padx=10, pady=10, font=ModernTheme.small_font, wrap=tk.WORD)
        issues_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if self.feedback['issues']:
            for issue in self.feedback['issues']:
                issues_text.insert(tk.END, f"⚠️ {issue}\n")
                if "uppercase" in issue.lower():
                    issues_text.insert(tk.END, "   💡 Fix: Add capital letters (A-Z)\n")
                elif "lowercase" in issue.lower():
                    issues_text.insert(tk.END, "   💡 Fix: Add lowercase letters (a-z)\n")
                elif "number" in issue.lower():
                    issues_text.insert(tk.END, "   💡 Fix: Add numbers (0-9)\n")
                elif "symbol" in issue.lower():
                    issues_text.insert(tk.END, "   💡 Fix: Add symbols (!@#$%)\n")
                elif "short" in issue.lower():
                    issues_text.insert(tk.END, "   💡 Fix: Make password longer (12+ chars)\n")
                issues_text.insert(tk.END, "\n")
        else:
            issues_text.insert(tk.END, "✅ No issues found!")
        issues_text.config(state=tk.DISABLED)
        
        # Tab 4: Suggestions
        suggestions_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(suggestions_tab, text="Suggestions")
        
        suggestions_text = tk.Text(suggestions_tab, bg=ModernTheme.bg_input, fg=ModernTheme.accent_info,
                                   bd=0, padx=10, pady=10, font=ModernTheme.small_font, wrap=tk.WORD)
        suggestions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        suggestions = []
        if len(self.password) < 12:
            suggestions.append("• Increase length to 12+ characters")
        if len(self.password) < 16:
            suggestions.append("• For excellent security, use 16+ characters")
        if not has_upper or not has_lower:
            suggestions.append("• Mix uppercase and lowercase letters")
        if not has_digit:
            suggestions.append("• Add numbers (0-9)")
        if not has_symbol:
            suggestions.append("• Add symbols (!@#$%)")
        if suggestions:
            for s in suggestions:
                suggestions_text.insert(tk.END, f"💡 {s}\n")
        else:
            suggestions_text.insert(tk.END, "✨ Your password looks great! No suggestions needed.")
        suggestions_text.config(state=tk.DISABLED)
        
        # Tab 5: Quick Actions
        actions_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(actions_tab, text="Quick Actions")
        
        action_frame = tk.Frame(actions_tab, bg=ModernTheme.bg_secondary)
        action_frame.pack(expand=True, pady=30)
        
        def generate_new():
            new_pwd = generate_password(20)
            SuggestPasswordDialog(self, new_pwd, self.parent.update_account_password)
        
        def copy_this():
            pyperclip.copy(self.password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        
        RoundedButton(action_frame, text="🔄 Generate New Password", command=generate_new,
                     bg=ModernTheme.accent_info, width=250, height=40).pack(pady=5)
        RoundedButton(action_frame, text="📋 Copy This Password", command=copy_this,
                     bg=ModernTheme.accent_success, width=250, height=40).pack(pady=5)
        RoundedButton(action_frame, text="✏️ Edit This Account", command=lambda: [self.destroy(), self.parent.edit_account()],
                     bg=ModernTheme.accent_warning, width=250, height=40).pack(pady=5)
        
        # Close button
        RoundedButton(main_frame, text="Close", command=self.destroy, bg=ModernTheme.bg_input, width=120, height=35).pack(pady=15)

class SuggestPasswordDialog(tk.Toplevel):
    """Dialog to suggest better passwords"""
    def __init__(self, parent, current_password, on_select):
        super().__init__(parent)
        self.parent = parent
        self.current_password = current_password
        self.on_select = on_select
        
        self.title("Password Suggestions")
        self.geometry("500x400")
        self.configure(bg=ModernTheme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (500 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = tk.Frame(self, bg=ModernTheme.bg_secondary, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Suggested Strong Passwords", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.accent, font=ModernTheme.heading_font).pack(pady=(0, 15))
        
        suggestions = [generate_password(16) for _ in range(3)]
        
        for i, pwd in enumerate(suggestions):
            feedback = get_password_feedback(pwd)
            frame = tk.Frame(main_frame, bg=ModernTheme.bg_card, relief="flat", bd=1,
                            highlightbackground=ModernTheme.border, highlightthickness=1)
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame, text=f"Option {i+1}", bg=ModernTheme.bg_card,
                    fg=ModernTheme.text_secondary, font=ModernTheme.small_font).pack(anchor=tk.W, padx=10, pady=(5, 0))
            
            tk.Label(frame, text=pwd, bg=ModernTheme.bg_card, fg=ModernTheme.text_primary,
                    font=ModernTheme.monospace_font).pack(side=tk.LEFT, padx=10, pady=5)
            
            strength_text = f"{feedback['category']} ({feedback['score']:.1f}/10)"
            tk.Label(frame, text=strength_text, bg=ModernTheme.bg_card,
                    fg=ModernTheme.strength_colors.get(feedback['category'])).pack(side=tk.LEFT, padx=10)
            
            RoundedButton(frame, text="Use This", command=lambda p=pwd: self.on_select(p),
                         bg=ModernTheme.accent, width=80, height=30, radius=6).pack(side=tk.RIGHT, padx=5, pady=5)
        
        RoundedButton(main_frame, text="Cancel", command=self.destroy, bg=ModernTheme.bg_input, width=100, height=35).pack(pady=15)

class ReuseReportWindow(tk.Toplevel):
    """Detailed password reuse report window"""
    def __init__(self, parent, reused):
        super().__init__(parent)
        self.parent = parent
        self.reused = reused
        
        self.title("Password Reuse Report")
        self.geometry("600x500")
        self.configure(bg=ModernTheme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (600 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = tk.Frame(self, bg=ModernTheme.bg_secondary, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Password Reuse Report", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.accent, font=ModernTheme.heading_font).pack(pady=(0, 15))
        
        tk.Label(main_frame, text=f"Found {len(self.reused)} reused password(s):", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.text_secondary).pack(anchor=tk.W, pady=(0, 10))
        
        # Scrollable text area
        text_frame = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, wrap=tk.WORD,
                              bg=ModernTheme.bg_input, fg=ModernTheme.text_primary,
                              bd=0, padx=10, pady=10, font=ModernTheme.body_font)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        for i, item in enumerate(self.reused, 1):
            text_widget.insert(tk.END, f"\n{i}. Password: {item['password']}\n", "password")
            text_widget.tag_config("password", foreground=ModernTheme.accent_danger, font=ModernTheme.monospace_font)
            text_widget.insert(tk.END, f"   Used in {item['count']} accounts:\n")
            for acc in item['accounts']:
                text_widget.insert(tk.END, f"   • {acc} ({accounts[acc]['app']})\n")
            text_widget.insert(tk.END, "\n" + "─"*50 + "\n")
        
        text_widget.config(state=tk.DISABLED)
        
        RoundedButton(main_frame, text="Close", command=self.destroy, bg=ModernTheme.bg_input, width=120, height=35).pack(pady=15)

class HealthDashboardWindow(tk.Toplevel):
    """Detailed password health dashboard"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.title("Password Health Dashboard")
        self.geometry("550x500")
        self.configure(bg=ModernTheme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (550 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = tk.Frame(self, bg=ModernTheme.bg_secondary, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Password Health Dashboard", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.accent, font=ModernTheme.heading_font).pack(pady=(0, 20))
        
        # Calculate statistics
        total = len(accounts)
        scores = []
        categories = []
        
        for data in accounts.values():
            fb = get_password_feedback(data['password'])
            scores.append(fb['score'])
            categories.append(fb['category'])
        
        avg_score = sum(scores) / total if total > 0 else 0
        
        cat_counts = {
            "Excellent": categories.count("Excellent"),
            "Very Strong": categories.count("Very Strong"),
            "Strong": categories.count("Strong"),
            "Good": categories.count("Good"),
            "Fair": categories.count("Fair"),
            "Weak": categories.count("Weak"),
            "Very Weak": categories.count("Very Weak")
        }
        
        # Stats cards
        stats_frame = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        total_card = tk.Frame(stats_frame, bg=ModernTheme.bg_card, relief="flat", bd=1,
                             highlightbackground=ModernTheme.border, highlightthickness=1)
        total_card.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Label(total_card, text="Total Accounts", bg=ModernTheme.bg_card, fg=ModernTheme.text_muted).pack(pady=5)
        tk.Label(total_card, text=str(total), bg=ModernTheme.bg_card, fg=ModernTheme.text_primary,
                font=("Segoe UI", 24, "bold")).pack(pady=5)
        
        avg_card = tk.Frame(stats_frame, bg=ModernTheme.bg_card, relief="flat", bd=1,
                           highlightbackground=ModernTheme.border, highlightthickness=1)
        avg_card.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
        tk.Label(avg_card, text="Avg Strength", bg=ModernTheme.bg_card, fg=ModernTheme.text_muted).pack(pady=5)
        
        if avg_score >= 8:
            color = ModernTheme.strength_colors["Excellent"]
        elif avg_score >= 6:
            color = ModernTheme.strength_colors["Strong"]
        elif avg_score >= 4:
            color = ModernTheme.strength_colors["Good"]
        else:
            color = ModernTheme.strength_colors["Weak"]
        
        tk.Label(avg_card, text=f"{avg_score:.1f}/10", bg=ModernTheme.bg_card, fg=color,
                font=("Segoe UI", 24, "bold")).pack(pady=5)
        
        # Strength breakdown
        breakdown_frame = tk.LabelFrame(main_frame, text="Strength Breakdown", bg=ModernTheme.bg_secondary,
                                        fg=ModernTheme.text_secondary, font=ModernTheme.small_font)
        breakdown_frame.pack(fill=tk.BOTH, expand=True)
        
        for cat, count in cat_counts.items():
            if count > 0:
                f = tk.Frame(breakdown_frame, bg=ModernTheme.bg_secondary)
                f.pack(fill=tk.X, pady=3, padx=10)
                
                color_box = tk.Canvas(f, width=20, height=20, bg=ModernTheme.strength_colors.get(cat, ModernTheme.accent),
                                      highlightthickness=0)
                color_box.pack(side=tk.LEFT, padx=5)
                
                tk.Label(f, text=f"{cat}: {count} account(s)", bg=ModernTheme.bg_secondary,
                        fg=ModernTheme.text_secondary).pack(side=tk.LEFT)
        
        # Recommendation
        rec_frame = tk.LabelFrame(main_frame, text="Recommendation", bg=ModernTheme.bg_secondary,
                                  fg=ModernTheme.text_secondary, font=ModernTheme.small_font)
        rec_frame.pack(fill=tk.X, pady=10)
        
        if avg_score >= 8:
            rec = "🎉 Excellent overall security! Keep up the good work."
        elif avg_score >= 6:
            rec = "👍 Good security. Consider updating weaker passwords for even better protection."
        elif avg_score >= 4:
            rec = "⚠️ Fair security. Review and update weak passwords regularly."
        else:
            rec = "🔴 Poor security! Update weak passwords immediately and enable 2FA where possible."
        
        tk.Label(rec_frame, text=rec, bg=ModernTheme.bg_secondary, fg=ModernTheme.text_primary,
                wraplength=450, justify=tk.LEFT).pack(pady=10, padx=10)
        
        RoundedButton(main_frame, text="Close", command=self.destroy, bg=ModernTheme.bg_input, width=120, height=35).pack(pady=15)

class ShortcutsWindow(tk.Toplevel):
    """Keyboard shortcuts help window"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Keyboard Shortcuts")
        self.geometry("450x450")
        self.configure(bg=ModernTheme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (450 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (450 // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = tk.Frame(self, bg=ModernTheme.bg_secondary, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Keyboard Shortcuts", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.accent, font=ModernTheme.heading_font).pack(pady=(0, 15))
        
        shortcuts = [
            ("⌘N / Ctrl+N", "New Account"),
            ("⌘, / Ctrl+,", "Preferences"),
            ("⌘H / Ctrl+H", "Hide to Tray"),
            ("⌘Q / Ctrl+Q", "Quit Application"),
            ("⌘? / Ctrl+?", "Show Shortcuts"),
            ("Esc", "Close Dialog"),
            ("Enter", "Save/Confirm"),
        ]
        
        for key, action in shortcuts:
            frame = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
            frame.pack(fill=tk.X, pady=3)
            
            key_label = tk.Label(frame, text=key, bg=ModernTheme.bg_input, fg=ModernTheme.accent_info,
                                 font=("Segoe UI", 9, "bold"), padx=8, pady=4)
            key_label.pack(side=tk.LEFT)
            
            tk.Label(frame, text=action, bg=ModernTheme.bg_secondary,
                    fg=ModernTheme.text_secondary).pack(side=tk.LEFT, padx=(15, 0))
        
        RoundedButton(main_frame, text="Close", command=self.destroy, bg=ModernTheme.bg_input, width=100, height=35).pack(pady=15)

class PreferencesWindow(tk.Toplevel):
    """User preferences window"""
    def __init__(self, parent, config, on_save):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.on_save = on_save
        
        self.title("Preferences")
        self.geometry("400x400")
        self.configure(bg=ModernTheme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (400 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        main_frame = tk.Frame(self, bg=ModernTheme.bg_secondary, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Preferences", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.accent, font=ModernTheme.heading_font).pack(anchor=tk.W, pady=(0, 20))
        
        # Start minimized
        self.min_var = tk.BooleanVar(value=self.config.get('start_minimized', False))
        tk.Checkbutton(main_frame, text="Start minimized to system tray",
                      variable=self.min_var, bg=ModernTheme.bg_secondary,
                      fg=ModernTheme.text_primary, selectcolor=ModernTheme.bg_secondary).pack(anchor=tk.W, pady=5)
        
        # Show tray icon
        self.tray_var = tk.BooleanVar(value=self.config.get('show_tray_icon', True))
        tk.Checkbutton(main_frame, text="Show system tray icon",
                      variable=self.tray_var, bg=ModernTheme.bg_secondary,
                      fg=ModernTheme.text_primary, selectcolor=ModernTheme.bg_secondary).pack(anchor=tk.W, pady=5)
        
        # Remember window position
        self.pos_var = tk.BooleanVar(value=self.config.get('remember_window_position', True))
        tk.Checkbutton(main_frame, text="Remember window position",
                      variable=self.pos_var, bg=ModernTheme.bg_secondary,
                      fg=ModernTheme.text_primary, selectcolor=ModernTheme.bg_secondary).pack(anchor=tk.W, pady=5)
        
        # Auto save
        self.save_var = tk.BooleanVar(value=self.config.get('auto_save', True))
        tk.Checkbutton(main_frame, text="Automatically save on exit",
                      variable=self.save_var, bg=ModernTheme.bg_secondary,
                      fg=ModernTheme.text_primary, selectcolor=ModernTheme.bg_secondary).pack(anchor=tk.W, pady=5)
        
        # Default category
        tk.Label(main_frame, text="Default Category", bg=ModernTheme.bg_secondary,
                fg=ModernTheme.text_muted).pack(anchor=tk.W, pady=(15, 5))
        
        self.cat_var = tk.StringVar(value=self.config.get('default_category', 'Personal'))
        cat_combo = ttk.Combobox(main_frame, textvariable=self.cat_var,
                                 values=["Academic", "Personal", "Internship", "Other"],
                                 state="readonly")
        cat_combo.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save():
            new_config = {
                'start_minimized': self.min_var.get(),
                'show_tray_icon': self.tray_var.get(),
                'remember_window_position': self.pos_var.get(),
                'auto_save': self.save_var.get(),
                'default_category': self.cat_var.get()
            }
            self.on_save(new_config)
            self.destroy()
        
        RoundedButton(btn_frame, text="Save", command=save, bg=ModernTheme.accent, width=100, height=35).pack(side=tk.LEFT, padx=5)
        RoundedButton(btn_frame, text="Cancel", command=self.destroy, bg=ModernTheme.bg_input, width=100, height=35).pack(side=tk.LEFT, padx=5)

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class GateKeeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GateKeeper")
        self.root.geometry("1400x800")
        self.root.configure(bg=ModernTheme.bg_primary)
        self.root.minsize(1200, 600)
        self.root.overrideredirect(True)
        
        # Load configuration
        self.config = Config.load()
        
        # Load window position
        self.load_window_position()
        
        self.current_account = None
        self.show_passwords = False
        
        # System tray
        self.tray = None
        if TRAY_AVAILABLE and self.config.get('show_tray_icon', True):
            self.setup_tray()
        
        self.setup_custom_titlebar()
        self.setup_ui()
        self.setup_shortcuts()
        self.refresh_accounts()
    
    def load_window_position(self):
        if self.config.get('remember_window_position', True):
            pos = Config.load_window_position()
            if pos:
                self.root.geometry(f"{pos['width']}x{pos['height']}+{pos['x']}+{pos['y']}")
    
    def save_window_position(self):
        if self.config.get('remember_window_position', True):
            Config.save_window_position(
                self.root.winfo_x(), self.root.winfo_y(),
                self.root.winfo_width(), self.root.winfo_height()
            )
    
    def setup_tray(self):
        """Setup system tray icon"""
        img = Image.new('RGB', (64, 64), color=ModernTheme.bg_secondary)
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 25, 44, 45], fill=ModernTheme.accent)
        draw.rectangle([24, 15, 40, 25], fill=ModernTheme.accent)
        
        menu = pystray.Menu(
            pystray.MenuItem("Show GateKeeper", self.show_window),
            pystray.MenuItem("New Account", self.add_account_dialog),
            pystray.MenuItem("Generate Password", self.show_password_generator),
            pystray.MenuItem("Exit", self.quit_app)
        )
        
        self.tray = pystray.Icon("gatekeeper", img, "GateKeeper", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()
    
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def minimize_to_tray(self):
        if self.tray and self.config.get('show_tray_icon', True):
            self.root.withdraw()
        else:
            self.root.iconify()
    
    def quit_app(self):
        self.save_window_position()
        if self.tray:
            self.tray.stop()
        self.root.quit()
    
    def setup_custom_titlebar(self):
        titlebar = tk.Frame(self.root, bg=ModernTheme.bg_secondary, height=40)
        titlebar.pack(fill=tk.X, side=tk.TOP)
        titlebar.pack_propagate(False)
        
        icon_label = tk.Label(titlebar, text="🔐", bg=ModernTheme.bg_secondary, fg=ModernTheme.accent, font=("Segoe UI", 12))
        icon_label.pack(side=tk.LEFT, padx=(10, 5))
        
        title_label = tk.Label(titlebar, text="GateKeeper", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_primary, font=("Segoe UI", 11, "bold"))
        title_label.pack(side=tk.LEFT)
        
        controls_frame = tk.Frame(titlebar, bg=ModernTheme.bg_secondary)
        controls_frame.pack(side=tk.RIGHT, padx=10)
        
        min_btn = tk.Button(controls_frame, text="─", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_primary,
                           bd=0, font=("Segoe UI", 12), activebackground=ModernTheme.bg_hover, command=self.minimize_to_tray)
        min_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(controls_frame, text="✕", bg=ModernTheme.bg_secondary, fg=ModernTheme.accent_danger,
                             bd=0, font=("Segoe UI", 12), activebackground=ModernTheme.accent_danger,
                             activeforeground="white", command=self.quit_app)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        for widget in [titlebar, icon_label, title_label]:
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.on_move)
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def setup_shortcuts(self):
        self.root.bind('<Command-n>', lambda e: self.add_account_dialog())
        self.root.bind('<Control-n>', lambda e: self.add_account_dialog())
        self.root.bind('<Command-comma>', lambda e: self.show_preferences())
        self.root.bind('<Control-comma>', lambda e: self.show_preferences())
        self.root.bind('<Command-h>', lambda e: self.minimize_to_tray())
        self.root.bind('<Control-h>', lambda e: self.minimize_to_tray())
        self.root.bind('<Command-slash>', lambda e: self.show_shortcuts())
        self.root.bind('<Control-slash>', lambda e: self.show_shortcuts())
        self.root.bind('<Command-q>', lambda e: self.quit_app())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
    
    def setup_ui(self):
        main_container = tk.Frame(self.root, bg=ModernTheme.bg_primary)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # LEFT SIDEBAR
        sidebar = tk.Frame(main_container, bg=ModernTheme.bg_secondary, width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        logo_frame = tk.Frame(sidebar, bg=ModernTheme.bg_secondary, height=80)
        logo_frame.pack(fill=tk.X, pady=(20, 10))
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="🔐 GateKeeper", bg=ModernTheme.bg_secondary, fg=ModernTheme.accent, font=ModernTheme.heading_font).pack()
        tk.Label(logo_frame, text="secure password manager", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted, font=ModernTheme.small_font).pack()
        
        # Search
        search_frame = tk.Frame(sidebar, bg=ModernTheme.bg_secondary, padx=15, pady=10)
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="🔍 Search accounts", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted, font=ModernTheme.small_font).pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_accounts())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(fill=tk.X, pady=(5, 0))
        
        # Categories
        categories_frame = tk.Frame(sidebar, bg=ModernTheme.bg_secondary, padx=15, pady=10)
        categories_frame.pack(fill=tk.X)
        tk.Label(categories_frame, text="📂 Categories", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted, font=ModernTheme.small_font).pack(anchor=tk.W)
        categories = ["All", "Academic", "Personal", "Internship", "Other"]
        self.category_var = tk.StringVar(value="All")
        for cat in categories:
            rb = tk.Radiobutton(categories_frame, text=cat, variable=self.category_var, value=cat,
                               bg=ModernTheme.bg_secondary, fg=ModernTheme.text_secondary,
                               selectcolor=ModernTheme.bg_secondary, activebackground=ModernTheme.bg_secondary,
                               command=self.refresh_accounts)
            rb.pack(anchor=tk.W, pady=2)
        
        # Tools section
        tools_frame = tk.Frame(sidebar, bg=ModernTheme.bg_secondary, padx=15, pady=10)
        tools_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Label(tools_frame, text="🛠️ Tools", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted, font=ModernTheme.small_font).pack(anchor=tk.W)
        
        RoundedButton(tools_frame, text="Password Inspector", command=self.show_inspector, bg=ModernTheme.bg_input, width=250, height=32, radius=6).pack(pady=2)
        RoundedButton(tools_frame, text="Password Generator", command=self.show_password_generator, bg=ModernTheme.bg_input, width=250, height=32, radius=6).pack(pady=2)
        RoundedButton(tools_frame, text="Reuse Check", command=self.show_reuse_report, bg=ModernTheme.bg_input, width=250, height=32, radius=6).pack(pady=2)
        RoundedButton(tools_frame, text="Health Dashboard", command=self.show_health_dashboard, bg=ModernTheme.bg_input, width=250, height=32, radius=6).pack(pady=2)
        RoundedButton(tools_frame, text="Shortcuts", command=self.show_shortcuts, bg=ModernTheme.bg_input, width=250, height=32, radius=6).pack(pady=2)
        
        # Add account button
        add_btn_frame = tk.Frame(sidebar, bg=ModernTheme.bg_secondary, padx=15, pady=20)
        add_btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        RoundedButton(add_btn_frame, text="+ New Account", command=self.add_account_dialog, bg=ModernTheme.accent, width=250, height=40, radius=8).pack()
        
        # MAIN CONTENT - Account Cards
        main_content = tk.Frame(main_container, bg=ModernTheme.bg_primary)
        main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(main_content, bg=ModernTheme.bg_primary, height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="Your Vault", bg=ModernTheme.bg_primary, fg=ModernTheme.text_primary, font=ModernTheme.heading_font).pack(side=tk.LEFT)
        self.stats_label = tk.Label(header_frame, text=f"{len(accounts)} accounts", bg=ModernTheme.bg_primary, fg=ModernTheme.text_muted, font=ModernTheme.body_font)
        self.stats_label.pack(side=tk.RIGHT)
        
        # Scrollable cards container
        cards_container = tk.Frame(main_content, bg=ModernTheme.bg_primary)
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        canvas = tk.Canvas(cards_container, bg=ModernTheme.bg_primary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(cards_container, orient="vertical", command=canvas.yview)
        self.cards_frame = tk.Frame(canvas, bg=ModernTheme.bg_primary)
        self.cards_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # RIGHT DETAIL PANEL with TABS
        detail_panel = tk.Frame(main_container, bg=ModernTheme.bg_secondary, width=340)
        detail_panel.pack(side=tk.RIGHT, fill=tk.Y)
        detail_panel.pack_propagate(False)
        
        # Account header
        header_frame = tk.Frame(detail_panel, bg=ModernTheme.bg_secondary, height=70)
        header_frame.pack(fill=tk.X, pady=(15, 5))
        header_frame.pack_propagate(False)
        self.panel_title = tk.Label(header_frame, text="Select an account", bg=ModernTheme.bg_secondary,
                                    fg=ModernTheme.text_primary, font=ModernTheme.subheading_font)
        self.panel_title.pack()
        
        # Strength circle and info
        strength_row = tk.Frame(detail_panel, bg=ModernTheme.bg_secondary)
        strength_row.pack(pady=10)
        self.panel_circle = StrengthCircle(strength_row, score=0, size=70)
        self.panel_circle.pack(side=tk.LEFT, padx=10)
        
        info_col = tk.Frame(strength_row, bg=ModernTheme.bg_secondary)
        info_col.pack(side=tk.LEFT, padx=10)
        self.panel_strength_label = tk.Label(info_col, text="", bg=ModernTheme.bg_secondary,
                                            fg=ModernTheme.text_secondary, font=ModernTheme.body_font)
        self.panel_strength_label.pack(anchor=tk.W)
        self.panel_crack_label = tk.Label(info_col, text="", bg=ModernTheme.bg_secondary,
                                         fg=ModernTheme.text_muted, font=ModernTheme.small_font)
        self.panel_crack_label.pack(anchor=tk.W)
        
        # Action buttons
        btn_row = tk.Frame(detail_panel, bg=ModernTheme.bg_secondary)
        btn_row.pack(pady=10)
        self.show_btn = RoundedButton(btn_row, text="Show", command=self.toggle_password, bg=ModernTheme.bg_input, width=80, height=32, radius=6)
        self.show_btn.pack(side=tk.LEFT, padx=5)
        self.copy_btn = RoundedButton(btn_row, text="Copy", command=self.copy_password, bg=ModernTheme.bg_input, width=80, height=32, radius=6)
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        self.edit_btn = RoundedButton(btn_row, text="Edit", command=self.edit_account, bg=ModernTheme.bg_input, width=80, height=32, radius=6)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = RoundedButton(btn_row, text="Delete", command=self.delete_account, bg=ModernTheme.accent_danger, width=80, height=32, radius=6)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Disable buttons initially
        for btn in [self.show_btn, self.copy_btn, self.edit_btn, self.delete_btn]:
            btn.configure(state=tk.DISABLED)
        
        # TABS for organized content
        notebook = ttk.Notebook(detail_panel)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Details
        details_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(details_tab, text="Details")
        self.panel_details = tk.Text(details_tab, height=6, bg=ModernTheme.bg_input, fg=ModernTheme.text_primary,
                                     bd=0, padx=10, pady=10, font=ModernTheme.monospace_font, wrap=tk.WORD)
        self.panel_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.panel_details.config(state=tk.DISABLED)
        
        # Tab 2: Strengths
        strengths_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(strengths_tab, text="Strengths")
        self.panel_strengths = tk.Text(strengths_tab, height=4, bg=ModernTheme.bg_input, fg=ModernTheme.accent_success,
                                       bd=0, padx=10, pady=10, font=ModernTheme.small_font, wrap=tk.WORD)
        self.panel_strengths.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.panel_strengths.config(state=tk.DISABLED)
        
        # Tab 3: Issues
        issues_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(issues_tab, text="Issues")
        self.panel_issues = tk.Text(issues_tab, height=4, bg=ModernTheme.bg_input, fg=ModernTheme.accent_danger,
                                    bd=0, padx=10, pady=10, font=ModernTheme.small_font, wrap=tk.WORD)
        self.panel_issues.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.panel_issues.config(state=tk.DISABLED)
        
        # Tab 4: Suggestions
        suggestions_tab = tk.Frame(notebook, bg=ModernTheme.bg_secondary)
        notebook.add(suggestions_tab, text="Suggestions")
        self.panel_suggestions = tk.Text(suggestions_tab, height=4, bg=ModernTheme.bg_input, fg=ModernTheme.accent_info,
                                         bd=0, padx=10, pady=10, font=ModernTheme.small_font, wrap=tk.WORD)
        self.panel_suggestions.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.panel_suggestions.config(state=tk.DISABLED)
        
        # Tip of the day
        tip_frame = tk.Frame(detail_panel, bg=ModernTheme.bg_secondary, padx=10, pady=5)
        tip_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(tip_frame, text="💡 Tip", bg=ModernTheme.bg_secondary, fg=ModernTheme.accent_info, font=ModernTheme.small_font).pack(anchor=tk.W)
        self.tip_label = tk.Label(tip_frame, text=random.choice([
            "Use 16+ characters for excellent security", "Mix uppercase, lowercase, numbers, and symbols",
            "Never reuse passwords across accounts", "Longer passwords are stronger than complex ones"
        ]), bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted, font=ModernTheme.small_font, wraplength=300, justify=tk.LEFT)
        self.tip_label.pack(anchor=tk.W, pady=2)
    
    def refresh_accounts(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        search_term = self.search_var.get().lower()
        category_filter = self.category_var.get()
        
        filtered = []
        for nickname, data in accounts.items():
            if category_filter != "All":
                if category_filter == "Other":
                    if data['category'].lower() in ["academic", "personal", "internship"]:
                        continue
                elif data['category'] != category_filter:
                    continue
            if search_term:
                if search_term not in nickname.lower() and search_term not in data['app'].lower():
                    continue
            filtered.append((nickname, data))
        
        filtered.sort(key=lambda x: x[0])
        for nickname, data in filtered:
            AccountCard(self.cards_frame, nickname, data, on_click=self.select_account)
        
        self.stats_label.config(text=f"{len(filtered)} accounts")
        if self.current_account and self.current_account not in accounts:
            self.current_account = None
            self.clear_detail_panel()
    
    def select_account(self, nickname):
        self.current_account = nickname
        self.update_detail_panel(nickname)
        for btn in [self.show_btn, self.copy_btn, self.edit_btn, self.delete_btn]:
            btn.configure(state=tk.NORMAL)
    
    def update_detail_panel(self, nickname):
        data = accounts[nickname]
        feedback = get_password_feedback(data['password'])
        
        self.panel_title.config(text=nickname)
        self.panel_circle.update_score(feedback['score'])
        
        crack_time = estimate_crack_time(data['password'])
        self.panel_strength_label.config(text=f"{feedback['category']} — {feedback['score']:.1f}/10")
        self.panel_crack_label.config(text=f"⏱️ {crack_time}")
        
        password_display = data['password'] if self.show_passwords else "•" * len(data['password'])
        details = f"App: {data['app']}\nCategory: {data['category']}\nPassword: {password_display}\nCreated: {data.get('created', 'Unknown')}\nModified: {data.get('last_modified', 'Unknown')}"
        
        self.panel_details.config(state=tk.NORMAL)
        self.panel_details.delete(1.0, tk.END)
        self.panel_details.insert(1.0, details)
        self.panel_details.config(state=tk.DISABLED)
        
        # Strengths
        self.panel_strengths.config(state=tk.NORMAL)
        self.panel_strengths.delete(1.0, tk.END)
        if feedback['strengths']:
            for s in feedback['strengths']:
                self.panel_strengths.insert(tk.END, f"✓ {s}\n")
        else:
            self.panel_strengths.insert(tk.END, "• No notable strengths\n")
        self.panel_strengths.config(state=tk.DISABLED)
        
        # Issues
        self.panel_issues.config(state=tk.NORMAL)
        self.panel_issues.delete(1.0, tk.END)
        if feedback['issues']:
            for issue in feedback['issues']:
                self.panel_issues.insert(tk.END, f"⚠️ {issue}\n")
        else:
            self.panel_issues.insert(tk.END, "✅ No issues found!\n")
        self.panel_issues.config(state=tk.DISABLED)
        
        # Suggestions
        self.panel_suggestions.config(state=tk.NORMAL)
        self.panel_suggestions.delete(1.0, tk.END)
        suggestions = []
        if len(data['password']) < 12:
            suggestions.append("• Increase length to 12+ characters")
        if len(data['password']) < 16:
            suggestions.append("• For excellent security, use 16+ characters")
        if not re.search(r"[A-Z]", data['password']):
            suggestions.append("• Add uppercase letters (A-Z)")
        if not re.search(r"[0-9]", data['password']):
            suggestions.append("• Add numbers (0-9)")
        if not re.search(r"[!@#$%^&*()]", data['password']):
            suggestions.append("• Add symbols (!@#$%)")
        if suggestions:
            for s in suggestions:
                self.panel_suggestions.insert(tk.END, f"💡 {s}\n")
        else:
            self.panel_suggestions.insert(tk.END, "✨ Password looks great!\n")
        self.panel_suggestions.config(state=tk.DISABLED)
        
        self.show_btn.configure(text="Hide" if self.show_passwords else "Show")
    
    def clear_detail_panel(self):
        self.panel_title.config(text="Select an account")
        self.panel_circle.update_score(0)
        self.panel_strength_label.config(text="")
        self.panel_crack_label.config(text="")
        
        for widget in [self.panel_details, self.panel_strengths, self.panel_issues, self.panel_suggestions]:
            widget.config(state=tk.NORMAL)
            widget.delete(1.0, tk.END)
            widget.config(state=tk.DISABLED)
        
        for btn in [self.show_btn, self.copy_btn, self.edit_btn, self.delete_btn]:
            btn.configure(state=tk.DISABLED)
    
    def update_account_password(self, new_password):
        """Update current account's password (called from suggestion dialog)"""
        if self.current_account and new_password:
            accounts[self.current_account]['password'] = new_password
            accounts[self.current_account]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_accounts()
            self.refresh_accounts()
            self.update_detail_panel(self.current_account)
            messagebox.showinfo("Updated", "Password updated successfully!")
    
    def show_inspector(self):
        if not self.current_account:
            messagebox.showwarning("No Selection", "Please select an account first.")
            return
        data = accounts[self.current_account]
        PasswordInspector(self.root, self.current_account, data['password'])
    
    def toggle_password(self):
        if not self.current_account:
            return
        if not self.show_passwords:
            if not messagebox.askyesno("Security", "Reveal password?\n\nMake sure no one is looking."):
                return
        self.show_passwords = not self.show_passwords
        self.update_detail_panel(self.current_account)
    
    def copy_password(self):
        if not self.current_account:
            return
        if not self.show_passwords:
            messagebox.showwarning("Hidden", "Click 'Show' first to reveal the password.")
            return
        try:
            pyperclip.copy(accounts[self.current_account]['password'])
            messagebox.showinfo("Success", "Password copied!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_account_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Account")
        dialog.geometry("450x620")
        dialog.configure(bg=ModernTheme.bg_secondary)
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, bg=ModernTheme.bg_secondary, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Create New Account", bg=ModernTheme.bg_secondary, fg=ModernTheme.accent, font=ModernTheme.heading_font).pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(main_frame, text="Nickname", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted).pack(anchor=tk.W)
        nickname_var = tk.StringVar()
        nickname_entry = ttk.Entry(main_frame, textvariable=nickname_var)
        nickname_entry.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(main_frame, text="App Name", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted).pack(anchor=tk.W)
        app_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=app_var).pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(main_frame, text="Category", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted).pack(anchor=tk.W)
        category_var = tk.StringVar(value=self.config.get('default_category', 'Personal'))
        ttk.Combobox(main_frame, textvariable=category_var, values=["Academic", "Personal", "Internship", "Other"], state="readonly").pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(main_frame, text="Password", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted).pack(anchor=tk.W)
        pwd_frame = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
        pwd_frame.pack(fill=tk.X, pady=(5, 10))
        password_var = tk.StringVar()
        password_entry = ttk.Entry(pwd_frame, textvariable=password_var, show="•")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(pwd_frame, text="Generate", command=lambda: password_var.set(generate_password())).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Live strength preview
        preview_frame = tk.LabelFrame(main_frame, text="Password Strength Preview", bg=ModernTheme.bg_secondary,
                                      fg=ModernTheme.text_muted, font=ModernTheme.small_font)
        preview_frame.pack(fill=tk.X, pady=10)
        
        preview_bar = ttk.Progressbar(preview_frame, length=350, mode='determinate')
        preview_bar.pack(pady=5, padx=5)
        preview_label = tk.Label(preview_frame, text="", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_secondary)
        preview_label.pack()
        preview_crack = tk.Label(preview_frame, text="", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted, font=ModernTheme.small_font)
        preview_crack.pack()
        
        def update_preview(*args):
            pwd = password_var.get()
            if pwd:
                fb = get_password_feedback(pwd)
                preview_bar['value'] = (fb['score'] / 10) * 100
                preview_label.config(text=f"{fb['category']} ({fb['score']:.1f}/10)", fg=ModernTheme.strength_colors.get(fb['category'], ModernTheme.text_secondary))
                preview_crack.config(text=f"⏱️ {estimate_crack_time(pwd)}")
            else:
                preview_bar['value'] = 0
                preview_label.config(text="Enter a password")
                preview_crack.config(text="")
        
        password_var.trace('w', update_preview)
        
        def save():
            nickname = nickname_var.get().strip()
            app = app_var.get().strip()
            category = category_var.get()
            password = password_var.get().strip()
            if not nickname or not app or not password:
                messagebox.showerror("Error", "All fields required")
                return
            category = category.lower().capitalize() if category.lower() in ["academic", "personal", "internship"] else "Other"
            
            # Check for duplicate data
            duplicate = False
            for n, d in accounts.items():
                if d['app'] == app and d['category'] == category and d['password'] == password and n != nickname:
                    duplicate = True
                    break
            if duplicate and not messagebox.askyesno("Duplicate", "Account with same data exists. Save anyway?"):
                return
            
            if nickname in accounts and not messagebox.askyesno("Duplicate", f"'{nickname}' exists. Overwrite?"):
                return
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            accounts[nickname] = {"app": app, "category": category, "password": password, "created": current_time, "last_modified": current_time}
            save_accounts()
            self.refresh_accounts()
            dialog.destroy()
        
        btn_frame = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        RoundedButton(btn_frame, text="Save", command=save, bg=ModernTheme.accent, width=100, height=35).pack(side=tk.LEFT, padx=5)
        RoundedButton(btn_frame, text="Cancel", command=dialog.destroy, bg=ModernTheme.bg_input, width=100, height=35).pack(side=tk.LEFT, padx=5)
        nickname_entry.focus()
    
    def edit_account(self):
        if not self.current_account:
            return
        data = accounts[self.current_account]
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Account — {self.current_account}")
        dialog.geometry("450x620")
        dialog.configure(bg=ModernTheme.bg_secondary)
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, bg=ModernTheme.bg_secondary, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Edit Account", bg=ModernTheme.bg_secondary, fg=ModernTheme.accent, font=ModernTheme.heading_font).pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(main_frame, text="Nickname", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted).pack(anchor=tk.W)
        tk.Label(main_frame, text=self.current_account, bg=ModernTheme.bg_secondary, fg=ModernTheme.text_primary).pack(anchor=tk.W, pady=(5, 10))
        
        tk.Label(main_frame, text="App Name", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted).pack(anchor=tk.W)
        app_var = tk.StringVar(value=data['app'])
        ttk.Entry(main_frame, textvariable=app_var).pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(main_frame, text="Category", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted).pack(anchor=tk.W)
        category_var = tk.StringVar(value=data['category'])
        ttk.Combobox(main_frame, textvariable=category_var, values=["Academic", "Personal", "Internship", "Other"], state="readonly").pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(main_frame, text="Password", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted).pack(anchor=tk.W)
        pwd_frame = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
        pwd_frame.pack(fill=tk.X, pady=(5, 10))
        password_var = tk.StringVar(value=data['password'])
        password_entry = ttk.Entry(pwd_frame, textvariable=password_var, show="•")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(pwd_frame, text="Generate", command=lambda: password_var.set(generate_password())).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Live strength preview
        preview_frame = tk.LabelFrame(main_frame, text="Password Strength Preview", bg=ModernTheme.bg_secondary,
                                      fg=ModernTheme.text_muted, font=ModernTheme.small_font)
        preview_frame.pack(fill=tk.X, pady=10)
        
        preview_bar = ttk.Progressbar(preview_frame, length=350, mode='determinate')
        preview_bar.pack(pady=5, padx=5)
        preview_label = tk.Label(preview_frame, text="", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_secondary)
        preview_label.pack()
        preview_crack = tk.Label(preview_frame, text="", bg=ModernTheme.bg_secondary, fg=ModernTheme.text_muted, font=ModernTheme.small_font)
        preview_crack.pack()
        
        def update_preview(*args):
            pwd = password_var.get()
            if pwd:
                fb = get_password_feedback(pwd)
                preview_bar['value'] = (fb['score'] / 10) * 100
                preview_label.config(text=f"{fb['category']} ({fb['score']:.1f}/10)", fg=ModernTheme.strength_colors.get(fb['category'], ModernTheme.text_secondary))
                preview_crack.config(text=f"⏱️ {estimate_crack_time(pwd)}")
            else:
                preview_bar['value'] = 0
                preview_label.config(text="Enter a password")
                preview_crack.config(text="")
        
        password_var.trace('w', update_preview)
        update_preview()
        
        def save_changes():
            accounts[self.current_account]['app'] = app_var.get()
            accounts[self.current_account]['category'] = category_var.get()
            accounts[self.current_account]['password'] = password_var.get()
            accounts[self.current_account]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_accounts()
            self.refresh_accounts()
            self.update_detail_panel(self.current_account)
            dialog.destroy()
        
        btn_frame = tk.Frame(main_frame, bg=ModernTheme.bg_secondary)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        RoundedButton(btn_frame, text="Save", command=save_changes, bg=ModernTheme.accent, width=100, height=35).pack(side=tk.LEFT, padx=5)
        RoundedButton(btn_frame, text="Cancel", command=dialog.destroy, bg=ModernTheme.bg_input, width=100, height=35).pack(side=tk.LEFT, padx=5)
    
    def delete_account(self):
        if self.current_account and messagebox.askyesno("Delete", f"Delete '{self.current_account}'?"):
            del accounts[self.current_account]
            save_accounts()
            self.current_account = None
            self.refresh_accounts()
            self.clear_detail_panel()
    
    def show_reuse_report(self):
        reused = detect_password_reuse()
        if not reused:
            messagebox.showinfo("Password Reuse", "✅ No reused passwords found!")
        else:
            ReuseReportWindow(self.root, reused)
    
    def show_health_dashboard(self):
        if not accounts:
            messagebox.showinfo("Health Dashboard", "No accounts to analyze")
            return
        HealthDashboardWindow(self.root)
    
    def show_password_generator(self):
        pwd = generate_password(24)
        feedback = get_password_feedback(pwd)
        if messagebox.askyesno("Password Generator", f"🔐 Generated:\n{pwd}\n\nStrength: {feedback['category']} ({feedback['score']:.1f}/10)\n⏱️ {estimate_crack_time(pwd)}\n\nCopy to clipboard?"):
            try:
                pyperclip.copy(pwd)
                messagebox.showinfo("Success", "Password copied!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def show_shortcuts(self):
        ShortcutsWindow(self.root)
    
    def show_preferences(self):
        PreferencesWindow(self.root, self.config, self.save_preferences)
    
    def save_preferences(self, new_config):
        self.config = new_config
        Config.save(new_config)
        # Update tray visibility
        if TRAY_AVAILABLE:
            if new_config['show_tray_icon'] and not self.tray:
                self.setup_tray()
            elif not new_config['show_tray_icon'] and self.tray:
                self.tray.stop()
                self.tray = None

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    # Show splash screen
    splash = SplashScreen()
    splash.after(2000, splash.close)
    
    root = tk.Tk()
    app = GateKeeperGUI(root)
    root.after(2100, root.deiconify)
    
    root.mainloop()

if __name__ == "__main__":
    main()
