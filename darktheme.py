# DarkTheme.py
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
    monospace_font = ("Consolas", 10) if __import__('os').name == 'nt' else ("Menlo", 10)
