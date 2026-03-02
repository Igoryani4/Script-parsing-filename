# Script-parsing-filename
1. Два режима работы:
Режим "move" (по умолчанию)
bash
python3 script_parse_name.py ./downloads ./processed -m move
Переименовывает файл

Перемещает в рабочую папку (output_dir)

Оригинал удаляется из исходной папки

Режим "archive"
bash
python3 script_parse_name.py ./downloads ./processed -m archive -a ./archive
Копирует переименованный файл в рабочую папку (output_dir)

Перемещает оригинал в архивную папку (archive_dir)

Исходная папка очищается, но оригиналы сохраняются в архиве

2. Улучшенный интерфейс командной строки
Теперь используем argparse для более гибкой работы:

bash
# Минимальное использование (режим move)
python3 script_parse_name.py ./downloads ./processed

# С кастомным интервалом
python3 script_parse_name.py ./downloads ./processed -i 5

# Режим archive с указанием архивной папки
python3 script_parse_name.py ./downloads ./processed -m archive -a ./archive

# Полная конфигурация
python3 script_parse_name.py ./input ./working -i 30 -m archive -a ./archive
3. Справка по использованию
bash
python3 script_parse_name.py -h
# или
python3 script_parse_name.py --help
Примеры использования:
Режим перемещения (для дальнейшей работы):
bash
python3 script_parse_name.py /data/incoming /data/processing -i 10 -m move
Файлы из /data/incoming переименовываются и перемещаются в /data/processing

В /data/incoming файлов больше нет

Режим архивации (с сохранением оригиналов):
bash
python3 script_parse_name.py /data/incoming /data/processing -m archive -a /data/archive -i 5
Переименованные копии в /data/processing

Оригиналы перемещаются в /data/archive

/data/incoming очищается

Все оригиналы сохранены в архиве

Преимущества:
Гибкость: выбор режима под конкретную задачу

Безопасность: режим archive сохраняет оригиналы

Автоматизация: непрерывное сканирование с настраиваемым интервалом

Информативность: подробный лог всех операций