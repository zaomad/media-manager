import os
import time
import json
import shutil
import zipfile
import tempfile
from datetime import datetime
from webdav3.client import Client
from app.config import get_config, update_config

# 数据目录路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def get_webdav_client():
    """创建WebDAV客户端"""
    webdav_config = get_config('webdav')
    
    if not webdav_config or not webdav_config.get('enabled'):
        return None
    
    options = {
        'webdav_hostname': webdav_config.get('url', ''),
        'webdav_login': webdav_config.get('username', ''),
        'webdav_password': webdav_config.get('password', ''),
        'webdav_root': '/',  # 使用根路径，避免路径重复
        'disable_check': True
    }
    
    # 验证必要的配置
    if not options['webdav_hostname'] or not options['webdav_login'] or not options['webdav_password']:
        print("WebDAV配置不完整，无法创建客户端")
        return None
    
    try:
        client = Client(options)
        return client
    except Exception as e:
        print(f"创建WebDAV客户端失败: {e}")
        return None

def ensure_remote_directory(client):
    """确保远程目录存在"""
    try:
        # 直接创建固定的目录结构
        print("确保远程目录结构存在")
        
        # 检查并创建media-manager目录
        if not client.check('media-manager'):
            print("创建media-manager目录")
            try:
                client.mkdir('media-manager')
            except Exception as e:
                print(f"创建media-manager目录失败: {e}")
                # 尝试使用完整路径
                try:
                    client.mkdir('/media-manager')
                except Exception as e:
                    print(f"使用完整路径创建media-manager目录也失败: {e}")
                    # 有些WebDAV服务可能需要逐级创建
                    return False
        
        # 检查并创建media-manager/backups目录
        if not client.check('media-manager/backups'):
            print("创建media-manager/backups目录")
            try:
                client.mkdir('media-manager/backups')
            except Exception as e:
                print(f"创建media-manager/backups目录失败: {e}")
                # 尝试使用完整路径
                try:
                    client.mkdir('/media-manager/backups')
                except Exception as e:
                    print(f"使用完整路径创建media-manager/backups目录也失败: {e}")
                    return False
        
        return True
    except Exception as e:
        print(f"确保远程目录存在失败: {e}")
        return False

def create_zip_backup(backup_path):
    """创建数据文件的ZIP备份"""
    try:
        # 数据文件列表
        data_files = ['books.json', 'movies.json', 'music.json', 'media_manager.db']
        
        # 创建ZIP文件
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in data_files:
                file_path = os.path.join(DATA_DIR, file)
                if os.path.exists(file_path):
                    print(f"添加文件到ZIP: {file}")
                    zipf.write(file_path, file)
                else:
                    print(f"文件不存在，跳过: {file}")
        
        print(f"ZIP备份创建成功: {backup_path}")
        return True
    except Exception as e:
        print(f"创建ZIP备份失败: {e}")
        return False

