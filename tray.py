# tray.py
import threading
import tkinter as tk
from tkinter import messagebox
import pyperclip
from DarkTheme import DarkTheme

TRAY_AVAILABLE = False
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    pass

class SystemTray:
    """System tray integration for background operation"""
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.icon = None
        self.tray_thread = None
        
        if TRAY_AVAILABLE and config.get('show_tray_icon', True):
            self.create_tray_icon()
    
    def create_tray_icon(self):
        """Create the system tray icon"""
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color=DarkTheme.bg_deep)
        draw = ImageDraw.Draw(image)
        
        # Draw a simple lock shape
        draw.rectangle([20, 25, 44, 45], fill=DarkTheme.accent_primary, outline=None)
        draw.rectangle([24, 15, 40, 25], fill=DarkTheme.accent_primary, outline=None)
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Show GateKeeper", self.show_window),
            pystray.MenuItem("Quick Add Account", self.quick_add),
            pystray.MenuItem("Generate Password", self.generate_password),
            pystray.MenuItem("Lock Now", self.lock_app),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Preferences", self.open_preferences),
            pystray.MenuItem("Exit", self.exit_app)
        )
        
        self.icon = pystray.Icon("gatekeeper", image, "GateKeeper", menu)
    
    def show_window(self):
        """Show the main window"""
        self.app.root.deiconify()
        self.app.root.lift()
        self.app.root.focus_force()
    
    def quick_add(self):
        """Open add account dialog"""
        self.app.root.deiconify()
        self.app.root.after(100, self.app.add_account_dialog)
    
    def generate_password(self):
        """Generate and copy a password"""
        from main import generate_password
        pwd = generate_password(16)
        pyperclip.copy(pwd)
        messagebox.showinfo("Password Generated", 
                           "Password copied to clipboard!\n\nYou can now paste it anywhere.")
    
    def lock_app(self):
        """Lock the app (minimize to tray)"""
        self.app.root.withdraw()
        if self.icon:
            self.show_notification("GateKeeper", "App is running in the background")
    
    def open_preferences(self):
        """Open preferences window"""
        self.app.root.deiconify()
        self.app.root.after(100, self.app.show_preferences)
    
    def show_notification(self, title, message):
        """Show a notification"""
        if hasattr(self.icon, 'notify'):
            self.icon.notify(message, title)
    
    def exit_app(self):
        """Exit the application"""
        if self.icon:
            self.icon.stop()
        self.app.quit_app()
    
    def run(self):
        """Run the tray icon in a separate thread"""
        if not TRAY_AVAILABLE or not self.config.get('show_tray_icon', True):
            return
        
        self.tray_thread = threading.Thread(target=self._run_icon, daemon=True)
        self.tray_thread.start()
    
    def _run_icon(self):
        """Internal method to run the icon"""
        if self.icon:
            self.icon.run()
    
    def stop(self):
        """Stop the tray icon"""
        if self.icon:
            self.icon.stop()
            self.icon = None
