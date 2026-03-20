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

import pyperclip
from password_checker import check_password_strength, get_password_feedback, estimate_crack_time

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_FILE = "gatekeeper_config.json"
WINDOW_CONFIG = "window_config.json"
FILENAME = "accounts.json"

if os.path.exists(FILENAME):
    with open(FILENAME, "r") as file:
        accounts = json.load(file)
else:
    accounts = {}

def save_accounts():
    with open(FILENAME, "w") as file:
        json.dump(accounts, file, indent=4)

def generate_password(length=20):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        score, _ = check_password_strength(password)
        if score >= 8:
            return password

def detect_password_reuse():
    password_map = {}
    reused = []
    for nickname, data in accounts.items():
        pwd = data['password']
        if pwd in password_map:
            password_map[pwd].append(nickname)
        else:
            password_map[pwd] = [nickname]
    for pwd, names in password_map.items():
        if len(names) > 1:
            reused.append({'password': pwd, 'accounts': names, 'count': len(names)})
    return reused

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class Config:
    DEFAULT = {'start_minimized': False, 'show_tray_icon': True, 'remember_window_position': True, 'auto_save': True, 'default_category': 'Personal'}
    @classmethod
    def load(cls):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return {**cls.DEFAULT, **json.load(f)}
            except:
                return cls.DEFAULT.copy()
        return cls.DEFAULT.copy()
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
    def save_window_position(cls, x, y, w, h):
        with open(WINDOW_CONFIG, 'w') as f:
            json.dump({'x': x, 'y': y, 'width': w, 'height': h}, f, indent=4)

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
# DARK THEME
# ============================================================================

class Theme:
    bg_primary = "#0a0c0f"
    bg_secondary = "#14181c"
    bg_card = "#1e2329"
    bg_input = "#23282e"
    accent = "#5f9ea0"
    accent_success = "#2e8b57"
    accent_danger = "#b22222"
    accent_info = "#4682b4"
    accent_warning = "#cd853f"
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
    mono_font = ("Consolas", 10) if os.name == 'nt' else ("Menlo", 10)

# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command=None, bg=Theme.accent, fg=Theme.text_primary,
                 width=120, height=35, radius=10, font=Theme.body_font, state=tk.NORMAL):
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=Theme.bg_secondary)
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
        self.draw_button(bg if state == tk.NORMAL else Theme.text_muted)
    def draw_button(self, color):
        self.delete("all")
        points = [self.radius, 0, self.width-self.radius, 0, self.width, 0, self.width, self.radius,
                  self.width, self.height-self.radius, self.width, self.height,
                  self.width-self.radius, self.height, self.radius, self.height,
                  0, self.height, 0, self.height-self.radius, 0, self.radius, 0, 0]
        self.create_polygon(points, smooth=True, fill=color, outline="")
        tc = self.fg if self.state == tk.NORMAL else Theme.text_muted
        self.create_text(self.width//2, self.height//2, text=self.text, fill=tc, font=self.font)
    def on_enter(self, e):
        if self.state == tk.NORMAL:
            self.draw_button(self.lighten(self.bg))
    def on_leave(self, e):
        if self.state == tk.NORMAL:
            self.draw_button(self.bg)
        else:
            self.draw_button(Theme.text_muted)
    def on_click(self, e):
        if self.state == tk.NORMAL and self.command:
            self.command()
    def lighten(self, c):
        if c.startswith("#"):
            r = int(c[1:3],16); g = int(c[3:5],16); b = int(c[5:7],16)
            r = min(255, r+30); g = min(255, g+30); b = min(255, b+30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return c
    def configure(self, **kwargs):
        if 'state' in kwargs:
            self.state = kwargs['state']
            self.draw_button(self.bg if self.state == tk.NORMAL else Theme.text_muted)

class StrengthCircle(tk.Canvas):
    def __init__(self, master, score=0, size=50):
        super().__init__(master, width=size, height=size, bg=Theme.bg_card, highlightthickness=0)
        self.size = size
        self.score = score
        self.draw()
    def draw(self):
        self.delete("all")
        c = self.size // 2
        r = self.size // 2 - 5
        self.create_oval(c-r, c-r, c+r, c+r, outline=Theme.border, width=2, fill="")
        angle = (self.score / 10) * 360
        self.create_arc(c-r, c-r, c+r, c+r, start=90, extent=-angle, outline=self.get_color(), width=3, style="arc")
        self.create_text(c, c, text=f"{self.score:.1f}", fill=Theme.text_primary, font=("Segoe UI", int(self.size*0.2), "bold"))
    def get_color(self):
        if self.score >= 9: return Theme.strength_colors["Excellent"]
        if self.score >= 7.5: return Theme.strength_colors["Very Strong"]
        if self.score >= 6: return Theme.strength_colors["Strong"]
        if self.score >= 4.5: return Theme.strength_colors["Good"]
        if self.score >= 3: return Theme.strength_colors["Fair"]
        if self.score >= 1.5: return Theme.strength_colors["Weak"]
        return Theme.strength_colors["Very Weak"]
    def update_score(self, score):
        self.score = score
        self.draw()

class AccountCard(tk.Frame):
    def __init__(self, master, nickname, data, on_click):
        super().__init__(master, bg=Theme.bg_card, relief="flat", bd=1, highlightbackground=Theme.border, highlightthickness=1)
        self.nickname = nickname
        self.data = data
        self.on_click = on_click
        self.pack(fill=tk.X, pady=5, padx=10)
        self.bind("<Button-1>", self.click)
        self.setup()
    def setup(self):
        fb = get_password_feedback(self.data['password'])
        StrengthCircle(self, score=fb['score'], size=50).pack(side=tk.LEFT, padx=10, pady=10)
        info = tk.Frame(self, bg=Theme.bg_card)
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(info, text=self.nickname, bg=Theme.bg_card, fg=Theme.text_primary, font=Theme.subheading_font, anchor=tk.W).pack(anchor=tk.W)
        tk.Label(info, text=self.data['category'], bg=Theme.bg_card, fg=Theme.text_muted, font=Theme.small_font, anchor=tk.W).pack(anchor=tk.W)
        tk.Label(info, text=f"📱 {self.data['app']}", bg=Theme.bg_card, fg=Theme.text_secondary, font=Theme.small_font, anchor=tk.W).pack(anchor=tk.W)
        right = tk.Frame(self, bg=Theme.bg_card)
        right.pack(side=tk.RIGHT, padx=10, pady=10)
        created = self.data.get('created', 'Unknown').split()[0]
        tk.Label(right, text=f"📅 {created}", bg=Theme.bg_card, fg=Theme.text_muted, font=Theme.small_font).pack(anchor=tk.E)
        tk.Label(right, text=f"{fb['category']} — {fb['score']:.1f}/10", bg=Theme.bg_card, fg=Theme.strength_colors.get(fb['category']), font=Theme.small_font).pack(anchor=tk.E)
    def click(self, e):
        if self.on_click:
            self.on_click(self.nickname)

# ============================================================================
# DIALOG WINDOWS
# ============================================================================

class SplashScreen(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry("450x300")
        self.configure(bg=Theme.bg_secondary)
        self.overrideredirect(True)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")
        main = tk.Frame(self, bg=Theme.bg_secondary)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="🔐", bg=Theme.bg_secondary, fg=Theme.accent, font=("Segoe UI", 64)).pack(pady=(40,10))
        tk.Label(main, text="GateKeeper", bg=Theme.bg_secondary, fg=Theme.text_primary, font=("Segoe UI", 24, "bold")).pack()
        tk.Label(main, text="secure password manager", bg=Theme.bg_secondary, fg=Theme.text_muted, font=("Segoe UI", 11)).pack(pady=(5,20))
        self.progress = ttk.Progressbar(main, length=300, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.start(10)
        self.update()
    def close(self):
        self.progress.stop()
        self.destroy()

class PreferencesWindow(tk.Toplevel):
    def __init__(self, parent, config, on_save):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.on_save = on_save
        self.title("Preferences")
        self.geometry("400x400")
        self.configure(bg=Theme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        self.center()
        self.setup()
    def center(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width()//2) - 200
        y = self.parent.winfo_y() + (self.parent.winfo_height()//2) - 200
        self.geometry(f"+{x}+{y}")
    def setup(self):
        main = tk.Frame(self, bg=Theme.bg_secondary, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="Preferences", bg=Theme.bg_secondary, fg=Theme.accent, font=Theme.heading_font).pack(anchor=tk.W, pady=(0,20))
        self.min_var = tk.BooleanVar(value=self.config.get('start_minimized', False))
        tk.Checkbutton(main, text="Start minimized to system tray", variable=self.min_var, bg=Theme.bg_secondary, fg=Theme.text_primary, selectcolor=Theme.bg_secondary).pack(anchor=tk.W, pady=5)
        self.tray_var = tk.BooleanVar(value=self.config.get('show_tray_icon', True))
        tk.Checkbutton(main, text="Show system tray icon", variable=self.tray_var, bg=Theme.bg_secondary, fg=Theme.text_primary, selectcolor=Theme.bg_secondary).pack(anchor=tk.W, pady=5)
        self.pos_var = tk.BooleanVar(value=self.config.get('remember_window_position', True))
        tk.Checkbutton(main, text="Remember window position", variable=self.pos_var, bg=Theme.bg_secondary, fg=Theme.text_primary, selectcolor=Theme.bg_secondary).pack(anchor=tk.W, pady=5)
        self.cat_var = tk.StringVar(value=self.config.get('default_category', 'Personal'))
        tk.Label(main, text="Default Category", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W, pady=(15,5))
        ttk.Combobox(main, textvariable=self.cat_var, values=["Academic", "Personal", "Internship", "Other"], state="readonly").pack(fill=tk.X)
        btn = tk.Frame(main, bg=Theme.bg_secondary)
        btn.pack(fill=tk.X, pady=(20,0))
        def save():
            new = {'start_minimized': self.min_var.get(), 'show_tray_icon': self.tray_var.get(),
                   'remember_window_position': self.pos_var.get(), 'default_category': self.cat_var.get()}
            self.on_save(new)
            self.destroy()
        RoundedButton(btn, "Save", save, Theme.accent, width=100, height=35).pack(side=tk.LEFT, padx=5)
        RoundedButton(btn, "Cancel", self.destroy, Theme.bg_input, width=100, height=35).pack(side=tk.LEFT, padx=5)

class ShortcutsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Keyboard Shortcuts")
        self.geometry("450x400")
        self.configure(bg=Theme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        self.center()
        self.setup()
    def center(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width()//2) - 225
        y = self.parent.winfo_y() + (self.parent.winfo_height()//2) - 200
        self.geometry(f"+{x}+{y}")
    def setup(self):
        main = tk.Frame(self, bg=Theme.bg_secondary, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="Keyboard Shortcuts", bg=Theme.bg_secondary, fg=Theme.accent, font=Theme.heading_font).pack(pady=(0,15))
        shortcuts = [("⌘N / Ctrl+N", "New Account"), ("⌘, / Ctrl+,", "Preferences"), ("⌘H / Ctrl+H", "Hide to Tray"),
                     ("⌘Q / Ctrl+Q", "Quit"), ("⌘? / Ctrl+?", "Shortcuts"), ("Esc", "Close Dialog"), ("Enter", "Save")]
        for key, action in shortcuts:
            f = tk.Frame(main, bg=Theme.bg_secondary)
            f.pack(fill=tk.X, pady=3)
            tk.Label(f, text=key, bg=Theme.bg_input, fg=Theme.accent_info, font=("Segoe UI",9,"bold"), padx=8, pady=4).pack(side=tk.LEFT)
            tk.Label(f, text=action, bg=Theme.bg_secondary, fg=Theme.text_secondary).pack(side=tk.LEFT, padx=(15,0))
        RoundedButton(main, "Close", self.destroy, Theme.bg_input, width=100, height=35).pack(pady=15)

class PasswordInspector(tk.Toplevel):
    def __init__(self, parent, nickname, password):
        super().__init__(parent)
        self.parent = parent
        self.password = password
        self.fb = get_password_feedback(password)
        self.title(f"Inspector — {nickname}")
        self.geometry("600x550")
        self.configure(bg=Theme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        self.center()
        self.setup()
    def center(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width()//2) - 300
        y = self.parent.winfo_y() + (self.parent.winfo_height()//2) - 275
        self.geometry(f"+{x}+{y}")
    def setup(self):
        main = tk.Frame(self, bg=Theme.bg_secondary, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        header = tk.Frame(main, bg=Theme.bg_secondary)
        header.pack(fill=tk.X, pady=(0,15))
        color = Theme.strength_colors.get(self.fb['category'], Theme.accent)
        tk.Label(header, text=f"{self.fb['score']:.1f}", font=("Segoe UI", 32, "bold"), fg=color, bg=Theme.bg_secondary).pack(side=tk.LEFT, padx=(0,20))
        info = tk.Frame(header, bg=Theme.bg_secondary)
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(info, text=self.fb['category'], font=("Segoe UI", 14, "bold"), fg=color, bg=Theme.bg_secondary).pack(anchor=tk.W)
        tk.Label(info, text=f"Length: {len(self.password)} chars", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        tk.Label(info, text=f"Crack: {estimate_crack_time(self.password)}", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        notebook = ttk.Notebook(main)
        notebook.pack(fill=tk.BOTH, expand=True)
        # Analysis tab
        a = tk.Frame(notebook, bg=Theme.bg_secondary)
        notebook.add(a, text="Analysis")
        has_lower = bool(re.search(r"[a-z]", self.password))
        has_upper = bool(re.search(r"[A-Z]", self.password))
        has_digit = bool(re.search(r"[0-9]", self.password))
        has_symbol = bool(re.search(r"[!@#$%^&*()]", self.password))
        for label, present in [("Lowercase", has_lower), ("Uppercase", has_upper), ("Numbers", has_digit), ("Symbols", has_symbol)]:
            f = tk.Frame(a, bg=Theme.bg_secondary)
            f.pack(fill=tk.X, pady=3, padx=10)
            tk.Label(f, text=label, width=15, bg=Theme.bg_secondary, fg=Theme.text_secondary).pack(side=tk.LEFT)
            tk.Label(f, text="✓ Yes" if present else "✗ No", bg=Theme.bg_secondary, fg=Theme.accent_success if present else Theme.accent_danger).pack(side=tk.LEFT)
        # Strengths
        s = tk.Frame(notebook, bg=Theme.bg_secondary)
        notebook.add(s, text="Strengths")
        st = tk.Text(s, bg=Theme.bg_input, fg=Theme.accent_success, bd=0, padx=10, pady=10, font=Theme.small_font, wrap=tk.WORD)
        st.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        if self.fb['strengths']:
            for x in self.fb['strengths']: st.insert(tk.END, f"✓ {x}\n")
        else: st.insert(tk.END, "No notable strengths")
        st.config(state=tk.DISABLED)
        # Issues
        i = tk.Frame(notebook, bg=Theme.bg_secondary)
        notebook.add(i, text="Issues & Fixes")
        it = tk.Text(i, bg=Theme.bg_input, fg=Theme.accent_danger, bd=0, padx=10, pady=10, font=Theme.small_font, wrap=tk.WORD)
        it.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        if self.fb['issues']:
            for issue in self.fb['issues']:
                it.insert(tk.END, f"⚠️ {issue}\n")
                if "uppercase" in issue.lower(): it.insert(tk.END, "   💡 Add capital letters (A-Z)\n")
                elif "lowercase" in issue.lower(): it.insert(tk.END, "   💡 Add lowercase letters (a-z)\n")
                elif "number" in issue.lower(): it.insert(tk.END, "   💡 Add numbers (0-9)\n")
                elif "symbol" in issue.lower(): it.insert(tk.END, "   💡 Add symbols (!@#$%)\n")
                elif "short" in issue.lower(): it.insert(tk.END, "   💡 Make password longer (12+ chars)\n")
        else: it.insert(tk.END, "✅ No issues found!")
        it.config(state=tk.DISABLED)
        # Suggestions
        g = tk.Frame(notebook, bg=Theme.bg_secondary)
        notebook.add(g, text="Suggestions")
        gt = tk.Text(g, bg=Theme.bg_input, fg=Theme.accent_info, bd=0, padx=10, pady=10, font=Theme.small_font, wrap=tk.WORD)
        gt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        sugg = []
        if len(self.password) < 12: sugg.append("• Increase length to 12+ characters")
        if len(self.password) < 16: sugg.append("• For excellent security, use 16+ characters")
        if not has_upper or not has_lower: sugg.append("• Mix uppercase and lowercase letters")
        if not has_digit: sugg.append("• Add numbers (0-9)")
        if not has_symbol: sugg.append("• Add symbols (!@#$%)")
        if sugg:
            for s in sugg: gt.insert(tk.END, f"💡 {s}\n")
        else: gt.insert(tk.END, "✨ Looks great!")
        gt.config(state=tk.DISABLED)
        # Actions
        act = tk.Frame(notebook, bg=Theme.bg_secondary)
        notebook.add(act, text="Quick Actions")
        af = tk.Frame(act, bg=Theme.bg_secondary)
        af.pack(expand=True, pady=30)
        def gen_new(): self.parent.suggest_better_password(generate_password(20), self)
        RoundedButton(af, "🔄 Generate New", gen_new, Theme.accent_info, width=200, height=35).pack(pady=5)
        RoundedButton(af, "📋 Copy", lambda: (pyperclip.copy(self.password), messagebox.showinfo("Copied", "Password copied!")), Theme.accent_success, width=200, height=35).pack(pady=5)
        RoundedButton(af, "✏️ Edit", lambda: [self.destroy(), self.parent.edit_account()], Theme.accent_warning, width=200, height=35).pack(pady=5)
        RoundedButton(main, "Close", self.destroy, Theme.bg_input, width=120, height=35).pack(pady=15)

class SuggestPasswordDialog(tk.Toplevel):
    def __init__(self, parent, password, on_select):
        super().__init__(parent)
        self.parent = parent
        self.password = password
        self.on_select = on_select
        self.title("Password Suggestions")
        self.geometry("500x400")
        self.configure(bg=Theme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        self.center()
        self.setup()
    def center(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width()//2) - 250
        y = self.parent.winfo_y() + (self.parent.winfo_height()//2) - 200
        self.geometry(f"+{x}+{y}")
    def setup(self):
        main = tk.Frame(self, bg=Theme.bg_secondary, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="Suggested Strong Passwords", bg=Theme.bg_secondary, fg=Theme.accent, font=Theme.heading_font).pack(pady=(0,15))
        suggestions = [generate_password(16) for _ in range(3)]
        for i, pwd in enumerate(suggestions):
            fb = get_password_feedback(pwd)
            f = tk.Frame(main, bg=Theme.bg_card, relief="flat", bd=1, highlightbackground=Theme.border, highlightthickness=1)
            f.pack(fill=tk.X, pady=5)
            tk.Label(f, text=f"Option {i+1}", bg=Theme.bg_card, fg=Theme.text_secondary, font=Theme.small_font).pack(anchor=tk.W, padx=10, pady=(5,0))
            tk.Label(f, text=pwd, bg=Theme.bg_card, fg=Theme.text_primary, font=Theme.mono_font).pack(side=tk.LEFT, padx=10, pady=5)
            tk.Label(f, text=f"{fb['category']} ({fb['score']:.1f}/10)", bg=Theme.bg_card, fg=Theme.strength_colors.get(fb['category'])).pack(side=tk.LEFT, padx=10)
            RoundedButton(f, "Use", lambda p=pwd: self.on_select(p), Theme.accent, width=80, height=30, radius=6).pack(side=tk.RIGHT, padx=5, pady=5)
        RoundedButton(main, "Cancel", self.destroy, Theme.bg_input, width=100, height=35).pack(pady=15)

class ReuseReportWindow(tk.Toplevel):
    def __init__(self, parent, reused):
        super().__init__(parent)
        self.parent = parent
        self.reused = reused
        self.title("Password Reuse Report")
        self.geometry("600x500")
        self.configure(bg=Theme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        self.center()
        self.setup()
    def center(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width()//2) - 300
        y = self.parent.winfo_y() + (self.parent.winfo_height()//2) - 250
        self.geometry(f"+{x}+{y}")
    def setup(self):
        main = tk.Frame(self, bg=Theme.bg_secondary, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="Password Reuse Report", bg=Theme.bg_secondary, fg=Theme.accent, font=Theme.heading_font).pack(pady=(0,15))
        tk.Label(main, text=f"Found {len(self.reused)} reused password(s):", bg=Theme.bg_secondary, fg=Theme.text_secondary).pack(anchor=tk.W)
        frame = tk.Frame(main, bg=Theme.bg_secondary)
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        scroll = ttk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text = tk.Text(frame, yscrollcommand=scroll.set, wrap=tk.WORD, bg=Theme.bg_input, fg=Theme.text_primary, bd=0, padx=10, pady=10)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=text.yview)
        for item in self.reused:
            text.insert(tk.END, f"\nPassword: {item['password']}\n", "pwd")
            text.tag_config("pwd", foreground=Theme.accent_danger, font=Theme.mono_font)
            text.insert(tk.END, f"Used in {item['count']} accounts:\n")
            for acc in item['accounts']:
                text.insert(tk.END, f"  • {acc} ({accounts[acc]['app']})\n")
            text.insert(tk.END, "\n" + "─"*50 + "\n")
        text.config(state=tk.DISABLED)
        RoundedButton(main, "Close", self.destroy, Theme.bg_input, width=120, height=35).pack(pady=15)

class HealthDashboardWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Health Dashboard")
        self.geometry("550x500")
        self.configure(bg=Theme.bg_secondary)
        self.transient(parent)
        self.grab_set()
        self.center()
        self.setup()
    def center(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width()//2) - 275
        y = self.parent.winfo_y() + (self.parent.winfo_height()//2) - 250
        self.geometry(f"+{x}+{y}")
    def setup(self):
        main = tk.Frame(self, bg=Theme.bg_secondary, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="Password Health Dashboard", bg=Theme.bg_secondary, fg=Theme.accent, font=Theme.heading_font).pack(pady=(0,20))
        total = len(accounts)
        scores = [get_password_feedback(d['password'])['score'] for d in accounts.values()]
        avg = sum(scores) / total if total else 0
        cats = [get_password_feedback(d['password'])['category'] for d in accounts.values()]
        cat_counts = {c: cats.count(c) for c in ["Excellent","Very Strong","Strong","Good","Fair","Weak","Very Weak"]}
        stats = tk.Frame(main, bg=Theme.bg_secondary)
        stats.pack(fill=tk.X, pady=(0,20))
        c1 = tk.Frame(stats, bg=Theme.bg_card, relief="flat", bd=1, highlightbackground=Theme.border)
        c1.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Label(c1, text="Total Accounts", bg=Theme.bg_card, fg=Theme.text_muted).pack(pady=5)
        tk.Label(c1, text=str(total), bg=Theme.bg_card, fg=Theme.text_primary, font=("Segoe UI",24,"bold")).pack(pady=5)
        c2 = tk.Frame(stats, bg=Theme.bg_card, relief="flat", bd=1, highlightbackground=Theme.border)
        c2.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
        tk.Label(c2, text="Avg Strength", bg=Theme.bg_card, fg=Theme.text_muted).pack(pady=5)
        color = Theme.strength_colors.get("Excellent" if avg>=9 else "Very Strong" if avg>=7.5 else "Strong" if avg>=6 else "Good" if avg>=4.5 else "Fair" if avg>=3 else "Weak" if avg>=1.5 else "Very Weak")
        tk.Label(c2, text=f"{avg:.1f}/10", bg=Theme.bg_card, fg=color, font=("Segoe UI",24,"bold")).pack(pady=5)
        br = tk.LabelFrame(main, text="Strength Breakdown", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font)
        br.pack(fill=tk.BOTH, expand=True)
        for cat, count in cat_counts.items():
            if count > 0:
                f = tk.Frame(br, bg=Theme.bg_secondary)
                f.pack(fill=tk.X, pady=3, padx=10)
                tk.Canvas(f, width=20, height=20, bg=Theme.strength_colors.get(cat), highlightthickness=0).pack(side=tk.LEFT, padx=5)
                tk.Label(f, text=f"{cat}: {count} account(s)", bg=Theme.bg_secondary, fg=Theme.text_secondary).pack(side=tk.LEFT)
        rec = tk.LabelFrame(main, text="Recommendation", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font)
        rec.pack(fill=tk.X, pady=10)
        if avg >= 8: msg = "🎉 Excellent overall security!"
        elif avg >= 6: msg = "👍 Good security, keep improving!"
        elif avg >= 4: msg = "⚠️ Fair security, update weak passwords"
        else: msg = "🔴 Poor security! Update weak passwords immediately"
        tk.Label(rec, text=msg, bg=Theme.bg_secondary, fg=Theme.text_primary, wraplength=450, justify=tk.LEFT).pack(pady=10, padx=10)
        RoundedButton(main, "Close", self.destroy, Theme.bg_input, width=120, height=35).pack(pady=15)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class GateKeeper:
    def __init__(self, root):
        self.root = root
        self.root.title("GateKeeper")
        self.root.geometry("1300x750")
        self.root.configure(bg=Theme.bg_primary)
        self.root.minsize(1100, 600)
        self.root.overrideredirect(True)
        self.config = Config.load()
        self.load_window_position()
        self.current_account = None
        self.show_password = False
        self.tray = None
        if TRAY_AVAILABLE and self.config.get('show_tray_icon', True):
            self.setup_tray()
        self.setup_titlebar()
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
            Config.save_window_position(self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width(), self.root.winfo_height())
    def setup_tray(self):
        img = Image.new('RGB', (64,64), color=Theme.bg_secondary)
        draw = ImageDraw.Draw(img)
        draw.rectangle([20,25,44,45], fill=Theme.accent)
        draw.rectangle([24,15,40,25], fill=Theme.accent)
        menu = pystray.Menu(pystray.MenuItem("Show", self.show_window), pystray.MenuItem("New Account", self.add_account_dialog), pystray.MenuItem("Exit", self.quit_app))
        self.tray = pystray.Icon("gatekeeper", img, "GateKeeper", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
    def minimize_to_tray(self):
        if self.tray and self.config.get('show_tray_icon', True):
            self.root.withdraw()
        else:
            self.root.iconify()
    def quit_app(self):
        self.save_window_position()
        if self.tray: self.tray.stop()
        self.root.quit()
    def setup_titlebar(self):
        bar = tk.Frame(self.root, bg=Theme.bg_secondary, height=40)
        bar.pack(fill=tk.X, side=tk.TOP)
        bar.pack_propagate(False)
        tk.Label(bar, text="🔐", bg=Theme.bg_secondary, fg=Theme.accent, font=("Segoe UI",12)).pack(side=tk.LEFT, padx=(10,5))
        tk.Label(bar, text="GateKeeper", bg=Theme.bg_secondary, fg=Theme.text_primary, font=("Segoe UI",11,"bold")).pack(side=tk.LEFT)
        controls = tk.Frame(bar, bg=Theme.bg_secondary)
        controls.pack(side=tk.RIGHT, padx=10)
        tk.Button(controls, text="─", bg=Theme.bg_secondary, fg=Theme.text_primary, bd=0, font=("Segoe UI",12), command=self.minimize_to_tray).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="✕", bg=Theme.bg_secondary, fg=Theme.accent_danger, bd=0, font=("Segoe UI",12), command=self.quit_app).pack(side=tk.LEFT, padx=5)
        for w in [bar]:
            w.bind("<Button-1>", self.start_move)
            w.bind("<B1-Motion>", self.on_move)
    def start_move(self, e): self.x = e.x
    def on_move(self, e):
        x = self.root.winfo_x() + e.x - self.x
        y = self.root.winfo_y() + e.y - self.y
        self.root.geometry(f"+{x}+{y}")
    def setup_shortcuts(self):
        self.root.bind('<Command-n>', lambda e: self.add_account_dialog())
        self.root.bind('<Control-n>', lambda e: self.add_account_dialog())
        self.root.bind('<Command-comma>', lambda e: PreferencesWindow(self.root, self.config, self.save_preferences))
        self.root.bind('<Control-comma>', lambda e: PreferencesWindow(self.root, self.config, self.save_preferences))
        self.root.bind('<Command-h>', lambda e: self.minimize_to_tray())
        self.root.bind('<Control-h>', lambda e: self.minimize_to_tray())
        self.root.bind('<Command-slash>', lambda e: ShortcutsWindow(self.root))
        self.root.bind('<Control-slash>', lambda e: ShortcutsWindow(self.root))
        self.root.bind('<Command-q>', lambda e: self.quit_app())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
    def save_preferences(self, new):
        self.config = new
        Config.save(new)
        if TRAY_AVAILABLE:
            if new['show_tray_icon'] and not self.tray: self.setup_tray()
            elif not new['show_tray_icon'] and self.tray: self.tray.stop(); self.tray = None
    def setup_ui(self):
        main = tk.Frame(self.root, bg=Theme.bg_primary)
        main.pack(fill=tk.BOTH, expand=True)
        # Left sidebar
        sidebar = tk.Frame(main, bg=Theme.bg_secondary, width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        logo = tk.Frame(sidebar, bg=Theme.bg_secondary, height=80)
        logo.pack(fill=tk.X, pady=(20,10))
        logo.pack_propagate(False)
        tk.Label(logo, text="🔐 GateKeeper", bg=Theme.bg_secondary, fg=Theme.accent, font=Theme.heading_font).pack()
        tk.Label(logo, text="secure password manager", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font).pack()
        search = tk.Frame(sidebar, bg=Theme.bg_secondary, padx=15, pady=10)
        search.pack(fill=tk.X)
        tk.Label(search, text="🔍 Search accounts", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font).pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *a: self.refresh_accounts())
        ttk.Entry(search, textvariable=self.search_var).pack(fill=tk.X, pady=(5,0))
        cat = tk.Frame(sidebar, bg=Theme.bg_secondary, padx=15, pady=10)
        cat.pack(fill=tk.X)
        tk.Label(cat, text="📂 Categories", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font).pack(anchor=tk.W)
        self.category_var = tk.StringVar(value="All")
        for c in ["All","Academic","Personal","Internship","Other"]:
            tk.Radiobutton(cat, text=c, variable=self.category_var, value=c, bg=Theme.bg_secondary, fg=Theme.text_secondary, selectcolor=Theme.bg_secondary, command=self.refresh_accounts).pack(anchor=tk.W, pady=2)
        tools = tk.Frame(sidebar, bg=Theme.bg_secondary, padx=15, pady=10)
        tools.pack(fill=tk.X)
        tk.Label(tools, text="🛠️ Tools", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font).pack(anchor=tk.W)
        RoundedButton(tools, "Password Inspector", lambda: self.show_inspector() if self.current_account else messagebox.showwarning("No Selection", "Select an account first"), Theme.bg_input, width=230, height=32, radius=6).pack(pady=2)
        RoundedButton(tools, "Password Generator", self.show_password_generator, Theme.bg_input, width=230, height=32, radius=6).pack(pady=2)
        RoundedButton(tools, "Reuse Check", self.show_reuse_report, Theme.bg_input, width=230, height=32, radius=6).pack(pady=2)
        RoundedButton(tools, "Health Dashboard", self.show_health, Theme.bg_input, width=230, height=32, radius=6).pack(pady=2)
        RoundedButton(tools, "Shortcuts", lambda: ShortcutsWindow(self.root), Theme.bg_input, width=230, height=32, radius=6).pack(pady=2)
        add = tk.Frame(sidebar, bg=Theme.bg_secondary, padx=15, pady=20)
        add.pack(fill=tk.X, side=tk.BOTTOM)
        RoundedButton(add, "+ New Account", self.add_account_dialog, Theme.accent, width=230, height=40, radius=8).pack()
        # Main content - Cards
        content = tk.Frame(main, bg=Theme.bg_primary)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        header = tk.Frame(content, bg=Theme.bg_primary, height=60)
        header.pack(fill=tk.X, padx=20, pady=(20,10))
        header.pack_propagate(False)
        tk.Label(header, text="Your Vault", bg=Theme.bg_primary, fg=Theme.text_primary, font=Theme.heading_font).pack(side=tk.LEFT)
        self.stats = tk.Label(header, text="0 accounts", bg=Theme.bg_primary, fg=Theme.text_muted, font=Theme.body_font)
        self.stats.pack(side=tk.RIGHT)
        cards_container = tk.Frame(content, bg=Theme.bg_primary)
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        canvas = tk.Canvas(cards_container, bg=Theme.bg_primary, highlightthickness=0)
        scroll = ttk.Scrollbar(cards_container, orient="vertical", command=canvas.yview)
        self.cards_frame = tk.Frame(canvas, bg=Theme.bg_primary)
        self.cards_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        # Right panel (NO TABS - all info visible like your screenshot)
        panel = tk.Frame(main, bg=Theme.bg_secondary, width=320)
        panel.pack(side=tk.RIGHT, fill=tk.Y)
        panel.pack_propagate(False)
        # Account name
        self.panel_title = tk.Label(panel, text="Select an account", bg=Theme.bg_secondary, fg=Theme.text_primary, font=Theme.subheading_font)
        self.panel_title.pack(pady=(20,10))
        # Strength circle
        self.panel_circle = StrengthCircle(panel, score=0, size=80)
        self.panel_circle.pack(pady=10)
        # Strength text
        self.panel_strength = tk.Label(panel, text="", bg=Theme.bg_secondary, fg=Theme.text_secondary, font=Theme.body_font)
        self.panel_strength.pack()
        self.panel_crack = tk.Label(panel, text="", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font)
        self.panel_crack.pack(pady=(0,10))
        # Password row (like screenshot)
        pwd_row = tk.Frame(panel, bg=Theme.bg_secondary)
        pwd_row.pack(pady=5, padx=15, fill=tk.X)
        tk.Label(pwd_row, text="🔑 PASSWORD", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font, width=10, anchor=tk.W).pack(side=tk.LEFT)
        self.panel_password = tk.Label(pwd_row, text="", bg=Theme.bg_input, fg=Theme.text_primary, font=Theme.mono_font, padx=10, pady=5, relief="flat", bd=1)
        self.panel_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # Action buttons
        btn_frame = tk.Frame(panel, bg=Theme.bg_secondary)
        btn_frame.pack(pady=10)
        self.show_btn = tk.Button(btn_frame, text="Show", bg=Theme.bg_input, fg=Theme.text_primary, bd=0, padx=20, pady=5, command=self.toggle_password, state=tk.DISABLED)
        self.show_btn.pack(side=tk.LEFT, padx=5)
        self.copy_btn = tk.Button(btn_frame, text="Copy", bg=Theme.bg_input, fg=Theme.text_primary, bd=0, padx=20, pady=5, command=self.copy_password, state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        self.edit_btn = tk.Button(btn_frame, text="Edit", bg=Theme.bg_input, fg=Theme.text_primary, bd=0, padx=20, pady=5, command=self.edit_account, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = tk.Button(btn_frame, text="Delete", bg=Theme.accent_danger, fg=Theme.text_primary, bd=0, padx=20, pady=5, command=self.delete_account, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        # Strengths section
        strengths_frame = tk.LabelFrame(panel, text="✅ Strengths", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font)
        strengths_frame.pack(fill=tk.X, padx=15, pady=5)
        self.panel_strengths = tk.Text(strengths_frame, height=2, bg=Theme.bg_input, fg=Theme.accent_success, bd=0, padx=8, pady=5, wrap=tk.WORD, font=Theme.small_font)
        self.panel_strengths.pack(fill=tk.X, padx=5, pady=5)
        self.panel_strengths.config(state=tk.DISABLED)
        # Issues section
        issues_frame = tk.LabelFrame(panel, text="⚠️ Issues to fix", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font)
        issues_frame.pack(fill=tk.X, padx=15, pady=5)
        self.panel_issues = tk.Text(issues_frame, height=2, bg=Theme.bg_input, fg=Theme.accent_danger, bd=0, padx=8, pady=5, wrap=tk.WORD, font=Theme.small_font)
        self.panel_issues.pack(fill=tk.X, padx=5, pady=5)
        self.panel_issues.config(state=tk.DISABLED)
        # Tip
        tip = tk.Label(panel, text="💡 Tip: Longer passwords are stronger than complex ones", bg=Theme.bg_secondary, fg=Theme.text_muted, font=Theme.small_font, wraplength=280)
        tip.pack(side=tk.BOTTOM, pady=15)
    def refresh_accounts(self):
        for w in self.cards_frame.winfo_children(): w.destroy()
        search = self.search_var.get().lower()
        cat = self.category_var.get()
        filtered = []
        for name, data in accounts.items():
            if cat != "All":
                if cat == "Other" and data['category'].lower() in ["academic","personal","internship"]: continue
                elif data['category'] != cat: continue
            if search and search not in name.lower() and search not in data['app'].lower(): continue
            filtered.append((name, data))
        filtered.sort(key=lambda x: x[0])
        for name, data in filtered:
            AccountCard(self.cards_frame, name, data, self.select_account)
        self.stats.config(text=f"{len(filtered)} accounts")
        if self.current_account and self.current_account not in accounts:
            self.current_account = None
            self.clear_panel()
    def select_account(self, name):
        self.current_account = name
        self.update_panel(name)
        for btn in [self.show_btn, self.copy_btn, self.edit_btn, self.delete_btn]:
            btn.config(state=tk.NORMAL)
    def update_panel(self, name):
        data = accounts[name]
        fb = get_password_feedback(data['password'])
        self.panel_title.config(text=name)
        self.panel_circle.update_score(fb['score'])
        self.panel_strength.config(text=f"{fb['category']} — {fb['score']:.1f}/10")
        self.panel_crack.config(text=f"⏱️ {estimate_crack_time(data['password'])}")
        pwd_display = data['password'] if self.show_password else "•" * len(data['password'])
        self.panel_password.config(text=pwd_display)
        self.panel_strengths.config(state=tk.NORMAL)
        self.panel_strengths.delete(1.0, tk.END)
        if fb['strengths']:
            for s in fb['strengths']: self.panel_strengths.insert(tk.END, f"• {s}\n")
        else: self.panel_strengths.insert(tk.END, "No notable strengths")
        self.panel_strengths.config(state=tk.DISABLED)
        self.panel_issues.config(state=tk.NORMAL)
        self.panel_issues.delete(1.0, tk.END)
        if fb['issues']:
            for issue in fb['issues']: self.panel_issues.insert(tk.END, f"• {issue}\n")
        else: self.panel_issues.insert(tk.END, "No issues found — excellent!")
        self.panel_issues.config(state=tk.DISABLED)
        self.show_btn.config(text="Hide" if self.show_password else "Show")
    def clear_panel(self):
        self.panel_title.config(text="Select an account")
        self.panel_circle.update_score(0)
        self.panel_strength.config(text="")
        self.panel_crack.config(text="")
        self.panel_password.config(text="")
        for w in [self.panel_strengths, self.panel_issues]:
            w.config(state=tk.NORMAL); w.delete(1.0, tk.END); w.config(state=tk.DISABLED)
        for btn in [self.show_btn, self.copy_btn, self.edit_btn, self.delete_btn]:
            btn.config(state=tk.DISABLED)
    def show_inspector(self):
        if self.current_account:
            PasswordInspector(self.root, self.current_account, accounts[self.current_account]['password'])
    def toggle_password(self):
        if not self.current_account: return
        if not self.show_password and not messagebox.askyesno("Security", "Reveal password?"): return
        self.show_password = not self.show_password
        self.update_panel(self.current_account)
    def copy_password(self):
        if not self.current_account: return
        if not self.show_password:
            messagebox.showwarning("Hidden", "Click 'Show' first.")
            return
        try:
            pyperclip.copy(accounts[self.current_account]['password'])
            messagebox.showinfo("Success", "Password copied!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def add_account_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Account")
        dialog.geometry("450x600")
        dialog.configure(bg=Theme.bg_secondary)
        dialog.transient(self.root)
        dialog.grab_set()
        main = tk.Frame(dialog, bg=Theme.bg_secondary, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="Create New Account", bg=Theme.bg_secondary, fg=Theme.accent, font=Theme.heading_font).pack(anchor=tk.W, pady=(0,20))
        tk.Label(main, text="Nickname", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        name_var = tk.StringVar()
        ttk.Entry(main, textvariable=name_var).pack(fill=tk.X, pady=(5,10))
        tk.Label(main, text="App Name", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        app_var = tk.StringVar()
        ttk.Entry(main, textvariable=app_var).pack(fill=tk.X, pady=(5,10))
        tk.Label(main, text="Category", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        cat_var = tk.StringVar(value=self.config.get('default_category','Personal'))
        ttk.Combobox(main, textvariable=cat_var, values=["Academic","Personal","Internship","Other"], state="readonly").pack(fill=tk.X, pady=(5,10))
        tk.Label(main, text="Password", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        pwd_frame = tk.Frame(main, bg=Theme.bg_secondary)
        pwd_frame.pack(fill=tk.X, pady=(5,10))
        pwd_var = tk.StringVar()
        pwd_entry = ttk.Entry(pwd_frame, textvariable=pwd_var, show="•")
        pwd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(pwd_frame, text="Generate", command=lambda: pwd_var.set(generate_password())).pack(side=tk.RIGHT, padx=5)
        preview = tk.LabelFrame(main, text="Strength Preview", bg=Theme.bg_secondary, fg=Theme.text_muted)
        preview.pack(fill=tk.X, pady=10)
        bar = ttk.Progressbar(preview, length=350, mode='determinate')
        bar.pack(pady=5, padx=5)
        p_label = tk.Label(preview, text="", bg=Theme.bg_secondary, fg=Theme.text_secondary)
        p_label.pack()
        def update_preview(*a):
            pwd = pwd_var.get()
            if pwd:
                fb = get_password_feedback(pwd)
                bar['value'] = (fb['score']/10)*100
                p_label.config(text=f"{fb['category']} ({fb['score']:.1f}/10)", fg=Theme.strength_colors.get(fb['category']))
            else:
                bar['value'] = 0
                p_label.config(text="Enter a password")
        pwd_var.trace('w', update_preview)
        def save():
            name = name_var.get().strip()
            app = app_var.get().strip()
            cat = cat_var.get()
            pwd = pwd_var.get().strip()
            if not name or not app or not pwd:
                messagebox.showerror("Error", "All fields required")
                return
            cat = cat.lower().capitalize() if cat.lower() in ["academic","personal","internship"] else "Other"
            dup = any(d['app']==app and d['category']==cat and d['password']==pwd and n!=name for n,d in accounts.items())
            if dup and not messagebox.askyesno("Duplicate", "Account with same data exists. Save anyway?"): return
            if name in accounts and not messagebox.askyesno("Duplicate", f"'{name}' exists. Overwrite?"): return
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            accounts[name] = {"app": app, "category": cat, "password": pwd, "created": now, "last_modified": now}
            save_accounts()
            self.refresh_accounts()
            dialog.destroy()
        btn = tk.Frame(main, bg=Theme.bg_secondary)
        btn.pack(fill=tk.X, pady=(20,0))
        tk.Button(btn, text="Save", bg=Theme.accent, fg=Theme.text_primary, bd=0, padx=15, pady=5, command=save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn, text="Cancel", bg=Theme.bg_input, fg=Theme.text_primary, bd=0, padx=15, pady=5, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    def edit_account(self):
        if not self.current_account: return
        data = accounts[self.current_account]
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit — {self.current_account}")
        dialog.geometry("450x600")
        dialog.configure(bg=Theme.bg_secondary)
        dialog.transient(self.root)
        dialog.grab_set()
        main = tk.Frame(dialog, bg=Theme.bg_secondary, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="Edit Account", bg=Theme.bg_secondary, fg=Theme.accent, font=Theme.heading_font).pack(anchor=tk.W, pady=(0,20))
        tk.Label(main, text="Nickname", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        tk.Label(main, text=self.current_account, bg=Theme.bg_secondary, fg=Theme.text_primary).pack(anchor=tk.W, pady=(5,10))
        tk.Label(main, text="App Name", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        app_var = tk.StringVar(value=data['app'])
        ttk.Entry(main, textvariable=app_var).pack(fill=tk.X, pady=(5,10))
        tk.Label(main, text="Category", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        cat_var = tk.StringVar(value=data['category'])
        ttk.Combobox(main, textvariable=cat_var, values=["Academic","Personal","Internship","Other"], state="readonly").pack(fill=tk.X, pady=(5,10))
        tk.Label(main, text="Password", bg=Theme.bg_secondary, fg=Theme.text_muted).pack(anchor=tk.W)
        pwd_frame = tk.Frame(main, bg=Theme.bg_secondary)
        pwd_frame.pack(fill=tk.X, pady=(5,10))
        pwd_var = tk.StringVar(value=data['password'])
        pwd_entry = ttk.Entry(pwd_frame, textvariable=pwd_var, show="•")
        pwd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(pwd_frame, text="Generate", command=lambda: pwd_var.set(generate_password())).pack(side=tk.RIGHT, padx=5)
        preview = tk.LabelFrame(main, text="Strength Preview", bg=Theme.bg_secondary, fg=Theme.text_muted)
        preview.pack(fill=tk.X, pady=10)
        bar = ttk.Progressbar(preview, length=350, mode='determinate')
        bar.pack(pady=5, padx=5)
        p_label = tk.Label(preview, text="", bg=Theme.bg_secondary, fg=Theme.text_secondary)
        p_label.pack()
        def update_preview(*a):
            pwd = pwd_var.get()
            if pwd:
                fb = get_password_feedback(pwd)
                bar['value'] = (fb['score']/10)*100
                p_label.config(text=f"{fb['category']} ({fb['score']:.1f}/10)", fg=Theme.strength_colors.get(fb['category']))
            else:
                bar['value'] = 0
                p_label.config(text="Enter a password")
        pwd_var.trace('w', update_preview)
        update_preview()
        def save():
            accounts[self.current_account]['app'] = app_var.get()
            accounts[self.current_account]['category'] = cat_var.get()
            accounts[self.current_account]['password'] = pwd_var.get()
            accounts[self.current_account]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_accounts()
            self.refresh_accounts()
            self.update_panel(self.current_account)
            dialog.destroy()
        btn = tk.Frame(main, bg=Theme.bg_secondary)
        btn.pack(fill=tk.X, pady=(20,0))
        tk.Button(btn, text="Save", bg=Theme.accent, fg=Theme.text_primary, bd=0, padx=15, pady=5, command=save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn, text="Cancel", bg=Theme.bg_input, fg=Theme.text_primary, bd=0, padx=15, pady=5, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    def delete_account(self):
        if self.current_account and messagebox.askyesno("Delete", f"Delete '{self.current_account}'?"):
            del accounts[self.current_account]
            save_accounts()
            self.current_account = None
            self.refresh_accounts()
            self.clear_panel()
    def show_reuse_report(self):
        reused = detect_password_reuse()
        if not reused:
            messagebox.showinfo("Reuse Check", "✅ No reused passwords found!")
        else:
            ReuseReportWindow(self.root, reused)
    def show_health(self):
        if not accounts:
            messagebox.showinfo("Health", "No accounts to analyze")
        else:
            HealthDashboardWindow(self.root)
    def show_password_generator(self):
        pwd = generate_password(24)
        fb = get_password_feedback(pwd)
        if messagebox.askyesno("Generator", f"🔐 Generated:\n{pwd}\n\nStrength: {fb['category']} ({fb['score']:.1f}/10)\n⏱️ {estimate_crack_time(pwd)}\n\nCopy?"):
            try:
                pyperclip.copy(pwd)
                messagebox.showinfo("Success", "Copied!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    def suggest_better_password(self, new_pwd, dialog):
        if messagebox.askyesno("Use Password", f"Update '{self.current_account}' with this password?"):
            accounts[self.current_account]['password'] = new_pwd
            accounts[self.current_account]['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_accounts()
            self.refresh_accounts()
            self.update_panel(self.current_account)
            dialog.destroy()
            messagebox.showinfo("Updated", "Password updated!")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    splash = SplashScreen()
    splash.after(2000, splash.close)
    root = tk.Tk()
    app = GateKeeper(root)
    root.after(2100, root.deiconify)
    root.mainloop()

if __name__ == "__main__":
    main()
