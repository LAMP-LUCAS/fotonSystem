from datetime import datetime, timedelta

class CubService:
    """
    Service responsible for CUB (Custo Unitário Básico) intelligence.
    """

    BASE_URL = "https://www.sinduscongoias.com.br/arquivos/download/cub"

    @staticmethod
    def get_reference_month_data():
        """
        Returns the reference month/year for the *latest* available CUB.
        Usually, the CUB available today is from the previous month.
        """
        today = datetime.now()
        # Go back to the first day of this month, then subtract 1 day to get previous month
        first_of_this_month = today.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        
        return last_month

    @staticmethod
    def get_dynamic_url():
        """
        Constructs the URL for the PDF based on the logic:
        cub-{month_name}-{year}.pdf
        """
        ref_date = CubService.get_reference_month_data()
        
        months = {
            1: 'janeiro', 2: 'fevereiro', 3: 'marco', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        month_name = months[ref_date.month]
        year = ref_date.year
        
        # Construct URL
        # Example: https://www.sinduscongoias.com.br/arquivos/download/cub/cub-dezembro-2025.pdf
        return f"{CubService.BASE_URL}/cub-{month_name}-{year}.pdf"

    @staticmethod
    def get_reference_label():
        """Returns 'Dezembro/2025' for example"""
        ref_date = CubService.get_reference_month_data()
        months = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return f"{months[ref_date.month]}/{ref_date.year}"
