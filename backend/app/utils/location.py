import requests
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_ip_location(ip, format='%C-%a-%c'):
    """
    通过ip-api.com公共API查询IP地址的地理位置
    :param ip: IP地址字符串
    :param format: 输出格式，默认"%C-%a-%c"，表示"国家-地区-城市"
    :return: 格式化的地理位置字符串，如"国家-地区-城市"，查询失败时返回"未知位置"
    """
    if not ip or ip == '127.0.0.1' or ip.startswith('192.168.') or ip.startswith('10.'):
        return "本地主机"
        
    try:
        # 设置超时时间，避免API响应缓慢导致程序阻塞
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                # 格式化返回结果：国家-地区-城市
                country = data.get('country', '未知国家')
                region = data.get('regionName', '未知地区')
                city = data.get('city', '未知城市')
                return format.replace('%C', country).replace('%a', region).replace('%c', city)
    except requests.RequestException:
        # 捕获所有网络相关异常
        pass
    except Exception:
        # 捕获其他可能的异常
        pass
        
    return "未知位置"