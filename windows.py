# windows.py
import tkinter as tk
from tkinter import ttk, messagebox
from DarkTheme import DarkTheme
from ui_components import ModernEntry

class SplashScreen(tk.Toplevel):
    """Professional splash screen for app startup"""
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry("450x300")
        self.configure(bg=DarkTheme.bg_deep)
        self.overrideredirect(True)
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(self, bg=DarkTheme.bg_deep)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo
        logo_label = tk.Label(main_frame, text="🔐", bg=DarkTheme.bg_deep,
                              fg=DarkTheme.accent_primary, font=("Segoe UI", 64))
        logo_label.pack(pady=(40, 10))
        
        # App name
        name_label = tk.Label(main_frame, text="GateKeeper", bg=DarkTheme.bg_deep,
                              fg=DarkTheme.text_primary, font=("Segoe UI", 24, "bold"))
        name_label.pack()
        
        # Tagline
        tagline_label = tk.Label(main_frame, text="secure password manager", 
                                 bg=DarkTheme.bg_deep, fg=DarkTheme.text_muted,
                                 font=("Segoe UI", 11))
        tagline_label.pack(pady=(5, 20))
        
        # Loading bar
        self.progress = ttk.Progressbar(main_frame, length=300, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Version
        version_label = tk.Label(main_frame, text="v2.5.0", bg=DarkTheme.bg_deep,
                                 fg=DarkTheme.text_muted, font=("Segoe UI", 9))
        version_label.pack(side=tk.BOTTOM, pady=10)
        
        self.update()
    
    def close(self):
        self.progress.stop()
        self.destroy()

class PreferencesWindow(tk.Toplevel):
    """User preferences for the app"""
    def __init__(self, parent, config, on_save=None):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.on_save = on_save
        
        self.title("Preferences")
        self.geometry("500x450")
        self.configure(bg=DarkTheme.bg_deep)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (500 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (450 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self, style='Deep.TFrame', padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Settings", 
                 font=DarkTheme.heading_font,
                 foreground=DarkTheme.accent_primary).pack(pady=(0, 20))
        
        # Auto-lock setting
        lock_frame = ttk.Frame(main_frame)
        lock_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(lock_frame, text="Auto-lock after:", 
                 font=DarkTheme.body_font).pack(side=tk.LEFT)
        
        self.lock_var = tk.StringVar(value=self.config.get('auto_lock', '5 minutes'))
        lock_combo = ttk.Combobox(lock_frame, textvariable=self.lock_var,
                                  values=["1 minute", "5 minutes", "15 minutes", "30 minutes", "Never"],
                                  width=18, state="readonly")
        lock_combo.pack(side=tk.RIGHT)
        
        # Default category
        cat_frame = ttk.Frame(main_frame)
        cat_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(cat_frame, text="Default category:", 
                 font=DarkTheme.body_font).pack(side=tk.LEFT)
        
        self.cat_var = tk.StringVar(value=self.config.get('default_category', 'Personal'))
        cat_combo = ttk.Combobox(cat_frame, textvariable=self.cat_var,
                                 values=["Academic", "Personal", "Internship", "Other"],
                                 width=18, state="readonly")
        cat_combo.pack(side=tk.RIGHT)
        
        # Theme selection
        theme_frame = ttk.Frame(main_frame)
        theme_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(theme_frame, text="Theme:", 
                 font=DarkTheme.body_font).pack(side=tk.LEFT)
        
        self.theme_var = tk.StringVar(value=self.config.get('theme', 'Dark'))
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                   values=["Dark", "Light", "System"],
                                   width=18, state="readonly")
        theme_combo.pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Checkboxes
        self.min_var = tk.BooleanVar(value=self.config.get('start_minimized', False))
        ttk.Checkbutton(main_frame, text="Start minimized to system tray",
                       variable=self.min_var).pack(anchor=tk.W, pady=3)
        
        self.lock_min_var = tk.BooleanVar(value=self.config.get('lock_on_minimize', True))
        ttk.Checkbutton(main_frame, text="Lock when minimized",
                       variable=self.lock_min_var).pack(anchor=tk.W, pady=3)
        
        self.tray_var = tk.BooleanVar(value=self.config.get('show_tray_icon', True))
        ttk.Checkbutton(main_frame, text="Show system tray icon",
                       variable=self.tray_var).pack(anchor=tk.W, pady=3)
        
        self.save_var = tk.BooleanVar(value=self.config.get('auto_save', True))
        ttk.Checkbutton(main_frame, text="Automatically save on exit",
                       variable=self.save_var).pack(anchor=tk.W, pady=3)
        
        self.pos_var = tk.BooleanVar(value=self.config.get('remember_window_position', True))
        ttk.Checkbutton(main_frame, text="Remember window position",
                       variable=self.pos_var).pack(anchor=tk.W, pady=3)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Save", command=self.save_preferences,
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy,
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset_defaults,
                  width=15).pack(side=tk.RIGHT, padx=5)
    
    def save_preferences(self):
        new_config = {
            'auto_lock': self.lock_var.get(),
            'default_category': self.cat_var.get(),
            'theme': self.theme_var.get(),
            'start_minimized': self.min_var.get(),
            'lock_on_minimize': self.lock_min_var.get(),
            'show_tray_icon': self.tray_var.get(),
            'auto_save': self.save_var.get(),
            'remember_window_position': self.pos_var.get()
        }
        if self.on_save:
            self.on_save(new_config)
        messagebox.showinfo("Success", "Preferences saved!")
        self.destroy()
    
    def reset_defaults(self):
        from config import Config
        self.lock_var.set(Config.DEFAULT_CONFIG['auto_lock'])
        self.cat_var.set(Config.DEFAULT_CONFIG['default_category'])
        self.theme_var.set(Config.DEFAULT_CONFIG['theme'])
        self.min_var.set(Config.DEFAULT_CONFIG['start_minimized'])
        self.lock_min_var.set(Config.DEFAULT_CONFIG['lock_on_minimize'])
        self.tray_var.set(Config.DEFAULT_CONFIG['show_tray_icon'])
        self.save_var.set(Config.DEFAULT_CONFIG['auto_save'])
        self.pos_var.set(Config.DEFAULT_CONFIG['remember_window_position'])

