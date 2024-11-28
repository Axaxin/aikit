from flask import Blueprint, request, Response
from models.settings import Settings
from utils.proxy import ProxyHandler
import socket
import select

proxy_bp = Blueprint('proxy', __name__)

@proxy_bp.route('/<path:path>', methods=['CONNECT'])
def handle_connect(path):
    try:
        # 解析目标地址和端口
        host, port = path.split(':')
        port = int(port)
        
        # 创建到目标服务器的连接
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(10)  # 设置超时
        server_socket.connect((host, port))
        
        # 发送连接成功响应
        success_response = 'HTTP/1.1 200 Connection Established\r\n\r\n'
        request.environ['werkzeug.socket'].send(success_response.encode())
        
        # 获取客户端socket
        client_socket = request.environ['werkzeug.socket']
        
        # 在客户端和服务器之间转发数据
        sockets = [client_socket, server_socket]
        timeout = 1
        
        while True:
            # 使用select监听两个socket
            readable, _, exceptional = select.select(sockets, [], sockets, timeout)
            
            if exceptional:
                break
                
            for sock in readable:
                try:
                    data = sock.recv(4096)
                    if not data:
                        return Response('Connection closed', status=200)
                        
                    # 确定目标socket
                    target = server_socket if sock == client_socket else client_socket
                    target.send(data)
                except (socket.error, ConnectionError):
                    return Response('Connection error', status=500)
                    
    except Exception as e:
        print(f"CONNECT Error: {str(e)}")
        return Response(f'Connection failed: {str(e)}', status=500)
    
    return Response('Connection closed', status=200)

@proxy_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # 检查是否是管理面板路径
    if path.startswith(('login', 'settings', 'logout')):
        return None  # 让Flask继续处理这些路由
    
    # 获取Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response('Authorization required', status=401)
    
    # 验证Bearer token格式
    if not auth_header.startswith('Bearer '):
        return Response('Invalid authorization format', status=401)
    
    # 提取token
    auth_token = auth_header[7:]  # 跳过"Bearer "前缀
    
    # 查找后端配置
    backend_config = Settings.find_backend_by_auth(auth_token)
    if not backend_config:
        return Response('Invalid authorization', status=401)
    
    # 构建并发送代理请求
    proxy_request = ProxyHandler.build_proxy_request(request, backend_config)
    response = ProxyHandler.send_proxy_request(proxy_request)
    
    if response is None:
        return Response('Backend server error', status=500)
    
    # 返回响应
    return Response(
        response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )
