import re
from datetime import datetime

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