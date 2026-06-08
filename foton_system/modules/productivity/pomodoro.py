import time
import threading
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()

try:
    from plyer import notification
    PLYER_AVAILABLE: bool = True
except ImportError:
    logger.warning("Biblioteca 'plyer' não encontrada. Notificações visuais desativadas.")
    PLYER_AVAILABLE = False


class PomodoroTimer:
    """Timer Pomodoro com ciclos de trabalho/pausa, notificações e registro em timesheet."""

    def __init__(
        self,
        work_time: int,
        short_break_time: int,
        long_break_time: int,
        cycles: int,
        client_alias: Optional[str] = None,
        service_alias: Optional[str] = None,
    ) -> None:
        self.work_time: int = work_time * 60
        self.short_break_time: int = short_break_time * 60
        self.long_break_time: int = long_break_time * 60
        self.cycles: int = cycles
        self.client_alias: Optional[str] = client_alias
        self.service_alias: Optional[str] = service_alias
        self.current_cycle: int = 0
        self.cycle_records: List[Dict[str, Any]] = []

    def run(self) -> None:
        """Executa o ciclo completo de pomodoro: trabalho + pausas alternadas + relatório."""
        while self.current_cycle < self.cycles:
            self.current_cycle += 1
            print(f'\nIniciando ciclo {self.current_cycle} de trabalho.\n')
            if self.client_alias:
                print(f"Cliente: {self.client_alias} | Serviço: {self.service_alias or 'N/A'}")
            
            self.play_sound('inicio')
            
            work_duration: float = self.run_timer(self.work_time, 'Tempo de trabalho encerrado!')
            self.notify("Tempo de trabalho encerrado", f"Ciclo {self.current_cycle} concluído.")

            break_duration: float = 0
            break_type: str = 'nenhuma'

            if self.current_cycle < self.cycles:
                if self.current_cycle % 4 == 0:
                    self.play_sound('inicio')
                    print(f'\nIniciando pausa longa após ciclo {self.current_cycle}.\n')
                    break_duration = self.run_timer(self.long_break_time, 'Pausa longa encerrada.')
                    break_type = 'longa'
                else:
                    self.play_sound('inicio')
                    print(f'\nIniciando pausa curta após ciclo {self.current_cycle}.')
                    break_duration = self.run_timer(self.short_break_time, 'Pausa curta encerrada.')
                    break_type = 'curta'
                
                self.play_sound('fim')
                self.notify("Pausa encerrada", "Hora de voltar ao trabalho.")

            self.cycle_records.append({
                'cycle_number': self.current_cycle,
                'work_duration': work_duration,
                'break_duration': break_duration,
                'break_type': break_type,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'client': self.client_alias,
                'service': self.service_alias
            })

        self.show_report()
        self._save_to_timesheet()

    def run_timer(self, duration: float, message: str) -> float:
        """Executa contagem regressiva com exibição no terminal."""
        start_time: float = time.time()
        try:
            while time.time() - start_time < duration:
                elapsed: float = time.time() - start_time
                remaining: float = duration - elapsed
                minutes: int
                seconds: int
                minutes, seconds = divmod(int(remaining), 60)
                sys.stdout.write(f"\rTempo restante: {minutes:02d}:{seconds:02d} ")
                sys.stdout.flush()
                time.sleep(1)
            print(f"\n{message}")
            return duration
        except KeyboardInterrupt:
            print("\nTimer interrompido.")
            return time.time() - start_time

    def play_sound(self, signal_type: str = 'fim') -> None:
        """Toca beep de início ou fim. Fallback para bell ANSI se winsound indisponível."""
        try:
            import winsound
            if signal_type == 'inicio':
                winsound.Beep(1000, 500)
            elif signal_type == 'fim':
                winsound.Beep(500, 500)
                time.sleep(0.2)
                winsound.Beep(500, 500)
        except ImportError:
            # Linux/headless: usa bell ANSI
            sys.stderr.write('\a')
            sys.stderr.flush()
        except Exception as e:
            logger.error(f"Erro ao reproduzir som: {e}")

    def notify(self, title: str, message: str) -> None:
        """Envia notificação visual via plyer (se disponível)."""
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=f"Pomodoro - {title}",
                    message=message,
                    app_name="LAMP Pomodoro",
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Erro na notificação: {e}")

    def show_report(self) -> None:
        """Exibe relatório dos ciclos concluídos."""
        print("\nCiclos concluídos. Relatório:")
        for record in self.cycle_records:
            print(f"Ciclo {record['cycle_number']}: "
                  f"Trabalho {record['work_duration']/60:.1f}m, "
                  f"Pausa {record['break_duration']/60:.1f}m ({record['break_type']})")

    def _save_to_timesheet(self) -> None:
        """Persiste os registros dos ciclos no arquivo timesheet.csv."""
        try:
            from foton_system.modules.shared.infrastructure.config.config import Config
            import csv
            
            base_dir: Path = Config().base_dados.parent
            timesheet_path: Path = base_dir / 'timesheet.csv'
            
            file_exists: bool = timesheet_path.exists()
            
            with open(timesheet_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Timestamp', 'Client', 'Service', 'WorkDuration(min)', 'BreakDuration(min)', 'Cycle'])
                
                for record in self.cycle_records:
                    writer.writerow([
                        record['timestamp'],
                        record['client'] or 'N/A',
                        record['service'] or 'N/A',
                        f"{record['work_duration']/60:.2f}",
                        f"{record['break_duration']/60:.2f}",
                        record['cycle_number']
                    ])
            
            print(f"Dados salvos em: {timesheet_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar timesheet: {e}")
