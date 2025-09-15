import tkinter
import os
import platform
import sys

"""Нужно сделать обработку ошибок во время выполнения скрипта."""

vfs_path = None
script_path = None

if len(sys.argv) > 1:
    vfs_path = sys.argv[1]
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

def script(script_path):
    try:
        with open(script_path, 'r') as file:
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
    varname = cmd[1:]
    if varname in os.environ:
        cmd = os.path.expandvars(cmd)
        history.insert(tkinter.END, f"{platform.node()} ~ % {cmd}\n")
    else:
        history.insert(tkinter.END, f"{platform.node()} ~ % unknown command\n")


def vfs_commands(parts, cmd):
    if not parts:
        history.insert(tkinter.END, f"{platform.node()} ~ % empty command\n")
    elif parts[0] == 'ls':
        history.insert(tkinter.END, f"ls: {parts[1:]}\n")
    elif parts[0] == 'cd':
        history.insert(tkinter.END, f"cd: {parts[1:]}\n")
    elif cmd.startswith("$"):
        parser()
    elif parts[0] == 'exit':
        sys.exit()
    elif parts[0] == 'error':
        raise Exception("Тестовая ошибка выполнения скрипта")
    else:
        history.insert(tkinter.END, f"{platform.node()} ~ % unknown command\n")

def run_script_if_needed():
    if script_path:
        root.after(100, lambda: script(script_path))


run_script_if_needed()

root.mainloop()
