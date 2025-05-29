from flask import Flask
import os
import threading
import time
import logging

app = Flask(__name__, 
            static_folder='../static',
            template_folder='../templates')

# 确保数据目录存在
os.makedirs('../data', exist_ok=True)

# 设置密钥以便flash消息能够正常工作
app.secret_key = os.urandom(24)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 自动同步线程
def auto_sync_thread():
    """后台线程，定期自动同步数据"""
    logger.info("自动同步线程已启动")
    
    # 延迟导入，避免循环导入
    try:
        from app.config import get_config
        from app.webdav_sync import sync_data
        
        while True:
            try:
                # 获取配置
                config = get_config()
                webdav_config = config.get('webdav', {})
                
                # 检查是否启用了WebDAV同步
                if webdav_config.get('enabled', False):
                    # 获取同步间隔
                    sync_interval = webdav_config.get('sync_interval', 3600)
                    
                    # 执行同步
                    logger.info(f"执行自动同步，间隔: {sync_interval}秒")
                    sync_result = sync_data(force=False, direction='upload')
                    
                    if sync_result:
                        logger.info("自动同步成功")
                    else:
                        logger.warning("自动同步失败")
                else:
                    logger.info("WebDAV同步未启用，跳过自动同步")
                    # 如果未启用，使用更长的间隔
                    sync_interval = 3600
                    
                # 等待下一次同步
                time.sleep(sync_interval)
            except Exception as e:
                logger.error(f"自动同步线程发生错误: {e}")
                # 发生错误时，等待一段时间后重试
                time.sleep(300)  # 5分钟后重试
    except ImportError as e:
        logger.error(f"无法导入WebDAV同步模块: {e}")
        logger.warning("WebDAV同步功能将被禁用")

# 启动自动同步线程
sync_thread = threading.Thread(target=auto_sync_thread, daemon=True)
sync_thread.start()

# 导入路由
from app import routes 