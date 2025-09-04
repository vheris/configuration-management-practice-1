import tkinter
import os
import platform
import sys

root = tkinter.Tk()

root.title('VFS')

root.geometry('800x500')

history = tkinter.Text(root)
history.config(state='disabled')
history.pack()

commands = tkinter.Entry(root, width=40)
commands.pack()
commands.bind("<Return>", lambda event: view())


def view():
    cmd = commands.get()
    history.config(state='normal')
    history.insert(tkinter.END, f"{platform.node()} ~ % {cmd}\n")
    parts = cmd.split()
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
    else:
        history.insert(tkinter.END, f"{platform.node()} ~ % unknown command\n")
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

root.mainloop()