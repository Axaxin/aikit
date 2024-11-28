from flask import Blueprint, request, Response, jsonify
from models.settings import Settings
from utils.proxy import ProxyHandler

proxy_bp = Blueprint('proxy', __name__)

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

    # 检查是否是流式响应
    if response.headers.get('Content-Type') == 'text/event-stream':
        def generate():
            # 收集所有的响应块
            chunks = []
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        chunks.append(decoded_line)
            
            # 一次性发送所有块
            for chunk in chunks[:-1]:  # 除了最后一块
                yield f"{chunk}\n\n"
            
            # 最后一块单独处理，确保连接正确关闭
            if chunks:
                yield f"{chunks[-1]}\n\n"
        
        # 返回流式响应，保持原始响应头
        return Response(
            generate(),
            status=response.status_code,
            headers=dict(response.headers)
        )
    
    # 返回普通响应
    return Response(
        response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )
