import pytest
from datetime import date, datetime
from main import parse_args, read_log_and_generate_data, parse_date, print_report

# Тестовые данные
TEST_LOGS = [
    '{"@timestamp": "2023-01-01T12:00:00", "url": "/test", "response_time": 0.1}\n',
    '{"@timestamp": "2023-01-01T12:01:00", "url": "/test", "response_time": 0.2}\n',
    '{"@timestamp": "2023-01-02T12:00:00", "url": "/api", "response_time": 0.3}\n',
    'invalid json line\n'
]


@pytest.fixture
def temp_log_file(tmp_path):
    """Фикстура создает временный лог-файл для тестирования.
    """
    file = tmp_path / "test.log"
    file.write_text(''.join(TEST_LOGS))
    return str(file)


def test_parse_args():
    """Тестирует корректность парсинга аргументов командной строки.

    Проверяет:
    - Корректное разбиение файлов в --file
    - Правильное определение типа отчета (--report)
    - Корректный парсинг даты (--date)
    """
    sys_argv = ['--file', 'file1.log', 'file2.log', '--report', 'average', '--date', '2025-06-24']
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr('sys.argv', ['script.py'] + sys_argv)
        args = parse_args()
        assert args.file == ['file1.log', 'file2.log']
        assert args.report == 'average'
        assert args.date == '2025-06-24'


def test_parse_date_valid():
    """Тестирует корректный парсинг валидной даты.

    Проверяет, что функция parse_date правильно преобразует:
    - Строку формата YYYY-MM-DD в объект date
    """
    assert parse_date("2025-06-24") == date(2025, 6, 24)


def test_parse_date_invalid(capsys):
    """Тестирует обработку невалидного формата даты.

    Проверяет:
    - Возврат None при невалидной дате
    - Вывод сообщения об ошибке в stderr
    """
    assert parse_date("invalid-date") is None
    captured = capsys.readouterr()
    assert "Неверный формат даты" in captured.out


def test_parse_date_none():
    """Тестирует обработку отсутствия даты (None).

    Проверяет, что функция возвращает None при отсутствии входных данных.
    """
    assert parse_date(None) is None


def test_read_log_and_generate_data_average(temp_log_file):
    """Тестирует генерацию отчета 'average' без фильтрации по дате.

    Проверяет:
    - Количество обработанных URL
    - Правильность сортировки по количеству запросов
    - Корректность расчета среднего времени ответа
    """
    result = list(read_log_and_generate_data([temp_log_file], 'average'))
    assert len(result) == 2  # Должно быть 2 URL (/test и /api)
    assert result[0][1] == '/test'  # Первый должен быть /test (больше запросов)
    assert result[0][2] == 2  # 2 запроса для /test
    assert result[1][1] == '/api'  # Второй /api
    assert result[1][2] == 1  # 1 запрос для /api
    assert float(result[0][3]) == pytest.approx(0.15)
    assert float(result[1][3]) == pytest.approx(0.3)


def test_read_log_and_generate_data_average_with_date(temp_log_file):
    """Тестирует генерацию отчета 'average' с фильтрацией по дате.

    Проверяет:
    - Корректность фильтрации записей по дате
    - Правильность результатов после фильтрации
    """
    target_date = datetime.strptime('2023-01-01', '%Y-%m-%d').date()
    result = list(read_log_and_generate_data([temp_log_file], 'average', target_date))
    assert len(result) == 1
    assert result[0][1] == '/test'
    assert result[0][2] == 2

    target_date = datetime.strptime('2023-01-02', '%Y-%m-%d').date()
    result = list(read_log_and_generate_data([temp_log_file], 'average', target_date))
    assert len(result) == 1
    assert result[0][1] == '/api'
    assert result[0][2] == 1


def test_read_log_and_generate_data_file_not_found():
    """Тестирует обработку отсутствия файла.

    Проверяет, что функция корректно обрабатывает ситуацию, когда:
    - Указанный файл не существует
    - Возвращает пустой результат
    """
    result = list(read_log_and_generate_data(['nonexistent.log'], 'average'))
    assert len(result) == 0


def test_print_report_average(capsys, temp_log_file):
    """Тестирует вывод отчета типа 'average'.

    Проверяет:
    - Наличие обязательных заголовков в выводе
    - Присутствие ожидаемых данных в выводе
    - Общую структуру вывода
    """
    data = read_log_and_generate_data([temp_log_file], 'average')
    print_report(data, 'average')
    captured = capsys.readouterr()
    assert 'handler' in captured.out
    assert 'avg_response_time' in captured.out
    assert '/test' in captured.out


