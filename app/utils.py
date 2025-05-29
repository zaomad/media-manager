import re
from datetime import datetime
import os

def format_date(date_str):
    """格式化日期字符串为易读格式"""
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime('%Y年%m月%d日 %H:%M')
    except (ValueError, TypeError):
        return date_str

def slugify(text):
    """将文本转换为URL友好的格式"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def truncate_text(text, length=100):
    """截断文本，添加省略号"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length] + "..."

def get_year_range():
    """获取年份范围，用于表单选择"""
    current_year = datetime.now().year
    return list(range(current_year, current_year - 100, -1))

def get_rating_options():
    """获取评分选项"""
    return [
        {"value": "1", "label": "★☆☆☆☆ (1分)"},
        {"value": "2", "label": "★★☆☆☆ (2分)"},
        {"value": "3", "label": "★★★☆☆ (3分)"},
        {"value": "4", "label": "★★★★☆ (4分)"},
        {"value": "5", "label": "★★★★★ (5分)"}
    ]

def get_book_status_options():
    """获取书籍状态选项"""
    return [
        {"value": "unread", "label": "未读"},
        {"value": "reading", "label": "在读"},
        {"value": "read", "label": "已读"}
    ]

def get_movie_status_options():
    """获取电影状态选项"""
    return [
        {"value": "unwatched", "label": "未看"},
        {"value": "watching", "label": "在看"},
        {"value": "watched", "label": "已看"}
    ]

def get_common_genres():
    """获取常见分类"""
    return {
        "books": [
            "小说", "文学", "历史", "科幻", "奇幻", "悬疑", "传记", 
            "科普", "哲学", "心理学", "经济", "管理", "艺术", "教育"
        ],
        "movies": [
            "动作", "冒险", "喜剧", "剧情", "恐怖", "科幻", "奇幻",
            "动画", "纪录片", "爱情", "惊悚", "战争", "西部", "音乐"
        ],
        "music": [
            "流行", "摇滚", "民谣", "电子", "古典", "爵士", "嘻哈",
            "乡村", "蓝调", "金属", "朋克", "世界音乐", "实验", "R&B"
        ]
    }

def get_image_url(url, view_mode='grid'):
    """
    处理图片URL，确保URL可用并根据视图模式返回合适尺寸的图片
    
    参数:
    url (str): 原始图片URL
    view_mode (str): 视图模式，可选值: 'grid', 'list', 'table', 'detail'
    
    返回:
    str: 处理后的图片URL
    """
    if not url or url.strip() == '':
        return None
        
    # 如果是本地上传的图片（以/uploads/开头）
    if url.startswith('/uploads/'):
        # 确保文件存在
        file_path = os.path.join('static', url[1:])  # 去掉开头的斜杠
        if not os.path.exists(file_path):
            print(f"警告: 文件不存在 {file_path}")
            return None
        return url
    
    # 处理外部URL
    # 如果是豆瓣图片，可以根据需要调整尺寸
    if 'douban.com' in url or 'doubanio.com' in url:
        # 移除可能存在的尺寸参数
        url = re.sub(r'(img\d\.doubanio\.com/view/subject/[^/]+/)', r'img1.doubanio.com/view/subject/', url)
        
        # 根据视图模式选择合适的尺寸
        if view_mode == 'grid':
            url = url.replace('/subject/', '/subject/s/')  # 小图，用于网格视图
        elif view_mode == 'list':
            url = url.replace('/subject/', '/subject/m/')  # 中图，用于列表视图
        elif view_mode == 'detail':
            url = url.replace('/subject/', '/subject/l/')  # 大图，用于详情页
        else:  # table或其他
            url = url.replace('/subject/', '/subject/s/')  # 默认小图
            
    # 处理其他可能的图片源
    # 例如，如果是Amazon图片
    elif 'amazon.com' in url or 'amazon.cn' in url:
        # 移除可能的尺寸参数
        url = re.sub(r'_SX\d+_|_SY\d+_|_SR\d+,\d+_', '', url)
        
        # 添加适当的尺寸参数
        if view_mode == 'grid':
            url += '_SX200_'  # 小图，宽度200px
        elif view_mode == 'list':
            url += '_SX100_'  # 更小的图，宽度100px
        elif view_mode == 'detail':
            url += '_SX400_'  # 大图，宽度400px
        else:
            url += '_SX80_'   # 缩略图，宽度80px
    
    return url 