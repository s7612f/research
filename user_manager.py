import json
import os
import hashlib

with open('config.json') as _f:
    _CFG = json.load(_f)
_DB_DIR = _CFG.get('database_dir', '/root/databases')
os.makedirs(_DB_DIR, exist_ok=True)

class UserManager:
    """Simple file-based user store with per-user databases."""
    def __init__(self, path='users.json'):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)
        with open(self.path) as f:
            self.users = json.load(f)

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.users, f)

    def register(self, username: str, password: str, email: str=None) -> bool:
        if username in self.users:
            return False
        hashed = hashlib.sha256(password.encode()).hexdigest()
        db_path = os.path.join(_DB_DIR, f"{username}.db")
        self.users[username] = {
            'password': hashed,
            'db_path': db_path,
            'email': email
        }
        self._save()
        return True

    def authenticate(self, username: str, password: str) -> bool:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return username in self.users and self.users[username]['password'] == hashed

    def db_path(self, username: str) -> str:
        return self.users.get(username, {}).get('db_path')

    def email(self, username: str) -> str:
        return self.users.get(username, {}).get('email')

user_manager = UserManager()
