# ui_components.py
import tkinter as tk
from tkinter import ttk
from DarkTheme import DarkTheme

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
        self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius, 
                                 fill=color, outline="")
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

class ModernTitleBar(tk.Frame):
    """Custom title bar for app-like feel"""
    def __init__(self, master, app_name="GateKeeper", on_close=None, on_minimize=None):
        super().__init__(master, bg=DarkTheme.bg_deep, height=40)
        self.master = master
        self.on_close = on_close
        self.on_minimize = on_minimize
        self.pack(fill=tk.X, side=tk.TOP)
        
        # App icon and name
        icon_label = tk.Label(self, text="🔐", bg=DarkTheme.bg_deep, 
                              fg=DarkTheme.accent_primary, font=("Segoe UI", 14))
        icon_label.pack(side=tk.LEFT, padx=(10, 5))
        
        title_label = tk.Label(self, text=app_name, bg=DarkTheme.bg_deep,
                               fg=DarkTheme.text_primary, font=("Segoe UI", 11, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Window controls
        controls_frame = tk.Frame(self, bg=DarkTheme.bg_deep)
        controls_frame.pack(side=tk.RIGHT, padx=10)
        
        # Minimize button
        min_btn = tk.Button(controls_frame, text="─", bg=DarkTheme.bg_deep,
                           fg=DarkTheme.text_primary, bd=0, font=("Segoe UI", 12),
                           activebackground=DarkTheme.bg_light,
                           command=self.minimize_window)
        min_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(controls_frame, text="✕", bg=DarkTheme.bg_deep,
                             fg=DarkTheme.accent_danger, bd=0, font=("Segoe UI", 12),
                             activebackground=DarkTheme.accent_danger,
                             activeforeground="white",
                             command=self.close_window)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Make window draggable
        for widget in [self, icon_label, title_label]:
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.on_move)
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")
    
    def minimize_window(self):
        if self.on_minimize:
            self.on_minimize()
        else:
            self.master.iconify()
    
    def close_window(self):
        if self.on_close:
            self.on_close()
        else:
            self.master.quit()
