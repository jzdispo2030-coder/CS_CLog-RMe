#!/usr/bin/env python3
"""
GateKeeper Launcher - With error handling
"""

import sys
import traceback

def main():
    try:
        import main
        main.main()
    except ImportError as e:
        print(f"Error: Missing module - {e}")
        print("\nMake sure all files are in the same directory:")
        print("  - main.py")
        print("  - password_checker.py")
        print("  - pyperclip.py")
        print("  - accounts.json")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("\nError details:")
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