class ShortcutsWindow(tk.Toplevel):
    """Help window showing keyboard shortcuts"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Keyboard Shortcuts")
        self.geometry("450x400")
        self.configure(bg=DarkTheme.bg_deep)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (450 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(self, style='Deep.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Keyboard Shortcuts", 
                 font=DarkTheme.heading_font,
                 foreground=DarkTheme.accent_primary).pack(pady=(0, 15))
        
        shortcuts = [
            ("⌘N / Ctrl+N", "New Account"),
            ("⌘R / Ctrl+R", "Refresh List"),
            ("⌘F / Ctrl+F", "Focus Search"),
            ("⌘D / Ctrl+D", "Delete Selected"),
            ("⌘E / Ctrl+E", "Edit Selected"),
            ("⌘C / Ctrl+C", "Copy Password"),
            ("⌘, / Ctrl+,", "Preferences"),
            ("⌘H / Ctrl+H", "Hide to Tray"),
            ("⌘Q / Ctrl+Q", "Quit Application"),
            ("⌘? / Ctrl+?", "Show Shortcuts"),
            ("Esc", "Close Dialog"),
            ("Enter", "Save/Confirm"),
        ]
        
        # Create a frame with scrollbar
        canvas = tk.Canvas(main_frame, bg=DarkTheme.bg_deep, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for key, action in shortcuts:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5)
            
            key_label = tk.Label(frame, text=key, bg=DarkTheme.bg_input,
                                 fg=DarkTheme.accent_info, font=("Segoe UI", 9, "bold"),
                                 padx=8, pady=4)
            key_label.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=action, style='Muted.TLabel').pack(side=tk.LEFT, padx=(15, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(main_frame, text="Close", command=self.destroy).pack(pady=15)

class AboutWindow(tk.Toplevel):
    """About dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About GateKeeper")
        self.geometry("400x350")
        self.configure(bg=DarkTheme.bg_deep)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (350 // 2)
        self.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(self, style='Deep.TFrame', padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo
        logo_label = tk.Label(main_frame, text="🔐", bg=DarkTheme.bg_deep,
                              fg=DarkTheme.accent_primary, font=("Segoe UI", 48))
        logo_label.pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="GateKeeper", 
                 font=("Segoe UI", 18, "bold"),
                 foreground=DarkTheme.accent_primary).pack()
        
        ttk.Label(main_frame, text="Version 2.5.0", 
                 style='Muted.TLabel').pack(pady=5)
        
        ttk.Label(main_frame, text="A secure password manager for students and professionals",
                 wraplength=300, justify=tk.CENTER).pack(pady=10)
        
        ttk.Label(main_frame, text="© 2026 GateKeeper Team\nAI tools used responsibly",
                 style='Muted.TLabel', justify=tk.CENTER).pack(pady=10)
        
        ttk.Button(main_frame, text="Close", command=self.destroy).pack(pady=10)
