import json
import os

class Settings:
    CONFIG_FILE = 'config.json'

    @staticmethod
    def load_settings():
        """加载配置文件"""
        if os.path.exists(Settings.CONFIG_FILE):
            with open(Settings.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {
            "admin_password": "admin",
            "backends": []
        }

    @staticmethod
    def save_settings(config_data):
        """保存配置"""
        with open(Settings.CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True

    @staticmethod
    def find_backend_by_auth(auth_code):
        """根据验证码查找后端配置"""
        config = Settings.load_settings()
        for backend in config.get('backends', []):
            if backend.get('auth_code') == auth_code:
                return backend
        return None