def extract_zip_backup(zip_path, target_dir):
    """解压ZIP备份到目标目录"""
    try:
        # 创建备份目录
        backup_dir = os.path.join(target_dir, 'backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 备份现有数据文件
        data_files = ['books.json', 'movies.json', 'music.json', 'media_manager.db']
        for file in data_files:
            file_path = os.path.join(target_dir, file)
            if os.path.exists(file_path):
                backup_file = os.path.join(backup_dir, f"{file}.{int(time.time())}.bak")
                shutil.copy2(file_path, backup_file)
                print(f"已备份文件: {file} -> {backup_file}")
        
        # 解压ZIP文件
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(target_dir)
        
        print(f"ZIP备份解压成功: {zip_path} -> {target_dir}")
        return True
    except Exception as e:
        print(f"解压ZIP备份失败: {e}")
        return False

def upload_file(client, local_path, remote_path):
    """上传文件到WebDAV服务器"""
    try:
        print(f"上传文件: {local_path} -> {remote_path}")
        
        # 确保远程目录存在
        remote_dir = os.path.dirname(remote_path)
        if remote_dir and not client.check(remote_dir):
            print(f"远程目录不存在: {remote_dir}")
            return False
        
        # 上传文件，添加重试机制
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 尝试上传文件
                client.upload_sync(remote_path=remote_path, local_path=local_path)
                print(f"文件上传成功: {remote_path}")
                return True
            except Exception as e:
                retry_count += 1
                print(f"上传失败 (尝试 {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    print(f"等待 2 秒后重试...")
                    time.sleep(2)
                else:
                    print(f"达到最大重试次数，上传失败")
                    return False
        
        return False
    except Exception as e:
        print(f"上传文件失败: {local_path} - {str(e)}")
        return False

def download_file(client, remote_path, local_path):
    """从WebDAV服务器下载文件"""
    try:
        print(f"下载文件: {remote_path} -> {local_path}")
        
        # 确保本地目录存在
        local_dir = os.path.dirname(local_path)
        if not os.path.exists(local_dir):
            print(f"创建本地目录: {local_dir}")
            os.makedirs(local_dir, exist_ok=True)
        
        # 下载文件，添加重试机制
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 尝试下载文件
                client.download_sync(remote_path=remote_path, local_path=local_path)
                print(f"文件下载成功: {local_path}")
                return True
            except Exception as e:
                retry_count += 1
                print(f"下载失败 (尝试 {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    print(f"等待 2 秒后重试...")
                    time.sleep(2)
                else:
                    print(f"达到最大重试次数，下载失败")
                    return False
        
        return False
    except Exception as e:
        print(f"下载文件失败: {remote_path} - {str(e)}")
        return False

def get_available_backups():
    """获取远程可用的备份列表"""
    client = get_webdav_client()
    if not client:
        return []
    
    try:
        # 确保基础目录存在
        ensure_remote_directory(client)
        
        # 检查media-manager/backups目录是否存在
        if not client.check('media-manager/backups'):
            print("media-manager/backups目录不存在，尝试创建")
            try:
                client.mkdir('media-manager/backups')
            except Exception as e:
                print(f"创建media-manager/backups目录失败: {e}")
                try:
                    # 尝试使用完整路径
                    client.mkdir('/media-manager/backups')
                except Exception as e:
                    print(f"使用完整路径创建media-manager/backups目录也失败: {e}")
                    return []
        
        # 获取备份文件列表
        backup_files = []
        
        try:
            # 尝试列出目录内容
            print("获取media-manager/backups目录内容")
            items = client.list('media-manager/backups')
            print(f"获取到 {len(items)} 个项目")
            
            for item in items:
                print(f"处理项目: {item}")
                
                # 跳过目录，只处理文件
                if item.endswith('/'):
                    print(f"跳过目录: {item}")
                    continue
                    
                # 提取文件名称
                file_name = item.strip('/').split('/')[-1]
                print(f"文件名称: {file_name}")
                
                # 检查是否是备份文件（格式为backup_YYYYMMDD_HHMMSS.zip）
                if file_name.startswith('backup_') and file_name.endswith('.zip'):
                    try:
                        # 尝试解析时间戳
                        timestamp_str = file_name[7:-4]  # 去掉"backup_"前缀和".zip"后缀
                        timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        
                        backup_files.append({
                            'name': file_name,
                            'path': f"media-manager/backups/{file_name}",
                            'timestamp': timestamp,
                            'formatted_time': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        print(f"添加备份: {file_name} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                    except ValueError as e:
                        # 如果不是有效的时间戳格式，则忽略
                        print(f"无效的时间戳格式: {timestamp_str} - {e}")
                        continue
                else:
                    print(f"不是备份文件: {file_name}")
        except Exception as e:
            print(f"列出目录内容失败: {e}")
            
            # 尝试使用完整路径
            try:
                print("尝试使用完整路径获取目录内容")
                items = client.list('/media-manager/backups')
                print(f"获取到 {len(items)} 个项目")
                
                for item in items:
                    print(f"处理项目: {item}")
                    
                    # 跳过目录，只处理文件
                    if item.endswith('/'):
                        print(f"跳过目录: {item}")
                        continue
                        
                    # 提取文件名称
                    file_name = item.strip('/').split('/')[-1]
                    print(f"文件名称: {file_name}")
                    
                    # 检查是否是备份文件（格式为backup_YYYYMMDD_HHMMSS.zip）
                    if file_name.startswith('backup_') and file_name.endswith('.zip'):
                        try:
                            # 尝试解析时间戳
                            timestamp_str = file_name[7:-4]  # 去掉"backup_"前缀和".zip"后缀
                            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                            
                            backup_files.append({
                                'name': file_name,
                                'path': f"media-manager/backups/{file_name}",
                                'timestamp': timestamp,
                                'formatted_time': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                            })
                            print(f"添加备份: {file_name} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                        except ValueError as e:
                            # 如果不是有效的时间戳格式，则忽略
                            print(f"无效的时间戳格式: {timestamp_str} - {e}")
                            continue
                    else:
                        print(f"不是备份文件: {file_name}")
            except Exception as e2:
                print(f"使用完整路径获取目录内容也失败: {e2}")
        
        # 按时间戳降序排序（最新的在前）
        backup_files.sort(key=lambda x: x['timestamp'], reverse=True)
        print(f"总共找到 {len(backup_files)} 个有效备份")
        return backup_files
    except Exception as e:
        print(f"获取可用备份列表失败: {e}")
        return []

def sync_data(force=False, direction='both', backup_path=None):
    """
    同步数据文件
    
    参数:
    force (bool): 是否强制同步，忽略时间间隔限制
    direction (str): 同步方向，可选值: 'upload', 'download'
    backup_path (str): 下载时指定的备份路径，如果为None则使用最新的备份
    """
    client = get_webdav_client()
    if not client:
        print("WebDAV客户端创建失败，无法同步")
        return False
    
    webdav_config = get_config('webdav')
    if not webdav_config.get('enabled'):
        print("WebDAV同步未启用")
        return False
    
    # 检查上次同步时间，避免频繁同步
    last_sync = webdav_config.get('last_sync')
    sync_interval = webdav_config.get('sync_interval', 3600)
    
    if not force and last_sync:
        time_since_last_sync = time.time() - last_sync
        if time_since_last_sync < sync_interval:
            print(f"距离上次同步时间不足{sync_interval}秒，跳过同步")
            return True
    
    # 确保远程目录存在
    if not ensure_remote_directory(client):
        print("无法确保远程目录存在，同步失败")
        return False
    
    success = True
    
    if direction == 'upload':
        # 创建带时间戳的ZIP文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"backup_{timestamp}.zip"
        temp_zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
        remote_zip_path = f"media-manager/backups/{zip_filename}"
        
        # 创建ZIP备份
        if not create_zip_backup(temp_zip_path):
            print("创建ZIP备份失败")
            return False
        
        # 上传ZIP文件
        if not upload_file(client, temp_zip_path, remote_zip_path):
            print("上传ZIP备份失败")
            success = False
        
        # 清理临时文件
        try:
            os.remove(temp_zip_path)
            print(f"临时ZIP文件已删除: {temp_zip_path}")
        except Exception as e:
            print(f"删除临时ZIP文件失败: {e}")
    
    elif direction == 'download':
        # 如果没有指定备份路径，则获取可用的备份列表
        if not backup_path:
            backups = get_available_backups()
            if not backups:
                print("没有找到可用的远程备份")
                return False
            
            # 使用最新的备份
            backup_path = backups[0]['path']
            print(f"使用最新的备份: {backup_path}")
        
        # 创建临时文件路径
        temp_zip_path = os.path.join(tempfile.gettempdir(), os.path.basename(backup_path))
        
        # 下载ZIP文件
        if not download_file(client, backup_path, temp_zip_path):
            print("下载ZIP备份失败")
            return False
        
        # 解压ZIP文件
        if not extract_zip_backup(temp_zip_path, DATA_DIR):
            print("解压ZIP备份失败")
            success = False
        
        # 清理临时文件
        try:
            os.remove(temp_zip_path)
            print(f"临时ZIP文件已删除: {temp_zip_path}")
        except Exception as e:
            print(f"删除临时ZIP文件失败: {e}")
    
    else:
        # 双向同步模式（已不再支持）
        print("双向同步模式已不再支持")
        return False
    
    # 更新最后同步时间
    if success:
        update_config('webdav.last_sync', time.time())
        print("同步成功，已更新最后同步时间")
    else:
        print("同步过程中出现错误")
    
    return success

def test_connection():
    """测试WebDAV连接"""
    client = get_webdav_client()
    if not client:
        return False, "WebDAV客户端创建失败，请检查配置"
    
    try:
        # 尝试列出根目录
        print("测试WebDAV连接...")
        client.list('/')
        
        # 尝试创建并检查media-manager目录
        try:
            if not client.check('media-manager'):
                client.mkdir('media-manager')
                print("成功创建media-manager目录")
        except Exception as e:
            print(f"创建media-manager目录失败，但连接成功: {e}")
            
        return True, "连接成功"
    except Exception as e:
        return False, f"连接失败: {str(e)}" 