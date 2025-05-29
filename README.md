# 书影音管理系统 (Media Manager)

一个功能完整的个人媒体收藏管理系统，帮助用户轻松管理书籍、电影和音乐收藏。使用 Python Flask 框架构建，提供直观的用户界面和强大的管理功能。

## ✨ 主要特性

- 📚 **书籍管理**
  - 添加、编辑、删除和查看书籍信息
  - 支持 ISBN 查询和自动填充
  - 自定义分类和标签
  - 阅读进度追踪

- 🎬 **电影管理**
  - 完整的电影信息管理
  - 支持豆瓣电影信息导入
  - 观影状态追踪
  - 个人评分和评论

- 🎵 **音乐管理**
  - 专辑和单曲管理
  - 艺术家信息记录
  - 音乐分类和标签
  - 收藏状态追踪

- 🔍 **智能搜索**
  - 全文搜索功能
  - 多条件筛选
  - 标签筛选
  - 状态筛选

- 📱 **响应式设计**
  - 完美适配桌面和移动设备
  - 直观的用户界面
  - 流畅的操作体验

## 🛠 技术栈

- **后端**
  - Python 3.8+
  - Flask 2.0.1
  - Werkzeug 2.0.1
  - Jinja2 3.0.1

- **前端**
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 5
  - Vue.js

- **数据存储**
  - JSON 文件存储
  - 支持未来扩展至数据库

## 🚀 快速开始

### 系统要求

- Python 3.8 或更高版本
- pip（Python 包管理器）
- 现代网页浏览器

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/media-manager.git
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

## 📁 项目结构

```
media-manager/
├── app/                    # 应用核心代码
│   ├── __init__.py        # Flask应用初始化
│   ├── routes.py          # 路由定义
│   ├── models.py          # 数据模型
│   ├── utils.py           # 工具函数
│   ├── data.py            # 数据处理
│   ├── forms/             # 表单定义
│   ├── models/            # 模型定义
│   ├── routes/            # 路由模块
│   ├── static/            # 静态资源
│   └── templates/         # 模板文件
├── static/                # 静态资源
├── templates/             # HTML模板
├── data/                  # 数据存储
├── requirements.txt       # 项目依赖
└── run.py                # 应用入口
```

## 🔜 开发计划

- [ ] 用户认证系统
- [ ] 数据库支持
- [ ] 标签系统优化
- [ ] 数据导入/导出
- [ ] 统计分析功能
- [ ] API 文档
- [ ] 移动端应用

## 🤝 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

- 提交问题和建议
- 改进文档
- 提交代码改进
- 分享使用经验

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📮 联系方式

- 项目维护者：[Your Name]
- 邮箱：[your.email@example.com]
- 项目主页：[https://github.com/yourusername/media-manager]

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！ 