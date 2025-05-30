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
- `/bookshelf`: 书架（已拥有的书籍）

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

### 3.7 数据库模式 (`app/database.py`)

主要职责：
- 定义数据库表结构
- 初始化数据库
- 更新数据库架构

核心功能：
- `init_db()`: 初始化数据库表
- `update_db_schema()`: 更新数据库表结构
- `get_db_connection()`: 获取数据库连接

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

### 5.4 筛选功能实现

#### 5.4.1 按分类筛选
- 使用复选框实现多选功能
- 实时筛选更新显示结果
- 支持搜索和清除筛选

#### 5.4.2 按作者/导演/艺术家筛选
- 使用单选按钮实现单选功能
- 选中标签高亮显示
- 支持清除选择
- 使用CSS隐藏单选按钮，保持界面美观

#### 5.4.3 筛选器的实现方式
```javascript
// 筛选图书
function filterBooks() {
    const booksApp = document.getElementById('books-app').__vue__;
    const searchQuery = booksApp.searchQuery.toLowerCase();
    const statusFilter = booksApp.filterStatus;
    
    // 获取选中的分类和作者
    const selectedGenres = Array.from(document.querySelectorAll('.genre-checkbox:checked'))
        .map(checkbox => checkbox.value);
    
    const selectedAuthor = document.querySelector('.author-radio:checked')?.value || '';
    
    const allBooks = document.querySelectorAll('.book-item');
    
    allBooks.forEach(book => {
        const title = book.dataset.title.toLowerCase();
        const author = book.dataset.author.toLowerCase();
        const status = book.dataset.status;
        const tagsText = book.dataset.genre || '';
        
        // 搜索匹配 (标题或作者)
        const matchesSearch = !searchQuery || 
            title.includes(searchQuery) || 
            author.includes(searchQuery);
        
        // 状态匹配
        const matchesStatus = !statusFilter || status === statusFilter;
        
        // 分类匹配 (必须匹配所有选定的分类标签)
        let matchesGenre = selectedGenres.length === 0; // 如果没有选中分类，则默认匹配
        
        if (!matchesGenre) {
            // 检查书籍是否包含所有选定的分类
            matchesGenre = selectedGenres.every(filter => {
                // 查找书籍的分类是否包含此过滤标签
                return tagsText.toLowerCase().includes(filter.toLowerCase());
            });
        }
        
        // 作者匹配
        let matchesAuthor = !selectedAuthor; // 如果没有选中作者，则默认匹配
        
        if (!matchesAuthor) {
            // 检查书籍作者是否匹配选中的作者
            matchesAuthor = author === selectedAuthor.toLowerCase();
        }
        
        // 应用筛选
        if (matchesSearch && matchesStatus && matchesGenre && matchesAuthor) {
            book.style.display = '';
        } else {
            book.style.display = 'none';
        }
    });
}
```

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
      "notes": "笔记",
      "tags": "分类标签",
      "publish_date": "出版日期",
      "description": "简介",
      "is_owned": true/false
    }
  ],
  "movies": [
    {
      "id": "unique_id",
      "title": "电影名",
      "director": "导演",
      "cast": "主演",
      "year": "年份",
      "genre": "类型",
      "status": "观看状态",
      "rating": 评分,
      "notes": "笔记"
    }
  ],
  "music": [
    {
      "id": "unique_id",
      "title": "标题",
      "artist": "艺术家",
      "album": "专辑",
      "year": "年份",
      "genre": "类型",
      "status": "收听状态",
      "rating": 评分,
      "notes": "笔记"
    }
  ]
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

### 6.4 数据库架构更新

最近对数据库架构进行了以下更新：

1. **书籍表**
   - 添加 `description` 字段，用于存储书籍简介
   - 添加 `is_owned` 字段，用于标记是否拥有该书籍
   - 将 `genre` 字段重命名为 `tags`，用于存储分类标签
   - 将 `year` 字段重命名为 `publish_date`，用于存储出版日期

2. **电影表**
   - 添加 `cast` 字段，用于存储主演信息

3. **音乐表**
   - 添加 `status` 字段，用于存储收听状态

这些更新确保了数据库能够正确存储和检索所有必要的信息，支持新增的功能和修复的问题。

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

### 11.3 最近修复的问题

1. **书籍详情页显示问题**
   - 修复了书籍详情页无法正确显示出版年份和类型信息的问题
   - 将模板中的 `item.year` 替换为 `item.publish_date`
   - 将模板中的 `item.genre` 替换为 `item.tags`

2. **书籍简介保存问题**
   - 添加了数据库中的 `description` 字段
   - 修改了表单处理逻辑，确保简介信息被正确保存

3. **电影主演信息问题**
   - 添加了数据库中的 `cast` 字段
   - 修改了表单处理逻辑，确保主演信息被正确保存和显示

4. **音乐状态保存问题**
   - 添加了数据库中的 `status` 字段
   - 修改了表单处理逻辑，确保状态信息被正确保存

5. **筛选功能问题**
   - 修复了书籍按分类筛选功能
   - 改进了按作者/导演/艺术家筛选的用户体验
   - 统一了三个界面的筛选功能实现方式

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