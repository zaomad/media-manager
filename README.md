# 书影音管理系统 (Media Manager)

一个功能完整的个人媒体收藏管理系统，帮助用户轻松管理书籍、电影和音乐收藏。使用 Python Flask 框架构建，提供直观的用户界面和强大的管理功能。

## ✨ 主要特性

- 📚 **书籍管理**
  - 添加、编辑、删除和查看书籍信息
  - 支持 ISBN 查询和自动填充（待办）
  - 自定义分类和标签
  - 阅读进度追踪（待办）
  - 按作者单选筛选功能
  - 书架功能（显示已拥有的书籍）

- 🎬 **电影管理**
  - 完整的电影信息管理
  - 支持豆瓣电影信息导入（待办）
  - 观影状态追踪（待办）
  - 个人评分和评论
  - 按导演单选筛选功能
  - 支持记录主演信息

- 🎵 **音乐管理**
  - 专辑管理
  - 艺术家信息记录
  - 音乐分类和标签
  - 按艺术家单选筛选功能
  - 支持记录音乐状态

- 🔍 **智能搜索**
  - 全文搜索功能
  - 多条件筛选
  - 标签筛选
  - 状态筛选
  - 改进的筛选界面

- 📱 **响应式设计**
  - 完美适配桌面和移动设备（没有）
  - 直观的用户界面
  - 流畅的操作体验（不见得）
  - 支持卡片、列表和表格三种视图模式

- 🔄 **WebDAV 同步**
  - 数据云端备份与同步
  - 自动定期同步
  - 手动同步控制
  - 多设备数据共享

## 🛠 技术栈

- **后端**
  - Python 3.8+
  - Flask 2.0.1
  - Werkzeug 2.0.1
  - Jinja2 3.0.1
  - webdavclient3 3.14.6
  - itsdangerous 2.0.1
  - click 8.0.1
  - MarkupSafe 2.0.1

- **前端**
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 5
  - Vue.js

- **数据存储**
  - JSON 文件存储
  - SQLite 数据库（新增）
  - WebDAV 云同步
  - 支持未来扩展至数据库

## 🚀 快速开始

### 系统要求

- Python 3.8 或更高版本
- pip（Python 包管理器）
- 现代网页浏览器

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/zaomad/media-manager.git
   cd media-manager
   ```

2. **创建虚拟环境**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行应用**
   ```bash
   python run.py
   ```

5. **访问应用**
   打开浏览器访问：`http://localhost:5000`

### 数据库迁移

项目最近添加了SQLite数据库支持，如果您正在使用旧版本的JSON存储，可以使用以下命令将数据迁移到SQLite：

```bash
python migrate_to_sqlite.py
```

迁移过程会自动：
- 创建SQLite数据库文件
- 将JSON数据导入到数据库
- 更新数据库架构，添加新字段
- 保留原始JSON文件作为备份

详细的迁移说明请参考 `README_SQLITE_MIGRATION.md` 文件。

## 💻 使用指南

### 添加媒体条目

1. 在主页选择相应的媒体类型（书籍、电影或音乐）
2. 点击"添加"按钮
3. 填写表单信息
4. 上传封面图片（可选）
5. 点击"保存"按钮

### 管理媒体条目

- **查看详情**：点击条目的"详情"按钮
- **编辑条目**：点击条目的"编辑"按钮
- **删除条目**：点击条目的"删除"按钮
- **筛选条目**：使用页面上的筛选器和搜索框
- **切换视图**：使用视图切换按钮在卡片、列表和表格视图之间切换

### 数据同步

1. 进入"设置"页面
2. 配置WebDAV服务器信息
3. 启用自动同步或手动点击"立即同步"按钮

## 📁 项目结构

