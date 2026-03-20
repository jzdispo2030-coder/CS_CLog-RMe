# imports.py - Centralized import management for GateKeeper
import os
import sys

# Add vendor folder to Python path
vendor_path = os.path.join(os.path.dirname(__file__), 'vendor')
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)

# Try to import vendored packages
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
    print("✓ System tray features available")
except ImportError as e:
    print(f"⚠️  System tray features unavailable: {e}")
    TRAY_AVAILABLE = False
    pystray = None
    Image = None
    ImageDraw = None

# Pyperclip (already in repo)
try:
    import pyperclip
    print("✓ Clipboard features available")
except ImportError:
    pyperclip = None
    print("⚠️  Clipboard features unavailable")

# Export what's available
__all__ = ['pystray', 'Image', 'ImageDraw', 'TRAY_AVAILABLE', 'pyperclip']
