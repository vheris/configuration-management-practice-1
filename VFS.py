import json
import base64
import os

class VFS:
    def __init__(self, json_path):
        self.json_path = json_path
        self.fs = {}
        self.current_dir = "/"
        self.load_error = None
        self.load_vfs()
        
    def load_vfs(self):
        """Загрузка файловой системы"""
        try:
            if not os.path.exists(self.json_path):
                self.load_error = f"Файл VFS не найден: {self.json_path}"
                return
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.fs = json.load(f)
            if not self.validate_vfs_structure():
                self.load_error = f"Неверный формат: {self.json_path}"
                self.fs = {"/" : {"type": "directory", "content": {}}}
        except json.JSONDecodeError as e:
            self.load_error = f"Ошибка декодирования JSON: {str(e)}"
            self.fs = {"/": {"type": "directory", "content": {}}}
        except Exception as e:
            self.load_error = f"Ошибка загрузки VFS: {str(e)}"
            self.fs = {"/": {"type": "directory", "content": {}}}
    
    def validate_vfs_structure(self):
        """Проверка корректности структуры"""
        if not isinstance(self.fs, dict):
            return False
        if '/' not in self.fs:
            return False
        if not isinstance(self.fs["/"], dict):
            return False
        if "type" not in self.fs["/"] or self.fs["/"]["type"] != "directory":
            return False
        return True
    
    def get_node(self, path):
        """Поиск папки/файла"""
        if path == "/":
            return self.fs.get("/")
        
        parts = [p for p in path.split('/') if p]
        current = self.fs.get("/")
        
        for part in parts:
            if (current and current.get("type") == "directory" and "content" in current and part in current["content"]):
                 current = current["content"][part]
            else:
                return None
        return current
    
def init_vfs(json_path):
    """Инициализация VFS и возврат объекта"""
    return VFS(json_path)

def get_vfs_status(vfs):
    """Получение статуса VFS"""
    if vfs:
        if vfs.load_error:
            return f"ОШИБКА VFS: {vfs.load_error}"
        return f"VFS загружена: {vfs.json_path}"
    return "VFS: не используется"