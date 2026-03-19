#AI tools were used responsibly to support learning and development, not to replace understanding.

import re
import math

def check_password_strength(password):
    """
    Advanced password strength checker
    Returns: score (0-10), issues list
    """
    score = 0
    issues = []
    
    if not password:
        return 0, ["Password is empty"]
    
    length = len(password)
    
    # =========================================================================
    # LENGTH SCORING (0-4 points) - Much more nuanced
    # =========================================================================
    if length >= 20:
        score += 4
    elif length >= 16:
        score += 3.5
    elif length >= 14:
        score += 3
    elif length >= 12:
        score += 2.5
    elif length >= 10:
        score += 2
    elif length >= 8:
        score += 1
    else:
        issues.append(f"Too short ({length} chars) - minimum 8 recommended")
        if length < 6:
            issues.append("CRITICAL: Password is extremely short")
    
    # =========================================================================
    # CHARACTER VARIETY SCORING (0-3 points)
    # =========================================================================
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_symbol = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", password))
    
    # Count character types (0-4)
    char_types = sum([has_lower, has_upper, has_digit, has_symbol])
    
    if char_types == 4:
        score += 3
    elif char_types == 3:
        score += 2
    elif char_types == 2:
        score += 1
    elif char_types <= 1:
        issues.append("Very limited character variety")
    
    # Individual character type feedback
    if not has_lower:
        issues.append("Add lowercase letters")
    if not has_upper:
        issues.append("Add UPPERCASE letters")
    if not has_digit:
        issues.append("Add numbers")
    if not has_symbol:
        issues.append("Add symbols (!@#$% etc.)")
    
    # =========================================================================
    # UNIQUE CHARACTERS (0-1 point)
    # =========================================================================
    unique_chars = len(set(password))
    unique_ratio = unique_chars / length if length > 0 else 0
    
    if unique_ratio > 0.7:
        score += 1
    elif unique_ratio < 0.4 and length > 6:
        issues.append("Too many repeated characters")
    
    # =========================================================================
    # PATTERN DETECTION (Penalties)
    # =========================================================================
    
    # Check for sequential characters (abc, 123)
    sequences = [
        'abcdefghijklmnopqrstuvwxyz',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        '0123456789',
        'qwertyuiop', 'asdfghjkl', 'zxcvbnm',  # Keyboard rows
        '!@#$%^&*()'
    ]
    
    for seq in sequences:
        for i in range(len(seq) - 2):
            pattern = seq[i:i+3]
            if pattern in password.lower():
                score = max(0, score - 1)
                issues.append(f"Contains sequential pattern '{pattern}'")
                break
    
    # Check for repeated patterns (aaa, 111)
    for i in range(len(password) - 2):
        if password[i] == password[i+1] == password[i+2]:
            score = max(0, score - 1)
            issues.append(f"Contains repeated character '{password[i]}' (3+ times)")
            break
    
    # Check for common words (simplified check)
    common_words = ['password', 'admin', 'user', 'login', 'welcome', 'qwerty', 
                    'abc123', 'letmein', 'monkey', 'dragon', 'master', 'hello',
                    'freedom', 'whatever', 'pass', 'pwd', '123456', 'iloveyou']
    
    password_lower = password.lower()
    for word in common_words:
        if word in password_lower:
            if word == password_lower:
                score = max(0, score - 3)
                issues.append(f"Password is a common word: '{word}'")
            elif len(word) >= 4:
                score = max(0, score - 1)
                issues.append(f"Contains common word: '{word}'")
            break
    
    # Check for dates (like 2024, 1999)
    date_pattern = r'(19|20)\d{2}'
    if re.search(date_pattern, password):
        score = max(0, score - 1)
        issues.append("Contains a year (easily guessed)")
    
    # Check for keyboard patterns
    keyboard_patterns = ['qwerty', 'asdf', 'zxcv', '1234', '5678', 'qwertyuiop']
    for pattern in keyboard_patterns:
        if pattern in password_lower:
            score = max(0, score - 1)
            issues.append(f"Contains keyboard pattern: '{pattern}'")
            break
    
    # =========================================================================
    # FINAL SCORE NORMALIZATION (0-10 scale)
    # =========================================================================
    # Ensure score is within 0-10 range
    final_score = max(0, min(10, score))
    
    # Remove duplicate issues
    issues = list(dict.fromkeys(issues))
    
    return final_score, issues


def get_password_feedback(password):
    """Return user-friendly feedback for a password"""
    score, issues = check_password_strength(password)
    
    # Generate strengths based on what's GOOD about the password
    strengths = []
    length = len(password)
    
    if length >= 16:
        strengths.append("Excellent length (16+ characters)")
    elif length >= 12:
        strengths.append("Good length (12+ characters)")
    
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_symbol = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]", password))
    
    char_types = sum([has_lower, has_upper, has_digit, has_symbol])
    if char_types >= 3:
        strengths.append(f"Good character variety ({char_types}/4 types)")
    
    unique_chars = len(set(password))
    unique_ratio = unique_chars / length if length > 0 else 0
    if unique_ratio > 0.6:
        strengths.append("Good character uniqueness")
    
    # Determine category
    if score >= 9:
        category = "Excellent"
    elif score >= 7.5:
        category = "Very Strong"
    elif score >= 6:
        category = "Strong"
    elif score >= 4.5:
        category = "Good"
    elif score >= 3:
        category = "Fair"
    elif score >= 1.5:
        category = "Weak"
    else:
        category = "Very Weak"
    
    feedback = {
        'score': score,
        'category': category,
        'issues': issues,
        'strengths': strengths,
        'color': get_strength_color(category)
    }
    
    return feedback


def get_strength_color(category):
    """Return color code for strength category"""
    colors = {
        "Excellent": "#2ecc71",      # Bright green
        "Very Strong": "#27ae60",     # Green
        "Strong": "#3498db",          # Blue
        "Good": "#f39c12",            # Orange
        "Fair": "#f1c40f",            # Yellow
        "Weak": "#e67e22",             # Dark orange
        "Very Weak": "#e74c3c"         # Red
    }
    return colors.get(category, "#95a5a6")  # Gray default


def estimate_crack_time(password):
    """Estimate time to crack the password"""
    score, _ = check_password_strength(password)
    
    # Rough estimate based on score
    if score >= 9:
        return "centuries"
    elif score >= 7.5:
        return "hundreds of years"
    elif score >= 6:
        return "decades"
    elif score >= 4.5:
        return "years"
    elif score >= 3:
        return "months"
    elif score >= 1.5:
        return "weeks"
    elif score >= 0.5:
        return "days"
    else:
        return "seconds"
