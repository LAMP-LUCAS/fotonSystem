import re

def sanitize_filename(name):
    """
    Removes invalid characters from a filename.
    Allowed: Alphanumeric, spaces, hyphens, underscores, dots.
    """
    # Remove invalid characters for Windows: < > : " / \ | ? *
    # Also removing control characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '', name)
    # Remove leading/trailing spaces and dots
    cleaned = cleaned.strip().strip('.')
    return cleaned

def validate_filename(name):
    """
    Checks if a filename contains invalid characters.
    Returns True if valid, False otherwise.
    """
    if not name:
        return False
    
    # Check for invalid characters
    if re.search(r'[<>:"/\\|?*]', name):
        return False
        
    # Check for reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
    reserved = {'CON', 'PRN', 'AUX', 'NUL'}
    reserved.update({f'COM{i}' for i in range(1, 10)})
    reserved.update({f'LPT{i}' for i in range(1, 10)})
    
    if name.upper() in reserved:
        return False
        
    return True
