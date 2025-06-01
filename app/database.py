import os
import sqlite3
import logging
from pathlib import Path

# 设置日志
logger = logging.getLogger(__name__)

# 数据库文件路径
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DB_FILE = os.path.join(DB_DIR, 'media_manager.db')

# 确保数据目录存在
os.makedirs(DB_DIR, exist_ok=True)

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 使查询结果可通过列名访问
    return conn

def init_db():
    """初始化数据库，创建表结构"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 创建书籍表
        cursor.execute('''\
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            isbn TEXT,
            publisher TEXT,
            publish_date TEXT,
            pages INTEGER,
            status TEXT,
            rating REAL,
            notes TEXT,
            description TEXT,
            cover_url TEXT,
            tags TEXT,
            is_owned BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建电影表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            director TEXT,
            cast TEXT,
            year INTEGER,
            genre TEXT,
            status TEXT,
            rating REAL,
            notes TEXT,
            poster_url TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建音乐表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS music (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT,
            album TEXT,
            year INTEGER,
            genre TEXT,
            status TEXT,
            rating REAL,
            notes TEXT,
            cover_url TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建标签表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建项目-标签关联表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_tags (
            item_id TEXT NOT NULL,
            tag_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            PRIMARY KEY (item_id, tag_id, item_type),
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_title ON books (title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_title ON movies (title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_music_title ON music (title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_name ON tags (name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_tags_item_id ON item_tags (item_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_tags_tag_id ON item_tags (tag_id)')
        
        conn.commit()
        logger.info("数据库初始化成功")
    except Exception as e:
        conn.rollback()
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        conn.close()

def update_db_schema():
    """更新数据库表结构，添加缺失的字段"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 检查books表是否缺少description字段
        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'description' not in columns:
            logger.info("添加books表的description字段")
            cursor.execute("ALTER TABLE books ADD COLUMN description TEXT")
        
        # 检查books表是否缺少is_owned字段
        if 'is_owned' not in columns:
            logger.info("添加books表的is_owned字段")
            cursor.execute("ALTER TABLE books ADD COLUMN is_owned BOOLEAN DEFAULT 0")
        
        # 检查books表是否缺少series字段
        if 'series' not in columns:
            logger.info("添加books表的series字段")
            cursor.execute("ALTER TABLE books ADD COLUMN series TEXT")
        
        # 检查books表是否缺少translator字段
        if 'translator' not in columns:
            logger.info("添加books表的translator字段")
            cursor.execute("ALTER TABLE books ADD COLUMN translator TEXT")
        
        # 检查books表是否缺少totalPage字段（将使用pages字段）
        if 'page_count' not in columns:
            logger.info("添加books表的page_count字段")
            cursor.execute("ALTER TABLE books ADD COLUMN page_count INTEGER")
        
        # 检查books表是否缺少price字段
        if 'price' not in columns:
            logger.info("添加books表的price字段")
            cursor.execute("ALTER TABLE books ADD COLUMN price TEXT")
        
        # 检查movies表是否缺少cast字段
        cursor.execute("PRAGMA table_info(movies)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'cast' not in columns:
            logger.info("添加movies表的cast字段")
            cursor.execute("ALTER TABLE movies ADD COLUMN cast TEXT")
        
        # 检查music表是否缺少status字段
        cursor.execute("PRAGMA table_info(music)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'status' not in columns:
            logger.info("添加music表的status字段")
            cursor.execute("ALTER TABLE music ADD COLUMN status TEXT")
        
        conn.commit()
        logger.info("数据库表结构更新成功")
    except Exception as e:
        conn.rollback()
        logger.error(f"更新数据库表结构失败: {e}")
    finally:
        conn.close()

# 在模块导入时初始化数据库
if not os.path.exists(DB_FILE):
    logger.info(f"数据库文件不存在，创建新数据库: {DB_FILE}")
    init_db()
else:
    logger.info(f"数据库已存在: {DB_FILE}")
    # 更新数据库表结构
    update_db_schema()
    # 可以在这里添加数据库版本检查和迁移逻辑 