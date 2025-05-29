# 书影音管理系统 - 代码介绍文档

## 1. 项目概述与目的

本项目是一个基于 Flask 框架开发的个人媒体收藏管理系统，旨在为用户提供一个简单、高效的方式来管理他们的书籍、电影和音乐收藏。系统采用模块化设计，使用 JSON 文件作为数据存储，并提供了完整的 CRUD 操作接口。此外，系统还支持 WebDAV 同步功能，实现多设备间的数据共享与备份。

## 2. 总体架构设计

### 2.1 架构模式

项目采用经典的 MVC（Model-View-Controller）架构模式：

- **Model**: 数据模型层，负责数据的定义和操作
- **View**: 视图层，负责用户界面的展示
- **Controller**: 控制层，负责业务逻辑的处理

### 2.2 系统架构图

```
+------------------+     +------------------+     +------------------+
|    前端界面      |     |    Flask应用     |     |    数据存储      |
|  (HTML/CSS/JS)   |<--->|  (Python/Flask)  |<--->|  (JSON/WebDAV)   |
+------------------+     +------------------+     +------------------+
```

## 3. 核心模块与组件分析

### 3.1 应用初始化 (`app/__init__.py`)

```python
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
                sync_data(force=False)
            else:
                # 如果未启用，使用更长的间隔
                sync_interval = 3600
                
            # 等待下一次同步
            time.sleep(sync_interval)
        except Exception as e:
            # 发生错误时，等待一段时间后重试
            time.sleep(300)  # 5分钟后重试

# 启动自动同步线程
sync_thread = threading.Thread(target=auto_sync_thread, daemon=True)
sync_thread.start()

from app import routes
```

主要职责：
- 创建 Flask 应用实例
- 配置静态文件和模板目录
- 初始化数据存储目录
- 设置应用密钥
- 配置日志系统
- 启动自动同步后台线程

### 3.2 路由模块 (`app/routes.py`)

主要职责：
- 处理 HTTP 请求
- 实现业务逻辑
- 返回响应数据

主要路由：
- `/`: 首页
- `/books`: 书籍管理
- `/movies`: 电影管理
- `/music`: 音乐管理
- `/search`: 搜索功能
- `/settings`: 系统设置
- `/sync`: WebDAV 同步

### 3.3 数据模型 (`app/models.py`)

主要职责：
- 定义数据结构
- 实现数据操作方法
- 处理数据验证

核心模型：
- Book: 书籍信息
- Movie: 电影信息
- Music: 音乐信息

### 3.4 工具函数 (`app/utils.py`)

主要职责：
- 提供通用功能
- 处理数据转换
- 实现辅助方法

### 3.5 配置管理 (`app/config.py`)

主要职责：
- 管理系统配置
- 加载和保存配置
- 提供配置访问接口

核心功能：
- `load_config()`: 加载配置文件
- `save_config()`: 保存配置文件
- `update_config()`: 更新配置项
- `get_config()`: 获取配置项

### 3.6 WebDAV 同步 (`app/webdav_sync.py`)

主要职责：
- 实现数据云端同步
- 管理备份和恢复
- 处理同步冲突

核心功能：
- `sync_data()`: 执行数据同步
- `create_zip_backup()`: 创建数据备份
- `extract_zip_backup()`: 恢复数据备份
- `test_connection()`: 测试 WebDAV 连接

## 4. 数据流与交互

### 4.1 数据流程

1. 用户请求流程：
   ```
   用户 -> 浏览器 -> Flask路由 -> 业务逻辑 -> 数据操作 -> 响应 -> 用户
   ```

2. 数据存储流程：
   ```
   用户输入 -> 数据验证 -> JSON序列化 -> 文件存储 -> 数据读取 -> 展示
   ```

3. 数据同步流程：
   ```
   本地数据 -> ZIP打包 -> WebDAV上传 -> 云端存储 -> WebDAV下载 -> 本地解压 -> 数据更新
   ```

### 4.2 模块间通信

- 路由模块与模型模块：通过函数调用
- 模型模块与数据存储：通过文件 I/O
- 前端与后端：通过 HTTP 请求/响应
- 本地与云端：通过 WebDAV 协议

## 5. 核心逻辑与算法

### 5.1 搜索实现

- 使用 Python 内置的字符串匹配
- 支持多字段搜索
- 实现模糊匹配

### 5.2 数据验证

- 输入数据验证
- 类型检查
- 必填字段验证

### 5.3 同步算法

- 基于时间戳的冲突检测
- 增量同步策略
- 自动备份机制

## 6. 数据存储设计

### 6.1 JSON 文件结构

```json
{
  "books": [
    {
      "id": "unique_id",
      "title": "书名",
      "author": "作者",
      "isbn": "ISBN号",
      "status": "阅读状态",
      "rating": 评分,
      "notes": "笔记"
    }
  ],
  "movies": [...],
  "music": [...]
}
```

### 6.2 数据访问模式

- 读取：全量读取后内存操作
- 写入：全量写入
- 更新：读取-修改-写入

### 6.3 配置文件结构

```json
{
  "webdav": {
    "enabled": false,
    "url": "",
    "username": "",
    "password": "",
    "remote_path": "/media-manager/",
    "sync_interval": 3600,
    "last_sync": null
  }
}
```

## 7. 错误处理与日志

### 7.1 错误处理机制

- 使用 Flask 的错误处理器
- 自定义错误页面
- 异常捕获和记录

### 7.2 日志系统

- 使用 Python 的 logging 模块
- 记录关键操作和错误
- 同步状态跟踪

## 8. 测试策略

### 8.1 测试类型

- 单元测试
- 集成测试
- 功能测试

### 8.2 测试工具

- pytest
- Flask 测试客户端

## 9. 依赖管理

### 9.1 核心依赖

```
Flask==2.0.1
Werkzeug==2.0.1
Jinja2==3.0.1
itsdangerous==2.0.1
click==8.0.1
MarkupSafe==2.0.1
webdav3.client
```

### 9.2 依赖说明

- Flask: Web 框架
- Werkzeug: WSGI 工具库
- Jinja2: 模板引擎
- itsdangerous: 安全相关
- click: 命令行接口
- MarkupSafe: 安全标记
- webdav3.client: WebDAV 客户端库

## 10. 部署与运维

### 10.1 部署要求

- Python 3.8+
- 足够的磁盘空间
- 现代网页浏览器
- WebDAV 服务（可选）

### 10.2 性能优化

- 数据缓存
- 延迟加载
- 分页处理
- 异步同步操作

## 11. 已知问题与未来改进

### 11.1 当前限制

- JSON 文件存储的性能限制
- 并发访问问题
- 数据备份机制
- 同步冲突处理

### 11.2 改进方向

- 迁移到数据库存储
- 添加用户认证
- 优化搜索性能
- 增强同步冲突解决
- 改进用户界面

## 12. 扩展与贡献指南

### 12.1 代码规范

- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串

### 12.2 开发流程

1. 创建功能分支
2. 编写测试
3. 实现功能
4. 提交代码
5. 创建 Pull Request

### 12.3 贡献指南

- 提交 Issue 前先搜索
- 遵循代码风格
- 编写测试用例
- 更新文档 