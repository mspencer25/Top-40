"""
Utility Functions
Helper functions for formatting and display
"""

def format_currency(value: float) -> str:
    """
    Format number as currency
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted currency string
    """
    if value is None or value == 0:
        return "$0"
    
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:,.1f}K"
    else:
        return f"${value:,.2f}"

def format_number(value: float) -> str:
    """
    Format number with commas
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted number string
    """
    if value is None or value == 0:
        return "0"
    
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:,.1f}K"
    else:
        return f"{value:,.0f}"

def format_percentage(value: float) -> str:
    """
    Format number as percentage
    
    Args:
        value: Numeric value (already in percentage form, e.g., 47.5)
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "0.0%"
    
    return f"{value:.1f}%"

def validate_date_range(start_date, end_date) -> bool:
    """
    Validate that date range is logical
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid, False otherwise
    """
    return start_date <= end_date

def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if text is None:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."
