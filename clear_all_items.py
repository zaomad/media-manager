#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_connection
from app.dao.book_dao import BookDAO
from app.dao.movie_dao import MovieDAO
from app.dao.music_dao import MusicDAO

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_all_items():
    """清空所有图书、电影和音乐条目"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取清空前的数量
        cursor.execute('SELECT COUNT(*) as count FROM books')
        books_count_before = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM movies')
        movies_count_before = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM music')
        music_count_before = cursor.fetchone()['count']
        
        total_before = books_count_before + movies_count_before + music_count_before
        
        logger.info(f"清空前的条目数量:")
        logger.info(f"- 图书: {books_count_before}")
        logger.info(f"- 电影: {movies_count_before}")
        logger.info(f"- 音乐: {music_count_before}")
        logger.info(f"- 总计: {total_before}")
        
        # 清空item_tags表中的相关记录
        cursor.execute('DELETE FROM item_tags WHERE item_type IN ("book", "movie", "music")')
        item_tags_deleted = cursor.rowcount
        logger.info(f"已删除 {item_tags_deleted} 条标签关联记录")
        
        # 清空三个主表
        cursor.execute('DELETE FROM books')
        books_deleted = cursor.rowcount
        logger.info(f"已删除 {books_deleted} 条图书记录")
        
        cursor.execute('DELETE FROM movies')
        movies_deleted = cursor.rowcount
        logger.info(f"已删除 {movies_deleted} 条电影记录")
        
        cursor.execute('DELETE FROM music')
        music_deleted = cursor.rowcount
        logger.info(f"已删除 {music_deleted} 条音乐记录")
        
        # 获取清空后的数量
        cursor.execute('SELECT COUNT(*) as count FROM books')
        books_count_after = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM movies')
        movies_count_after = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM music')
        music_count_after = cursor.fetchone()['count']
        
        total_after = books_count_after + movies_count_after + music_count_after
        
        # 提交事务
        conn.commit()
        
        logger.info(f"清空后的条目数量:")
        logger.info(f"- 图书: {books_count_after}")
        logger.info(f"- 电影: {movies_count_after}")
        logger.info(f"- 音乐: {music_count_after}")
        logger.info(f"- 总计: {total_after}")
        
        return {
            'success': True,
            'before': {
                'books': books_count_before,
                'movies': movies_count_before,
                'music': music_count_before,
                'total': total_before
            },
            'after': {
                'books': books_count_after,
                'movies': movies_count_after,
                'music': music_count_after,
                'total': total_after
            }
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"清空条目失败: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

if __name__ == "__main__":
    print("准备清空所有图书、电影和音乐条目...")
    confirm = input("此操作将删除所有条目数据且无法恢复，是否继续？(y/n): ")
    
    if confirm.lower() == 'y':
        result = clear_all_items()
        if result['success']:
            print("\n清空操作成功完成!")
            print(f"删除前总条目数: {result['before']['total']}")
            print(f"- 图书: {result['before']['books']}")
            print(f"- 电影: {result['before']['movies']}")
            print(f"- 音乐: {result['before']['music']}")
            print(f"\n删除后总条目数: {result['after']['total']}")
        else:
            print(f"\n清空操作失败: {result.get('error', '未知错误')}")
    else:
        print("操作已取消") 