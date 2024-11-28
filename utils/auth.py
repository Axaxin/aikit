from models.settings import Settings
import hashlib

class Auth:
    @staticmethod
    def hash_password(password):
        """对密码进行哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_admin_login(password):
        """验证管理面板登录"""
        config = Settings.load_settings()
        stored_password = config.get('admin_password')
        if not stored_password:
            # 如果没有存储的密码，使用默认密码
            stored_password = Auth.hash_password('password')
            config['admin_password'] = stored_password
            Settings.save_settings(config)
        return stored_password == Auth.hash_password(password)

    @staticmethod
    def change_password(old_password, new_password):
        """修改管理密码"""
        if not Auth.verify_admin_login(old_password):
            return False
        
        config = Settings.load_settings()
        config['admin_password'] = Auth.hash_password(new_password)
        return Settings.save_settings(config)
