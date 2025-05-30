import os
import json
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from app.database import get_db_connection, init_db

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 数据目录路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def load_json_data(file_path):
    """从JSON文件加载数据"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"加载JSON文件失败: {file_path}, 错误: {e}")
        return []

def backup_json_files():
    """备份JSON文件"""
    try:
        backup_dir = os.path.join(DATA_DIR, 'backup', datetime.now().strftime('%Y%m%d_%H%M%S'))
        os.makedirs(backup_dir, exist_ok=True)
        
        for file_name in ['books.json', 'movies.json', 'music.json']:
            source_path = os.path.join(DATA_DIR, file_name)
            if os.path.exists(source_path):
                target_path = os.path.join(backup_dir, file_name)
                with open(source_path, 'r', encoding='utf-8') as src:
                    with open(target_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                logger.info(f"已备份文件: {file_name} -> {target_path}")
        
        return backup_dir
    except Exception as e:
        logger.error(f"备份JSON文件失败: {e}")
        return None

def migrate_books():
    """迁移书籍数据"""
    books_file = os.path.join(DATA_DIR, 'books.json')
    books = load_json_data(books_file)
    
    if not books:
        logger.info("没有书籍数据需要迁移")
        return 0
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        count = 0
        
        for book in books:
            # 准备数据
            book_data = {
                'id': book.get('id', ''),
                'title': book.get('title', ''),
                'author': book.get('author', ''),
                'isbn': book.get('isbn', ''),
                'publisher': book.get('publisher', ''),
                'publish_date': book.get('publish_date', ''),
                'pages': book.get('pages', 0),
                'status': book.get('status', ''),
                'rating': book.get('rating', 0),
                'notes': book.get('notes', ''),
                'cover_url': book.get('cover_url', ''),
                'tags': ','.join(book.get('tags', [])) if isinstance(book.get('tags'), list) else book.get('tags', '')
            }
            
            # 插入数据
            cursor.execute('''
            INSERT OR REPLACE INTO books 
            (id, title, author, isbn, publisher, publish_date, pages, status, rating, notes, cover_url, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                book_data['id'], book_data['title'], book_data['author'], 
                book_data['isbn'], book_data['publisher'], book_data['publish_date'], 
                book_data['pages'], book_data['status'], book_data['rating'], 
                book_data['notes'], book_data['cover_url'], book_data['tags']
            ))
            count += 1
            
            # 处理标签
            if isinstance(book.get('tags'), list) and book.get('tags'):
                for tag_name in book.get('tags'):
                    # 确保标签存在
                    cursor.execute('INSERT OR IGNORE INTO tags (id, name, type) VALUES (?, ?, ?)', 
                                 (tag_name.lower().replace(' ', '_'), tag_name, 'book'))
                    
                    # 获取标签ID
                    cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                    tag_id = cursor.fetchone()[0]
                    
                    # 创建关联
                    cursor.execute('''
                    INSERT OR IGNORE INTO item_tags (item_id, tag_id, item_type)
                    VALUES (?, ?, ?)
                    ''', (book_data['id'], tag_id, 'book'))
        
        conn.commit()
        logger.info(f"成功迁移 {count} 条书籍数据")
        return count
    except Exception as e:
        conn.rollback()
        logger.error(f"迁移书籍数据失败: {e}")
        return 0
    finally:
        conn.close()

def migrate_movies():
    """迁移电影数据"""
    movies_file = os.path.join(DATA_DIR, 'movies.json')
    movies = load_json_data(movies_file)
    
    if not movies:
        logger.info("没有电影数据需要迁移")
        return 0
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        count = 0
        
        for movie in movies:
            # 准备数据
            movie_data = {
                'id': movie.get('id', ''),
                'title': movie.get('title', ''),
                'director': movie.get('director', ''),
                'year': movie.get('year', 0),
                'genre': movie.get('genre', ''),
                'status': movie.get('status', ''),
                'rating': movie.get('rating', 0),
                'notes': movie.get('notes', ''),
                'poster_url': movie.get('poster_url', ''),
                'tags': ','.join(movie.get('tags', [])) if isinstance(movie.get('tags'), list) else movie.get('tags', '')
            }
            
            # 插入数据
            cursor.execute('''
            INSERT OR REPLACE INTO movies 
            (id, title, director, year, genre, status, rating, notes, poster_url, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie_data['id'], movie_data['title'], movie_data['director'], 
                movie_data['year'], movie_data['genre'], movie_data['status'], 
                movie_data['rating'], movie_data['notes'], movie_data['poster_url'], 
                movie_data['tags']
            ))
            count += 1
            
            # 处理标签
            if isinstance(movie.get('tags'), list) and movie.get('tags'):
                for tag_name in movie.get('tags'):
                    # 确保标签存在
                    cursor.execute('INSERT OR IGNORE INTO tags (id, name, type) VALUES (?, ?, ?)', 
                                 (tag_name.lower().replace(' ', '_'), tag_name, 'movie'))
                    
                    # 获取标签ID
                    cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                    tag_id = cursor.fetchone()[0]
                    
                    # 创建关联
                    cursor.execute('''
                    INSERT OR IGNORE INTO item_tags (item_id, tag_id, item_type)
                    VALUES (?, ?, ?)
                    ''', (movie_data['id'], tag_id, 'movie'))
        
        conn.commit()
        logger.info(f"成功迁移 {count} 条电影数据")
        return count
    except Exception as e:
        conn.rollback()
        logger.error(f"迁移电影数据失败: {e}")
        return 0
    finally:
        conn.close()

def migrate_music():
    """迁移音乐数据"""
    music_file = os.path.join(DATA_DIR, 'music.json')
    music_items = load_json_data(music_file)
    
    if not music_items:
        logger.info("没有音乐数据需要迁移")
        return 0
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        count = 0
        
        for music in music_items:
            # 准备数据
            music_data = {
                'id': music.get('id', ''),
                'title': music.get('title', ''),
                'artist': music.get('artist', ''),
                'album': music.get('album', ''),
                'year': music.get('year', 0),
                'genre': music.get('genre', ''),
                'rating': music.get('rating', 0),
                'notes': music.get('notes', ''),
                'cover_url': music.get('cover_url', ''),
                'tags': ','.join(music.get('tags', [])) if isinstance(music.get('tags'), list) else music.get('tags', '')
            }
            
            # 插入数据
            cursor.execute('''
            INSERT OR REPLACE INTO music 
            (id, title, artist, album, year, genre, rating, notes, cover_url, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                music_data['id'], music_data['title'], music_data['artist'], 
                music_data['album'], music_data['year'], music_data['genre'], 
                music_data['rating'], music_data['notes'], music_data['cover_url'], 
                music_data['tags']
            ))
            count += 1
            
            # 处理标签
            if isinstance(music.get('tags'), list) and music.get('tags'):
                for tag_name in music.get('tags'):
                    # 确保标签存在
                    cursor.execute('INSERT OR IGNORE INTO tags (id, name, type) VALUES (?, ?, ?)', 
                                 (tag_name.lower().replace(' ', '_'), tag_name, 'music'))
                    
                    # 获取标签ID
                    cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                    tag_id = cursor.fetchone()[0]
                    
                    # 创建关联
                    cursor.execute('''
                    INSERT OR IGNORE INTO item_tags (item_id, tag_id, item_type)
                    VALUES (?, ?, ?)
                    ''', (music_data['id'], tag_id, 'music'))
        
        conn.commit()
        logger.info(f"成功迁移 {count} 条音乐数据")
        return count
    except Exception as e:
        conn.rollback()
        logger.error(f"迁移音乐数据失败: {e}")
        return 0
    finally:
        conn.close()

def run_migration():
    """执行完整的数据迁移"""
    logger.info("开始数据迁移: JSON -> SQLite")
    
    # 确保数据库初始化
    init_db()
    
    # 备份JSON文件
    backup_dir = backup_json_files()
    if not backup_dir:
        logger.error("备份失败，中止迁移")
        return False
    
    # 迁移数据
    book_count = migrate_books()
    movie_count = migrate_movies()
    music_count = migrate_music()
    
    total_count = book_count + movie_count + music_count
    logger.info(f"数据迁移完成，共迁移 {total_count} 条记录")
    logger.info(f"- 书籍: {book_count} 条")
    logger.info(f"- 电影: {movie_count} 条")
    logger.info(f"- 音乐: {music_count} 条")
    
    return True

if __name__ == "__main__":
    run_migration() 