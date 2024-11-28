from flask import Flask
from routes.admin import admin_bp
from routes.proxy import proxy_bp
import os
import argparse

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于session加密

# 注册蓝图
app.register_blueprint(admin_bp)
app.register_blueprint(proxy_bp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='API Proxy Server')
    parser.add_argument('--port', type=int, default=5012,
                      help='Port to run the server on (default: 5012)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                      help='Host to run the server on (default: 127.0.0.1)')
    args = parser.parse_args()
    
    app.run(host=args.host, port=args.port)
