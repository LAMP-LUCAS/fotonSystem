import locale
import re
from datetime import datetime

class FotonFormatter:
    """
    Centralizes formatting rules for the Foton System.
    Ensures consistency for LLMs and final documents.
    """

    @staticmethod
    def format_currency(value):
        """
        Converts value to Brazilian decimal string with R$ prefix.
        Used for presentation (CLI/MCP reports).
        """
        try:
            formatted = FotonFormatter.format_decimal(value)
            return f"R$ {formatted}"
        except Exception:
            return f"R$ {value}"


    @staticmethod
    def format_decimal(value):
        """Converts float/int/str to '1.234,56'"""
        try:
            val_float = FotonFormatter.parse_br_number(value)
            # Custom formatting to avoid OS locale dependencies
            return f"{val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return value

    @staticmethod
    def smart_format(key, value_str):
        """
        Decides formatting based on content and key:
        - If in quotes ("2026"): returns literal without quotes.
        - If key ends with '%': returns formatted percentage (e.g. 0.14 -> 14,00%).
        - If pure number (140): returns formatted decimal (140,00).
        - If text: returns as is.
        """
        if value_str is None:
            return ""
            
        if not isinstance(value_str, str):
            value_str = str(value_str)

        stripped = value_str.strip()
        if not stripped:
            return ""
        
        # 1. Literal Check (Quotes)
        if (stripped.startswith('"') and stripped.endswith('"')) or \
           (stripped.startswith("'") and stripped.endswith("'")):
            return stripped[1:-1]

        # 2. Decimal and Percentage Check
        try:
            # We only want to format if the ENTIRE string is a numeric value
            # Remove currency and units for the check
            check_val = stripped.replace('R$', '').replace('m²', '').replace('m2', '').strip()
            
            # If it's a percentage key, we expect a decimal like 0.14
            if str(key).endswith('%'):
                clean_val = FotonFormatter.parse_br_number(check_val)
                perc_val = clean_val * 100
                return f"{perc_val:.2f}%".replace('.', ',')
            
            # For other keys, only format if it looks like a stand-alone number
            # This prevents converting "Galpão de 140m2" into "0,00"
            if re.match(r'^-?[\d\.,]+$', check_val):
                clean_val = FotonFormatter.parse_br_number(check_val)
                return FotonFormatter.format_decimal(clean_val)
        except (ValueError, TypeError):
            pass

        # 3. Fallback to raw text
        return value_str

    @staticmethod
    def parse_br_number(value_str):
        """Converts '1.234,56' or 'R$ 1.234,56' or '5000.00' to float"""
        if isinstance(value_str, (int, float)):
            return float(value_str)
        
        clean = str(value_str).replace('R$', '').replace('m²', '').replace('m2', '').strip()
        
        if not clean:
            raise ValueError("Empty string is not a number")

        # Logic to distinguish 1.000,00 (BR) from 1000.00 (US)
        if ',' in clean:
            # Assume BR format: remove thousands separator (.), replace decimal (,)
            clean = clean.replace('.', '').replace(',', '.')
        else:
            # No comma. 
            # If multiple dots (1.000.000), it's likely thousands separator -> remove them.
            if clean.count('.') > 1:
                 clean = clean.replace('.', '')
        
        return float(clean)

    @staticmethod
    def get_full_date(date_obj=None):
        """Returns '29 de Janeiro de 2026'"""
        if not date_obj:
            date_obj = datetime.now()
        
        months = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        return f"{date_obj.day} de {months[date_obj.month]} de {date_obj.year}"
