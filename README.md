Базовые команды

python log_analyzer.py --file access.log --report average
Полный синтаксис

python log_analyzer.py \
  --file <путь_к_файлу1> [<путь_к_файлу2>...] \
  --report <average|user-agent> \
  [--date ГГГГ-ММ-ДД]
Параметры
Параметр	Обязательный	Описание	Пример
--file	Да	Путь к файлу(ам) логов	access.log
--report	Да	Тип отчета	average
--date	Нет	Фильтрация по дате (ГГГГ-ММ-ДД)	2023-01-15
