from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from models.settings import Settings
from utils.auth import Auth

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if Auth.verify_admin_login(password):
            session['logged_in'] = True
            return redirect(url_for('admin.settings'))
        flash('Invalid password', 'error')
    return render_template('login.html')

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        config = Settings.load_settings()
        
        if action == 'reset_password':
            # 只重置密码
            config['admin_password'] = Auth.hash_password('password')
            Settings.save_settings(config)
            flash('Admin password has been reset to "password"', 'success')
            return redirect(url_for('admin.logout'))
            
        elif action == 'add_backend':
            port = request.form.get('port')
            auth_code = request.form.get('auth_code')
            api_key = request.form.get('api_key')
            
            # 检查验证码是否已存在
            if any(backend['auth_code'] == auth_code for backend in config.get('backends', [])):
                flash('Auth code already exists. Please use a unique auth code.', 'error')
                return redirect(url_for('admin.settings'))
                
            new_backend = {
                'name': request.form.get('name'),
                'host': request.form.get('host'),
                'port': int(port) if port else None,
                'auth_code': auth_code,
                'api_key': api_key if api_key else None
            }
            
            if 'backends' not in config:
                config['backends'] = []
            config['backends'].append(new_backend)
            Settings.save_settings(config)
            flash('Backend added successfully', 'success')
            
        elif action == 'edit_backend':
            old_auth_code = request.form.get('old_auth_code')
            new_auth_code = request.form.get('auth_code')
            port = request.form.get('port')
            api_key = request.form.get('api_key')
            
            # 如果修改了验证码，检查新验证码是否已存在
            if old_auth_code != new_auth_code and any(backend['auth_code'] == new_auth_code for backend in config.get('backends', [])):
                flash('Auth code already exists. Please use a unique auth code.', 'error')
                return redirect(url_for('admin.settings'))
            
            # 更新后端配置
            for backend in config.get('backends', []):
                if backend['auth_code'] == old_auth_code:
                    backend.update({
                        'name': request.form.get('name'),
                        'host': request.form.get('host'),
                        'port': int(port) if port else None,
                        'auth_code': new_auth_code,
                        'api_key': api_key if api_key else None
                    })
                    break
            
            Settings.save_settings(config)
            flash('Backend updated successfully', 'success')
            
        elif action == 'delete_backend':
            auth_code = request.form.get('auth_code')
            original_length = len(config.get('backends', []))
            config['backends'] = [b for b in config.get('backends', []) if b['auth_code'] != auth_code]
            
            if len(config.get('backends', [])) < original_length:
                Settings.save_settings(config)
                flash('Backend deleted successfully', 'success')
            else:
                flash('Backend not found', 'error')
            
        elif action == 'change_password':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
            elif Auth.change_password(old_password, new_password):
                flash('Password changed successfully', 'success')
            else:
                flash('Invalid old password', 'error')
                
        return redirect(url_for('admin.settings'))
        
    config = Settings.load_settings()
    return render_template('settings.html', 
                         backends=config.get('backends', []))

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin.login'))