```
media-manager/
├── app/                    # 应用核心代码
│   ├── __init__.py        # Flask应用初始化
│   ├── routes.py          # 路由定义
│   ├── models.py          # 数据模型
│   ├── utils.py           # 工具函数
│   ├── data.py            # 数据处理
│   ├── config.py          # 配置管理
│   ├── webdav_sync.py     # WebDAV同步功能
│   ├── forms/             # 表单定义
│   ├── models/            # 模型定义
│   ├── routes/            # 路由模块
│   ├── static/            # 静态资源
│   └── templates/         # 模板文件
├── static/                # 静态资源
├── templates/             # HTML模板
│   ├── base.html          # 基础模板
│   ├── index.html         # 首页
│   ├── books.html         # 书籍列表页
│   ├── book_form.html     # 书籍添加/编辑表单
│   ├── bookshelf.html     # 书架页面（已拥有的书籍）
│   ├── movies.html        # 电影列表页
│   ├── movie_form.html    # 电影添加/编辑表单
│   ├── music.html         # 音乐列表页
│   ├── music_form.html    # 音乐添加/编辑表单
│   ├── item_detail.html   # 条目详情页
│   ├── settings.html      # 设置页面
│   ├── private_collections.html # 私人收藏页面
│   ├── private_artists.html    # 艺术家收藏页面
│   └── private_novels.html     # 小说收藏页面
├── data/                  # 数据存储
├── config/                # 配置文件
├── requirements.txt       # 项目依赖
└── run.py                # 应用入口
```

## 📄 页面结构与功能

- **首页 (index.html)**
  - 系统概览
  - 最近添加的条目
  - 快速导航

- **书籍管理 (books.html)**
  - 书籍列表展示（卡片/列表/表格视图）
  - 按标题、作者搜索
  - 按阅读状态筛选
  - 按分类标签多选筛选
  - 按作者单选筛选

- **书架 (bookshelf.html)**
  - 显示已拥有的书籍
  - 与书籍管理页面类似的功能

- **电影管理 (movies.html)**
  - 电影列表展示（卡片/列表/表格视图）
  - 按标题、导演搜索
  - 按观看状态筛选
  - 按类型多选筛选
  - 按导演单选筛选

- **音乐管理 (music.html)**
  - 音乐列表展示（卡片/列表/表格视图）
  - 按专辑名、艺术家搜索
  - 按收听状态筛选
  - 按类型多选筛选
  - 按艺术家单选筛选

- **条目表单 (book_form.html, movie_form.html, music_form.html)**
  - 添加/编辑媒体条目
  - 表单验证
  - 封面图片上传

- **条目详情 (item_detail.html)**
  - 显示媒体条目的详细信息
  - 编辑和删除操作

- **设置 (settings.html)**
  - WebDAV同步配置
  - 系统偏好设置
  - 数据备份与恢复

- **私人收藏 (private_collections.html)**
  - 用户的特殊收藏
  - 自定义分组

- **艺术家收藏 (private_artists.html)**
  - 艺术家作品收藏
  - 艺术家信息管理

- **小说收藏 (private_novels.html)**
  - 小说特别收藏
  - 阅读进度追踪

## 🔄 WebDAV 同步功能

书影音管理系统支持通过 WebDAV 协议与云存储服务进行数据同步，确保您的媒体收藏数据安全且可在多设备间共享：

- **自动同步**：系统会根据设定的时间间隔自动同步数据
- **手动同步**：随时手动触发同步操作
- **双向同步**：支持上传和下载数据
- **历史备份**：自动创建数据备份，防止数据丢失
- **连接测试**：提供 WebDAV 服务器连接测试功能

### 支持的 WebDAV 服务

- NextCloud
- Seafile
- 坚果云
- Box.com
- 其他兼容 WebDAV 协议的云存储服务

## 🔜 最近更新

- [x] 改进了书籍界面的按作者筛选功能，使用单选按钮，选中标签高亮显示
- [x] 改进了音乐界面的按艺术家筛选功能，使用单选按钮，选中标签高亮显示
- [x] 改进了电影界面的按导演筛选功能
- [x] 修复了书籍详情页显示问题，正确显示出版年份和类型信息
- [x] 修复了书籍简介保存问题
- [x] 更新了数据库架构，添加了必要的字段
- [x] 修复了电影主演信息保存问题
- [x] 修复了音乐状态保存问题
- [x] 修复了书籍按分类筛选功能

## 🔜 开发计划

- [ ] 用户认证系统
- [ ] 数据库支持
- [ ] 标签系统优化
- [x] 数据导入/导出
- [ ] 统计分析功能
- [ ] API 文档
- [ ] 移动端应用
