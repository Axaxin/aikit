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
        print("\n=== 开始处理流式响应 ===")
        # 收集所有的响应内容
        full_response = []
        for line in response.iter_lines():
            if line:
                # 解码并打印每一行
                decoded_line = line.decode('utf-8')
                print(f"收到行: {decoded_line}")
                if decoded_line.startswith('data: '):
                    try:
                        # 提取JSON数据部分
                        data = decoded_line[6:]  # 跳过'data: '
                        if data != '[DONE]':
                            # 直接返回原始响应数据，不做处理
                            full_response.append(data)
                    except Exception as e:
                        print(f"处理行时出错: {e}")
                        print(f"问题行内容: {decoded_line}")
        
        print(f"\n=== 收集到的完整响应 ===\n{''.join(full_response)}")
        
        # 直接返回收集到的原始响应
        return Response(
            ''.join(full_response),
            status=200,
            headers={
                'Content-Type': 'application/json'
            }
        )
    
    # 返回普通响应
    return Response(
        response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )
