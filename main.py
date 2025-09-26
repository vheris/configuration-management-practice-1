import tkinter
import os
import platform
import sys

try:
    from VFS import init_vfs, get_vfs_status
    VFS_AVAILABLE = True
except ImportError:
    VFS_AVAILABLE = False
    print("VFS модуль не доступен")

script_path = None
current_path = "/"

if len(sys.argv) > 1:
    arg1 = sys.argv[1]
    if VFS_AVAILABLE and arg1.endswith('.json'):
        vfs = init_vfs(arg1)
        status = get_vfs_status(vfs)
        print(status)
        if hasattr(vfs, 'fs'):
            vfs_data = vfs.fs
            print("VFS данные загружены из vfs.fs")
            
        if vfs.load_error:
            print("Ошибка VFS! Программа завершена.")
            sys.exit(1)
    else:
        script_path = arg1
        
if len(sys.argv) > 2:
    script_path = sys.argv[2]

root = tkinter.Tk()

root.title('VFS')

root.geometry('800x400')

history = tkinter.Text(root)
history.config(state='disabled')
history.pack()

commands = tkinter.Entry(root, width=40)
commands.pack()
commands.bind("<Return>", lambda event: view())

def get_current_directory(vfs_data, path):
    """Получить текущую директорию по пути"""
    if path == "/":
        return vfs_data["/"]
    
    parts = path.strip("/").split("/")
    current = vfs_data["/"]
    
    for part in parts:
        if part and part in current.get("content", {}):
            current = current["content"][part]
        else:
            return None
    
    return current

def get_file_content(vfs_data, file_path):
    """Получить содержимое файла по пути"""
    if file_path == "/":
        return None
    
    parts = file_path.strip("/").split("/")
    current = vfs_data["/"]
    
    for part in parts[:-1]:
        if part and part in current.get("content", {}):
            current = current["content"][part]
        else:
            return None
    
    filename = parts[-1]
    if filename in current.get("content", {}):
        file_data = current["content"][filename]
        if file_data.get("type") == "file":
            return file_data.get("content", "")
    
    return None

def ls_command(vfs_data, path, args):
    """Реализация команды ls"""
    target_path = path
    
    # Обработка аргументов
    if args:
        if args[0].startswith("-"):
            # Пропускаем флаги (упрощенная реализация)
            path_args = args[1:]
        else:
            path_args = args
    else:
        path_args = []
    
    # Определяем целевой путь
    if path_args:
        target_path = path_args[0]
        if not target_path.startswith("/"):
            # Относительный путь
            if path == "/":
                target_path = "/" + target_path
            else:
                target_path = path + "/" + target_path
    
    # Нормализуем путь
    target_path = os.path.normpath(target_path).replace("\\", "/")
    if not target_path.startswith("/"):
        target_path = "/" + target_path
    
    # Получаем целевую директорию
    target_dir = get_current_directory(vfs_data, target_path)
    
    if not target_dir:
        return f"ls: cannot access '{target_path}': No such file or directory\n"
    
    if target_dir.get("type") != "directory":
        return f"ls: cannot access '{target_path}': Not a directory\n"
    
    # Получаем содержимое директории
    content = target_dir.get("content", {})
    if not content:
        return ""  # Пустая директория
    
    # Формируем список файлов и папок
    items = []
    for name, item_data in content.items():
        if item_data.get("type") == "directory":
            items.append(f"{name}/")
        else:
            items.append(name)
    
    # Сортируем: сначала директории, потом файлы
    dirs = [item for item in items if item.endswith("/")]
    files = [item for item in items if not item.endswith("/")]
    
    sorted_items = sorted(dirs) + sorted(files)
    return "  ".join(sorted_items) + "\n"

def cd_command(vfs_data, current_path, args):
    """Реализация команды cd"""
    if not args:
        # cd без аргументов - переход в корень
        return "/"
    
    target_path = args[0]
    
    # Определяем новый путь
    if target_path == "/":
        new_path = "/"
    elif target_path.startswith("/"):
        # Абсолютный путь
        new_path = target_path
    else:
        # Относительный путь
        if current_path == "/":
            new_path = "/" + target_path
        else:
            new_path = current_path + "/" + target_path
    
    # Нормализуем путь
    new_path = os.path.normpath(new_path).replace("\\", "/")
    if not new_path.startswith("/"):
        new_path = "/" + new_path
    
    # Проверяем существование пути
    target_dir = get_current_directory(vfs_data, new_path)
    
    if not target_dir:
        return current_path, f"cd: no such file or directory: {target_path}\n"
    
    if target_dir.get("type") != "directory":
        return current_path, f"cd: not a directory: {target_path}\n"
    
    return new_path, ""

def tac_command(vfs_data, current_path, args):
    """Реализация команды tac (обратный cat)"""
    if not args:
        return "tac: missing file operand\n"
    
    file_path = args[0]
    if not file_path.startswith("/"):
        # Относительный путь
        if current_path == "/":
            file_path = "/" + file_path
        else:
            file_path = current_path + "/" + file_path
    
    # Нормализуем путь
    file_path = os.path.normpath(file_path).replace("\\", "/")
    if not file_path.startswith("/"):
        file_path = "/" + file_path
    
    # Получаем содержимое файла
    content = get_file_content(vfs_data, file_path)
    
    if content is None:
        return f"tac: cannot access '{file_path}': No such file\n"
    
    # Разделяем содержимое на строки и переворачиваем их порядок
    lines = content.split('\n')
    reversed_lines = lines[::-1]
    
    return '\n'.join(reversed_lines) + '\n'

def uname_command(args):
    """Реализация команды uname"""
    if not args:
        # По умолчанию выводим только имя системы
        return platform.system() + "\n"
    
    if args[0] == "-a":
        # Выводим всю информацию
        return f"{platform.system()} {platform.node()} {platform.release()} {platform.version()} {platform.machine()}\n"
    elif args[0] == "-s":
        # Только имя ядра/ОС
        return platform.system() + "\n"
    elif args[0] == "-n":
        # Имя сетевого узла
        return platform.node() + "\n"
    elif args[0] == "-r":
        # Релиз ядра
        return platform.release() + "\n"
    elif args[0] == "-v":
        # Версия ядра
        return platform.version() + "\n"
    elif args[0] == "-m":
        # Архитектура машины
        return platform.machine() + "\n"
    else:
        return f"uname: invalid option -- '{args[0][1:]}'\n"

def wc_command(vfs_data, current_path, args):
    """Реализация команды wc (word count)"""
    if not args:
        return "wc: missing file operand\n"
    
    file_path = args[0]
    if not file_path.startswith("/"):
        # Относительный путь
        if current_path == "/":
            file_path = "/" + file_path
        else:
            file_path = current_path + "/" + file_path
    
    # Нормализуем путь
    file_path = os.path.normpath(file_path).replace("\\", "/")
    if not file_path.startswith("/"):
        file_path = "/" + file_path
    
    # Получаем содержимое файла
    content = get_file_content(vfs_data, file_path)
    
    if content is None:
        return f"wc: cannot access '{file_path}': No such file\n"
    
    # Подсчитываем статистику
    lines = content.split('\n')
    # Убираем последнюю пустую строку, если файл заканчивается на \n
    if lines and lines[-1] == '':
        lines = lines[:-1]
    
    line_count = len(lines)
    word_count = 0
    char_count = len(content)
    
    for line in lines:
        words = line.split()
        word_count += len(words)
    
    return f"  {line_count}  {word_count}  {char_count} {file_path}\n"


def script(script_path):
    try:
        with open(script_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        history.config(state='normal')
        history.insert(tkinter.END, f"\n=== ВЫПОЛНЕНИЕ СКРИПТА: {script_path} ===\n")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            history.insert(tkinter.END, f"{platform.node()} ~ % {line}\n")
            vfs_commands(line.split(), line)
            
        history.insert(tkinter.END, f"=== ВЫПОЛНЕНИЕ СКРИПТА ЗАВЕРШЕНО ===\n\n")
        history.config(state='disabled')
        
    except FileNotFoundError:
        history.config(state='normal')
        history.insert(tkinter.END, f"ОШИБКА: Скрипт не найден: {script_path}\n")
        history.config(state='disabled')
    except Exception as e:
        history.config(state='normal')
        history.insert(tkinter.END, f"ОШИБКА при выполнении скрипта: {str(e)}\n")
        history.config(state='disabled')

def view():
    cmd = commands.get()
    history.config(state='normal')
    history.insert(tkinter.END, f"{platform.node()} ~ % {cmd}\n")
    cmd = os.path.expandvars(cmd)
    vfs_commands(cmd.split(), cmd)
    commands.delete(0, tkinter.END)
    history.config(state='disabled')

def parser():
    cmd = commands.get()
    expanded = os.path.expandvars(cmd)
    if expanded != cmd:
        history.insert(tkinter.END, f"{platform.node()} ~ % {expanded}\n")
    else:
        history.insert(tkinter.END, f"{platform.node()} ~ % unknown command\n")


def vfs_commands(parts, cmd):
    global current_path
    
    if not parts:
        history.insert(tkinter.END, f"{platform.node()} ~ % empty command\n")
        return
    
    command = parts[0]
    
    if command == 'ls':
        if VFS_AVAILABLE:
            result = ls_command(vfs_data, current_path, parts[1:])
            history.insert(tkinter.END, result)
        else:
            history.insert(tkinter.END, f"ls: VFS not available\n")
    
    elif command == 'cd':
        if VFS_AVAILABLE:
            new_path, error = cd_command(vfs_data, current_path, parts[1:])
            if error:
                history.insert(tkinter.END, error)
            else:
                current_path = new_path
        else:
            history.insert(tkinter.END, f"cd: VFS not available\n")
            
    elif command == 'tac':
        if VFS_AVAILABLE:
            result = tac_command(vfs_data, current_path, parts[1:])
            history.insert(tkinter.END, result)
        else:
            history.insert(tkinter.END, f"tac: VFS not available\n")
    
    elif command == 'uname':
        result = uname_command(parts[1:])
        history.insert(tkinter.END, result)
    
    elif command == 'wc':
        if VFS_AVAILABLE:
            result = wc_command(vfs_data, current_path, parts[1:])
            history.insert(tkinter.END, result)
        else:
            history.insert(tkinter.END, f"wc: VFS not available\n")
    
    elif cmd.startswith("$") or cmd.startswith("%"):
        parser()
    
    elif command == 'exit':
        sys.exit(1)
    
    elif command == 'error':
        raise Exception("Тестовая ошибка выполнения скрипта")
    
    else:
        history.insert(tkinter.END, f"{platform.node()} ~ % unknown command\n")


def run_script_if_needed():
    if script_path:
        root.after(100, lambda: script(script_path))


run_script_if_needed()

root.mainloop()