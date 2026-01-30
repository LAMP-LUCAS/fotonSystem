import locale
from datetime import datetime

class FotonFormatter:
    """
    Centralizes formatting rules for the Foton System.
    Ensures consistency for LLMs and final documents.
    """

    @staticmethod
    def format_currency(value):
        """Converts float/int/str to 'R$ 1.234,56'"""
        try:
            val_float = FotonFormatter.parse_br_number(value)
            # Custom formatting to avoid OS locale dependencies
            return f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return value

    @staticmethod
    def format_decimal(value):
        """Converts float/int/str to '1.234,56'"""
        try:
            val_float = FotonFormatter.parse_br_number(value)
            return f"{val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return value

    @staticmethod
    def parse_br_number(value_str):
        """Converts '1.234,56' or 'R$ 1.234,56' or '5000.00' to float"""
        if isinstance(value_str, (int, float)):
            return float(value_str)
        
        try:
            clean = str(value_str).replace('R$', '').strip()
            
            # Logic to distinguish 1.000,00 (BR) from 1000.00 (US)
            if ',' in clean:
                # Assume BR format: remove thousands separator (.), replace decimal (,)
                clean = clean.replace('.', '').replace(',', '.')
            else:
                # No comma. 
                # If multiple dots (1.000.000), it's likely thousands separator -> remove them.
                # If single dot (1000.00), it could be US decimal.
                if clean.count('.') > 1:
                     clean = clean.replace('.', '')
                # If single dot, we generally assume it's a decimal point in programming contexts
                # unless it's explicitly "1.000" (which implies 1000).
                # But "5000.00" is definitely 5000.
                pass 

            return float(clean)
        except:
            return 0.0

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
