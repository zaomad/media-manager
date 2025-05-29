import os
import json

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# 确保配置目录存在
os.makedirs(CONFIG_DIR, exist_ok=True)

# 默认配置
DEFAULT_CONFIG = {
    "webdav": {
        "enabled": False,
        "url": "",
        "username": "",
        "password": "",
        "remote_path": "/media-manager/",
        "sync_interval": 3600,  # 同步间隔，默认1小时
        "last_sync": None
    }
}

def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
            # 确保所有默认配置项都存在
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if sub_key not in config[key]:
                            config[key][sub_key] = sub_value
            
            return config
    except Exception as e:
        print(f"加载配置文件出错: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存配置文件出错: {e}")
        return False

def update_config(key, value):
    """更新配置项"""
    config = load_config()
    
    # 处理嵌套配置
    if '.' in key:
        parts = key.split('.')
        parent = config
        for i in range(len(parts) - 1):
            if parts[i] not in parent:
                parent[parts[i]] = {}
            parent = parent[parts[i]]
        parent[parts[-1]] = value
    else:
        config[key] = value
    
    return save_config(config)

def get_config(key=None):
    """获取配置项"""
    config = load_config()
    
    if key is None:
        return config
    
    # 处理嵌套配置
    if '.' in key:
        parts = key.split('.')
        value = config
        for part in parts:
            if part not in value:
                return None
            value = value[part]
        return value
    
    return config.get(key) 