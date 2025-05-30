#!/usr/bin/env python3
"""
SQLite数据库功能测试脚本

此脚本用于测试媒体管理系统的SQLite数据库功能。
"""

import os
import sys
import logging
import sqlite3
from app.database import get_db_connection, init_db
from app.dao.book_dao import BookDAO
from app.dao.movie_dao import MovieDAO
from app.dao.music_dao import MusicDAO

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """测试数据库连接"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT sqlite_version();')
        version = cursor.fetchone()[0]
        conn.close()
        logger.info(f"SQLite版本: {version}")
        return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False

def test_tables_exist():
    """测试表是否存在"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        expected_tables = ['books', 'movies', 'music', 'tags', 'item_tags']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            logger.error(f"缺少以下表: {', '.join(missing_tables)}")
            return False
        else:
            logger.info(f"所有必要的表都存在: {', '.join(tables)}")
            return True
    except Exception as e:
        logger.error(f"表存在性测试失败: {e}")
        return False

def test_book_dao():
    """测试BookDAO功能"""
    try:
        book_dao = BookDAO()
        books = book_dao.get_all()
        logger.info(f"书籍总数: {len(books)}")
        
        # 如果有书籍，测试获取单本书籍
        if books:
            book_id = books[0]['id']
            book = book_dao.get_by_id(book_id)
            if book:
                logger.info(f"成功获取书籍: {book['title']}")
            else:
                logger.error(f"无法获取书籍ID: {book_id}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"BookDAO测试失败: {e}")
        return False

def test_movie_dao():
    """测试MovieDAO功能"""
    try:
        movie_dao = MovieDAO()
        movies = movie_dao.get_all()
        logger.info(f"电影总数: {len(movies)}")
        
        # 如果有电影，测试获取单部电影
        if movies:
            movie_id = movies[0]['id']
            movie = movie_dao.get_by_id(movie_id)
            if movie:
                logger.info(f"成功获取电影: {movie['title']}")
            else:
                logger.error(f"无法获取电影ID: {movie_id}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"MovieDAO测试失败: {e}")
        return False

def test_music_dao():
    """测试MusicDAO功能"""
    try:
        music_dao = MusicDAO()
        music_items = music_dao.get_all()
        logger.info(f"音乐总数: {len(music_items)}")
        
        # 如果有音乐，测试获取单个音乐
        if music_items:
            music_id = music_items[0]['id']
            music = music_dao.get_by_id(music_id)
            if music:
                logger.info(f"成功获取音乐: {music['title']}")
            else:
                logger.error(f"无法获取音乐ID: {music_id}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"MusicDAO测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("=== SQLite数据库功能测试 ===")
    
    # 测试数据库连接
    logger.info("测试数据库连接...")
    if not test_database_connection():
        return 1
    
    # 测试表是否存在
    logger.info("测试表是否存在...")
    if not test_tables_exist():
        return 1
    
    # 测试DAO功能
    logger.info("测试BookDAO功能...")
    if not test_book_dao():
        return 1
    
    logger.info("测试MovieDAO功能...")
    if not test_movie_dao():
        return 1
    
    logger.info("测试MusicDAO功能...")
    if not test_music_dao():
        return 1
    
    logger.info("所有测试通过!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 