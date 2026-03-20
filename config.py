# config.py
import json
import os

CONFIG_FILE = "gatekeeper_config.json"
WINDOW_CONFIG = "window_config.json"

class Config:
    """Manage application configuration"""
    
    DEFAULT_CONFIG = {
        'auto_lock': '5 minutes',
        'default_category': 'Personal',
        'theme': 'Dark',
        'start_minimized': False,
        'auto_save': True,
        'lock_on_minimize': True,
        'show_tray_icon': True,
        'remember_window_position': True
    }
    
    @classmethod
    def load(cls):
        """Load configuration from file"""
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
        """Save configuration to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    
    @classmethod
    def load_window_position(cls):
        """Load window position from file"""
        if os.path.exists(WINDOW_CONFIG):
            try:
                with open(WINDOW_CONFIG, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    @classmethod
    def save_window_position(cls, x, y, width, height):
        """Save window position to file"""
        config = {
            'x': x, 'y': y,
            'width': width, 'height': height
        }
        with open(WINDOW_CONFIG, 'w') as f:
            json.dump(config, f, indent=4)
