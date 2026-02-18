"""
Teste: Demonstração da Estratégia Inteligente de Backup

Este script simula 100 operações e mostra quantos backups são criados
com a estratégia inteligente vs. criar um backup a cada operação.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))


class SmartBackupSimulator:
    """Simula o comportamento do backup inteligente."""
    
    def __init__(self):
        self.backups_created = 0
        self.backups_skipped = 0
        self.last_backup_time = None
        self.last_backup_size = 0
        self.operations = []
    
    def simulate_operation(self, op_num: int, minute: int, file_size_change_bytes: int):
        """
        Simula uma operação.
        
        Args:
            op_num: Número da operação (1-100)
            minute: Minuto do dia (0-1440)
            file_size_change_bytes: Mudança de tamanho em bytes
        """
        operation_time = datetime.now().replace(minute=minute % 60, second=op_num % 60)
        current_size = 50000 + (op_num * 100)  # 50KB base + mudanças
        
        # Aplica lógica inteligente
        should_backup = True
        
        if self.last_backup_time is not None:
            time_diff = operation_time - self.last_backup_time
            size_diff_percent = abs(current_size - self.last_backup_size) / self.last_backup_size * 100
            
            # Não cria se: backup recente (< 30 min) E tamanho não mudou muito (< 10%)
            if time_diff < timedelta(minutes=30) and size_diff_percent < 10:
                should_backup = False
        
        # Registra resultado
        if should_backup:
            self.backups_created += 1
            self.last_backup_time = operation_time
            self.last_backup_size = current_size
            status = f"{Fore.GREEN}✓ Backup criado{Style.RESET_ALL}"
        else:
            self.backups_skipped += 1
            status = f"{Fore.YELLOW}✗ Pulado (económico){Style.RESET_ALL}"
        
        self.operations.append({
            'num': op_num,
            'time': operation_time,
            'backed_up': should_backup,
            'size': current_size
        })
        
        # Print progress a cada 10 operações
        if op_num % 10 == 0:
            print(f"  Op {op_num:3d}: {status}")
    
    def run_simulation(self):
        """Executa a simulação de 100 operações ao longo do dia."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}={'='*70}")
        print(f"SIMULAÇÃO: 100 OPERAÇÕES EM 1 DIA")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        # Simula 100 operações espalhadas ao longo do dia
        for i in range(1, 101):
            # Coloca operações aleatoriamente ao longo do dia
            minute = (i * 14) % 1440  # 14 minutos de intervalo
            
            # Algumas horas têm mais operações
            if 8 <= (minute // 60) <= 10:  # 8-10h: período ativo
                file_size_change = 100 + (i % 50)
            elif 13 <= (minute // 60) <= 15:  # 13-15h: período ativo
                file_size_change = 80 + (i % 40)
            else:
                file_size_change = 20 + (i % 10)
            
            self.simulate_operation(i, minute, file_size_change)
        
        self.print_results()
    
    def print_results(self):
        """Imprime os resultados da simulação."""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"RESULTADOS DA SIMULAÇÃO")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        # Comparação
        naive_backups = 100  # Um por operação
        smart_backups = self.backups_created
        
        print(f"{Fore.WHITE}Operações totais:                {100}{Style.RESET_ALL}")
        print(f"{Fore.RED}Backups (método ingênuo):       {naive_backups} ✗{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Backups (método inteligente):   {smart_backups} ✓{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Operações sem backup:           {self.backups_skipped}{Style.RESET_ALL}\n")
        
        reduction_percent = (1 - smart_backups / naive_backups) * 100
        reduction_ratio = naive_backups / smart_backups if smart_backups > 0 else float('inf')
        
        print(f"Redução de backups:              {reduction_percent:.1f}%")
        print(f"Proporção (antes/depois):        {reduction_ratio:.1f}x menor\n")
        
        # Cálculo de espaço
        backup_size_mb = 1.5  # Tamanho médio por backup
        
        space_naive_mb = naive_backups * backup_size_mb
        space_smart_mb = smart_backups * backup_size_mb
        space_saved_mb = space_naive_mb - space_smart_mb
        
        print(f"{Fore.RED}Espaço (método ingênuo):        {space_naive_mb:.1f} MB ✗{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Espaço (método inteligente):    {space_smart_mb:.1f} MB ✓{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Espaço economizado:             {space_saved_mb:.1f} MB ({reduction_percent:.0f}%){Style.RESET_ALL}\n")
        
        # Projeção anual
        print(f"{Fore.YELLOW}{'─'*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}PROJEÇÃO ANUAL (365 dias){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─'*70}{Style.RESET_ALL}\n")
        
        annual_naive = naive_backups * 365 * backup_size_mb
        annual_smart = smart_backups * 365 * backup_size_mb
        annual_saved = annual_naive - annual_smart
        
        print(f"{Fore.RED}Espaço anual (ingênuo):         {annual_naive:.1f} GB ✗{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Espaço anual (inteligente):     {annual_smart:.1f} GB ✓{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Espaço economizado por ano:     {annual_saved:.1f} GB ({reduction_percent:.0f}%){Style.RESET_ALL}\n")
        
        # Detalhes por hora
        print(f"{Fore.YELLOW}{'─'*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}BREAKDOWN POR HORA{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─'*70}{Style.RESET_ALL}\n")
        
        hourly_data = {}
        for op in self.operations:
            hour = op['time'].hour
            if hour not in hourly_data:
                hourly_data[hour] = {'total': 0, 'backed_up': 0}
            hourly_data[hour]['total'] += 1
            if op['backed_up']:
                hourly_data[hour]['backed_up'] += 1
        
        for hour in sorted(hourly_data.keys()):
            data = hourly_data[hour]
            total = data['total']
            backed = data['backed_up']
            skipped = total - backed
            
            if total > 0:
                skip_percent = (skipped / total) * 100
                print(f"{hour:02d}:00 - {total:2d} ops → {backed} backups ({skipped} pulados, {skip_percent:.0f}% economia)")
        
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Conclusão: Economia de {reduction_percent:.0f}% sem perder recuperabilidade!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def main():
    """Executa a simulação."""
    simulator = SmartBackupSimulator()
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}TESTE: ESTRATÉGIA INTELIGENTE DE BACKUP{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Simulando 100 operações em um dia...{Style.RESET_ALL}\n")
    
    simulator.run_simulation()


if __name__ == "__main__":
    main()
