#!/usr/bin/env python3
import os
import shutil
import re
import sys
import time
from pathlib import Path
from datetime import datetime
import argparse

def parse_filename(filename):
    """
    Парсит имя файла, извлекая ID, дату и время.
    Поддерживает различные форматы, где после даты и времени могут быть любые поля.
    """
    # Основной паттерн: ID_..._ДАТА_ВРЕМЯ_... .wav
    # ID должен быть 8 hex символов в начале
    # Дата: 8 цифр (ГГГММДД)
    # Время: 6 цифр (ЧЧММСС)
    pattern = re.compile(
        r'^([0-9A-Fa-f]{8})_'  # ID устройства (8 hex символов) в начале
        r'.*?_'                 # любые поля между ID и датой (нежадное совпадение)
        r'(\d{8})_'            # дата (ГГГММДД)
        r'(\d{6})'              # время (ЧЧММСС) - без подчеркивания после, т.к. дальше может быть что угодно
        r'.*\.wav$'             # остальные поля и расширение
    )
    
    match = pattern.match(filename)
    if match:
        device_id = match.group(1).upper()
        date = match.group(2)
        time = match.group(3)
        return device_id, date, time
    return None, None, None

def process_files(source_dir, destination_dir, mode='move', processed_dir=None):
    """
    Сканирует директорию, переименовывает файлы и обрабатывает их согласно режиму.
    
    Режимы:
    - 'move': переименовывает и перемещает в destination_dir для дальнейшей работы
    - 'archive': переименовывает, копирует в destination_dir, а оригинал перемещает в processed_dir
    """
    processed_count = 0
    error_count = 0
    skipped_count = 0
    
    print(f"\n📁 Исходная директория: {source_dir}")
    print(f"📁 Директория назначения: {destination_dir}")
    if mode == 'archive' and processed_dir:
        print(f"📁 Директория для обработанных файлов: {processed_dir}")
    print(f"🔄 Режим работы: {mode}")
    print("-" * 60)
    
    # Проходим по всем файлам в исходной директории
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        
        # Пропускаем директории
        if not os.path.isfile(file_path):
            continue
            
        # Проверяем, что файл имеет расширение .wav
        if not filename.lower().endswith('.wav'):
            print(f"⏭️  Пропущен (не WAV): {filename}")
            skipped_count += 1
            continue
        
        # Пытаемся разобрать имя файла
        device_id, date, time = parse_filename(filename)
        
        if not all([device_id, date, time]):
            print(f"⚠️  Ошибка формата (не удалось извлечь ID/дату/время): {filename}")
            error_count += 1
            continue
        
        # Создаем новое имя файла
        new_filename = f"EM_Dime_{date}_{time}_NML_{device_id}.wav"
        
        # Полный путь для нового файла в директории назначения
        dest_file_path = os.path.join(destination_dir, new_filename)
        
        # Проверяем, не существует ли уже файл с таким именем
        if os.path.exists(dest_file_path):
            base, ext = os.path.splitext(new_filename)
            counter = 1
            while os.path.exists(os.path.join(destination_dir, f"{base}_{counter}{ext}")):
                counter += 1
            dest_file_path = os.path.join(destination_dir, f"{base}_{counter}{ext}")
            print(f"⚠️  Внимание: файл {new_filename} уже существует. Использую {os.path.basename(dest_file_path)}")
        
        try:
            if mode == 'move':
                # Режим 1: Переименовываем и перемещаем в папку для дальнейшей работы
                shutil.move(file_path, dest_file_path)
                print(f"✅ {filename} -> {os.path.basename(dest_file_path)} (перемещен в рабочую папку)")
                
            elif mode == 'archive' and processed_dir:
                # Режим 2: Копируем переименованный в рабочую папку, оригинал в архив
                # Сначала копируем переименованный файл в рабочую папку
                shutil.copy2(file_path, dest_file_path)
                
                # Затем перемещаем оригинал в папку обработанных
                archive_path = os.path.join(processed_dir, filename)
                
                # Проверяем на дубликаты в архиве
                if os.path.exists(archive_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(os.path.join(processed_dir, f"{base}_{counter}{ext}")):
                        counter += 1
                    archive_path = os.path.join(processed_dir, f"{base}_{counter}{ext}")
                
                shutil.move(file_path, archive_path)
                print(f"✅ {filename} -> {os.path.basename(dest_file_path)} (скопирован в рабочую)")
                print(f"   Оригинал перемещен в архив: {os.path.basename(archive_path)}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при обработке {filename}: {e}")
            error_count += 1
    
    return processed_count, error_count, skipped_count

def continuous_scanning(source_dir, destination_dir, interval=10, mode='move', processed_dir=None):
    """
    Непрерывно сканирует директорию с заданным интервалом.
    """
    mode_desc = {
        'move': 'перемещение в рабочую папку',
        'archive': 'копирование в рабочую + архивация оригиналов'
    }
    
    print(f"🔄 Запущен режим непрерывного сканирования (интервал: {interval} сек)")
    print(f"📋 Режим обработки: {mode_desc.get(mode, mode)}")
    print(f"📅 Время старта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Множество для отслеживания уже обработанных файлов
    processed_files = set()
    total_processed = 0
    scan_count = 0
    
    try:
        while True:
            scan_count += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n🔄 Сканирование #{scan_count} | {current_time}")
            
            # Получаем список файлов до обработки
            all_files = set(os.listdir(source_dir))
            
            # Находим новые файлы (которые еще не обрабатывали)
            new_files = all_files - processed_files
            
            if new_files:
                print(f"📝 Найдено новых файлов: {len(new_files)}")
                
                # Обрабатываем новые файлы
                processed, errors, skipped = process_files(
                    source_dir, 
                    destination_dir, 
                    mode=mode, 
                    processed_dir=processed_dir
                )
                
                total_processed += processed
                
                # Обновляем множество обработанных файлов
                processed_files.update(os.listdir(source_dir))
                if processed_dir:
                    processed_files.update(os.listdir(processed_dir))
            else:
                print(f"📝 Новых файлов не найдено")
            
            print(f"📊 Всего обработано за сессию: {total_processed} файлов")
            print(f"⏳ Следующее сканирование через {interval} секунд...")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Получен сигнал прерывания (Ctrl+C)")
        print(f"📊 Итоговая статистика за сессию:")
        print(f"   ✅ Всего обработано файлов: {total_processed}")
        print(f"   🔄 Выполнено сканирований: {scan_count}")
        print(f"👋 Завершение работы...")

def print_usage():
    """Выводит информацию об использовании скрипта"""
    print("Использование: python3 script_parse_name.py <input_dir> <output_dir> [опции]")
    print("\nОбязательные аргументы:")
    print("   input_dir   - путь к директории с исходными файлами")
    print("   output_dir  - путь к рабочей директории для обработанных файлов")
    print("\nОпции:")
    print("   -i, --interval SEC    интервал сканирования в секундах (по умолчанию: 10)")
    print("   -m, --mode {move,archive}  режим работы:")
    print("        move    - переименовать и переместить в рабочую папку (по умолчанию)")
    print("        archive - скопировать в рабочую, оригиналы переместить в архив")
    print("   -a, --archive DIR     директория для архивации оригиналов (обязательно для mode=archive)")
    print("   -h, --help            показать эту справку")
    print("\nПримеры:")
    print("   python3 script_parse_name.py ./downloads ./processed")
    print("   python3 script_parse_name.py ./downloads ./processed -i 5")
    print("   python3 script_parse_name.py ./downloads ./processed -m archive -a ./archive")
    print("   python3 script_parse_name.py /home/user/input /home/user/working -i 30 -m archive -a /home/user/processed")

def main():
    parser = argparse.ArgumentParser(
        description='Скрипт для переименования и перемещения WAV файлов',
        usage='python3 script_parse_name.py <input_dir> <output_dir> [опции]',
        add_help=False
    )
    
    # Обязательные аргументы
    parser.add_argument('input_dir', nargs='?', help='Директория с исходными файлами')
    parser.add_argument('output_dir', nargs='?', help='Рабочая директория для обработанных файлов')
    
    # Опциональные аргументы
    parser.add_argument('-i', '--interval', type=int, default=10, 
                       help='Интервал сканирования в секундах (по умолчанию: 10)')
    parser.add_argument('-m', '--mode', choices=['move', 'archive'], default='move',
                       help='Режим работы: move (перемещение) или archive (копирование+архивация)')
    parser.add_argument('-a', '--archive', dest='archive_dir',
                       help='Директория для архивации оригиналов (обязательно для mode=archive)')
    parser.add_argument('-h', '--help', action='store_true', help='Показать эту справку')
    
    args = parser.parse_args()
    
    # Показываем справку
    if args.help or not args.input_dir or not args.output_dir:
        print_usage()
        sys.exit(0 if args.help else 1)
    
    source_directory = args.input_dir
    destination_directory = args.output_dir
    interval = args.interval
    mode = args.mode
    
    # Проверяем режим archive
    if mode == 'archive' and not args.archive_dir:
        print("❌ Ошибка: Для режима 'archive' необходимо указать директорию для архивации (-a или --archive)")
        print_usage()
        sys.exit(1)
    
    # Проверяем существование исходной директории
    if not os.path.isdir(source_directory):
        print(f"❌ Ошибка: Исходная директория '{source_directory}' не существует!")
        sys.exit(1)
    
    # Создаем директорию назначения, если она не существует
    Path(destination_directory).mkdir(parents=True, exist_ok=True)
    
    # Создаем архивную директорию, если нужно
    archive_dir = None
    if mode == 'archive':
        archive_dir = args.archive_dir
        Path(archive_dir).mkdir(parents=True, exist_ok=True)
    
    # Проверяем интервал
    if interval < 1:
        print("⚠️  Интервал должен быть положительным числом. Использую значение по умолчанию 10 сек.")
        interval = 10
    
    # Запускаем непрерывное сканирование
    continuous_scanning(source_directory, destination_directory, interval, mode, archive_dir)

if __name__ == "__main__":
    main()