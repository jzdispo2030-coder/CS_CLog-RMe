# vendor/__init__.py
import os
import sys

# Add the vendor directory to Python's import path
vendor_dir = os.path.dirname(__file__)
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)
