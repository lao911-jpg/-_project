import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Scheduler:
    @staticmethod
    def find_best_engineer(ticket, available_engineers_with_times, current_time):
        """
        Находит лучшего инженера для заявки.
        
        available_engineers_with_times: список словарей
        [
            {
                'engineer': Engineer объект,
                'free_from': datetime или None (если свободен сейчас),
                'solve_time': int (минуты)
            },
            ...
        ]
        """
        best_result = None
        best_finish = None
        
        for item in available_engineers_with_times:
            engineer = item['engineer']
            free_from = item.get('free_from')
            solve_time = item['solve_time']
            
            # Если инженер свободен сейчас
            if free_from is None or free_from < current_time:
                start_time = current_time
            else:
                start_time = free_from
            
            # Проверяем рабочие часы (упрощённо для первого запуска)
            work_start = engineer.work_start
            work_end = engineer.work_end
            
            # Переносим на следующий день, если start_time после конца рабочего дня
            if start_time.time() >= work_end:
                next_day = start_time.date() + timedelta(days=1)
                start_time = datetime.combine(next_day, work_start)
            
            finish_time = start_time + timedelta(minutes=solve_time)
            
            # Если finish_time выходит за конец рабочего дня
            if finish_time.time() > work_end:
                next_day = finish_time.date() + timedelta(days=1)
                remaining_minutes = (finish_time - datetime.combine(finish_time.date(), work_end)).seconds // 60
                start_time = datetime.combine(next_day, work_start)
                finish_time = start_time + timedelta(minutes=remaining_minutes)
            
            if best_finish is None or finish_time < best_finish:
                best_finish = finish_time
                best_result = {
                    'engineer': engineer,
                    'start_time': start_time,
                    'finish_time': finish_time
                }
                logger.info(f"Найден кандидат: {engineer.name} -> старт {start_time}, финиш {finish_time}")
        
        if best_result:
            logger.info(f"ВЫБРАН инженер: {best_result['engineer'].name}")
        else:
            logger.warning(f"Не найден инженер для заявки #{ticket.id}")
        
        return best_result