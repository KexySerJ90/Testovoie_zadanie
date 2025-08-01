import argparse
import json
from tabulate import tabulate
from datetime import datetime


def parse_args():
    """Парсит аргументы командной строки.

        - file (list): Список путей к файлам логов (обязательный)
        - report (str): Тип отчета (обязательный)
        - date (str): Дата для фильтрации (опциональный)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', nargs='*', required=True)
    parser.add_argument('--report', choices=['average', 'user-agent'], required=True)
    parser.add_argument('--date', help='format: YYYY-MM-DD')
    return parser.parse_args()


def read_log(file_paths:list, report_type:str, target_date=None)->dict:
    """Читает и анализирует логи из указанных файлов.
    """
    end_stats = {}
    for f in file_paths:
        try:
            with open(f, 'r') as file:
                for line in file:
                    try:
                        log = json.loads(line)
                        if target_date:
                            log_date = datetime.fromisoformat(log['@timestamp']).date()
                            if log_date != target_date:
                                continue
                        if report_type == 'average':
                            url = log.get('url')
                            response_time = log.get('response_time')
                            if url not in end_stats:
                                end_stats[url] = {'total': 0, 'time': 0}
                            end_stats[url]['total'] += 1
                            end_stats[url]['time'] += response_time
                        elif report_type == 'user-agent':
                            pass  # Реализация в разработке
                    except json.JSONDecodeError:
                        print(f"Ошибка парсинга JSON в строке файла {f}:{line}")
                        continue
        except FileNotFoundError:
            print(f"Файл не найден: {f}")
            continue
    return end_stats


def generate_data(end_stats:dict):
    """Генерирует данные для отчета из собранной статистики.
    """
    for i, (url, stats) in enumerate(
            sorted(end_stats.items(), key=lambda x: x[1]['total'], reverse=True)):
        avg_response_time = stats['time'] / stats['total']
        yield (i, url, stats['total'], f"{avg_response_time:.3f}")


def parse_date(date_str:str):
    """Парсит строку с датой в объект date.
    """
    if not date_str:
        return None
    try:
        print(f'Информация за {date_str}')
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print(f"Неверный формат даты: {date_str}. Используйте формат YYYY-MM-DD")


def print_report(data, report_type:str):
    """Выводит отчет в удобочитаемом формате.
    """
    if report_type == 'average':
        headers = ['', 'handler', 'total', 'avg_response_time']
        print(tabulate(data, headers))
    elif report_type == 'user-agent':
        print('Какая-то логика')


def main():
    args = parse_args()
    target_date = parse_date(args.date)
    if args.date and not target_date:
        return
    log = read_log(args.file, args.report, target_date)
    data=generate_data(log)
    print_report(data, args.report)


if __name__ == '__main__':
    main()
