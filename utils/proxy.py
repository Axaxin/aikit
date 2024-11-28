import requests
from urllib.parse import urljoin

class ProxyHandler:
    @staticmethod
    def build_proxy_request(original_request, backend_config):
        """构建代理请求"""
        # 构建目标URL
        base_url = backend_config['host']
        if backend_config.get('port'):
            base_url = f"{base_url}:{backend_config['port']}"
        target_url = urljoin(base_url, original_request.path)

        # 复制原始请求头
        headers = dict(original_request.headers)
        
        # 处理Authorization头
        if backend_config.get('api_key') and backend_config['api_key'] != 'null':
            headers['Authorization'] = f"Bearer {backend_config['api_key']}"
        elif 'Authorization' in headers:
            del headers['Authorization']

        return {
            'url': target_url,
            'method': original_request.method,
            'headers': headers,
            'data': original_request.get_data(),
            'params': original_request.args
        }

    @staticmethod
    def send_proxy_request(proxy_request):
        """发送代理请求"""
        try:
            response = requests.request(
                method=proxy_request['method'],
                url=proxy_request['url'],
                headers=proxy_request['headers'],
                data=proxy_request['data'],
                params=proxy_request['params']
            )
            return response
        except requests.exceptions.RequestException as e:
            return None
