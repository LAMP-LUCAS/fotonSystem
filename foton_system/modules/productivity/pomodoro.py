import time
import threading
import sys
import winsound
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    logger.warning("Biblioteca 'plyer' não encontrada. Notificações visuais desativadas.")
    PLYER_AVAILABLE = False

class PomodoroTimer:
    def __init__(self, work_time, short_break_time, long_break_time, cycles):     
        self.work_time = work_time * 60
        self.short_break_time = short_break_time * 60
        self.long_break_time = long_break_time * 60
        self.cycles = cycles
        self.current_cycle = 0
        self.cycle_records = []

    def run(self):
        while self.current_cycle < self.cycles:
            self.current_cycle += 1
            print(f'\nIniciando ciclo {self.current_cycle} de trabalho.\n')
            self.play_sound('inicio')
            
            work_duration = self.run_timer(self.work_time, 'Tempo de trabalho encerrado!')
            self.notify("Tempo de trabalho encerrado", f"Ciclo {self.current_cycle} concluído.")

            break_duration = 0
            break_type = 'nenhuma'

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
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })

        self.show_report()

    def run_timer(self, duration, message):
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                remaining = duration - elapsed
                minutes, seconds = divmod(int(remaining), 60)
                sys.stdout.write(f"\rTempo restante: {minutes:02d}:{seconds:02d} ")
                sys.stdout.flush()
                time.sleep(1)
            print(f"\n{message}")
            return duration
        except KeyboardInterrupt:
            print("\nTimer interrompido.")
            return time.time() - start_time

    def play_sound(self, signal_type='fim'):
        try:
            if signal_type == 'inicio':
                winsound.Beep(1000, 500)
            elif signal_type == 'fim':
                winsound.Beep(500, 500)
                time.sleep(0.2)
                winsound.Beep(500, 500)
        except Exception as e:
            logger.error(f"Erro ao reproduzir som: {e}")

    def notify(self, title, message):
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

    def show_report(self):
        print("\nCiclos concluídos. Relatório:")
        for record in self.cycle_records:
            print(f"Ciclo {record['cycle_number']}: "
                  f"Trabalho {record['work_duration']/60:.1f}m, "
                  f"Pausa {record['break_duration']/60:.1f}m ({record['break_type']})")
