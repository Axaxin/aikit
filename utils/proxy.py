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
            
        # 需要移除的头部（包含客户端信息的）
        headers_to_remove = [
            'Host',
            'Cf-Connecting-Ip',
            'Cf-Ipcountry',
            'Cf-Ray',
            'Cf-Visitor',
            'Cf-Warp-Tag-Id',
            # 'X-Forwarded-For',
            # 'X-Stainless-Arch',
            # 'X-Stainless-Async',
            # 'X-Stainless-Lang',
            # 'X-Stainless-Os',
            # 'X-Stainless-Package-Version',
            # 'X-Stainless-Runtime',
            # 'X-Stainless-Runtime-Version',
            'Cdn-Loop'
        ]
        
        # 移除不需要的头部
        for header in headers_to_remove:
            headers.pop(header, None)
            
        #  更新的头部
        headers.update({
            # 'User-Agent': 'Python-Requests/2.31.0',  # 使用通用的User-Agent
            #'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            #'Content-Type': 'application/json'
        })
        
        # 查看apikey
        apikey = backend_config.get('api_key')

        # 处理Authorization头
        if apikey == 'None' or apikey is None or apikey == '':
            del headers['Authorization']
        elif len(apikey) > 4:
            if 'mistral' in backend_config['backend_name']:
                headers['ApiKey'] = f"Bearer {backend_config['api_key']}"
            else:
                headers['Authorization'] = f"Bearer {backend_config['api_key']}"


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
                params=proxy_request['params'],
                stream=True  # 启用流式传输
            )
            return response
        except requests.exceptions.RequestException as e:
            print(f"Proxy request error: {e}")
            return None
