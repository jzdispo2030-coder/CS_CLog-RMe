#AI tools were used responsibly to support learning and development, not to replace understanding.

import re

def check_password_strength(password):
    score = 0
    issues = []

    # Length
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        issues.append("Too short (minimum 8 characters)")

    # Uppercase
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        issues.append("Add uppercase letters")

    # Numbers
    if re.search(r"[0-9]", password):
        score += 1
    else:
        issues.append("Add numbers")

    # Symbols
    if re.search(r"[!@#$%^&*()]", password):
        score += 1
    else:
        issues.append("Add symbols")

    return score, issues
