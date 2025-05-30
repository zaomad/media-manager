import logging
from app.dao.base_dao import BaseDAO
from app.database import get_db_connection

logger = logging.getLogger(__name__)

class MovieDAO(BaseDAO):
    """电影数据访问对象"""
    
    def __init__(self):
        super().__init__('movies')
    
    def search_movies(self, query):
        """搜索电影"""
        search_fields = ['title', 'director', 'genre', 'notes', 'tags']
        return self.search(query, search_fields)
    
    def get_movies_by_tag(self, tag):
        """根据标签获取电影"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT m.* FROM movies m
            JOIN item_tags it ON m.id = it.item_id
            JOIN tags t ON it.tag_id = t.id
            WHERE t.name = ? AND it.item_type = 'movie'
            ''', (tag,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取标签为'{tag}'的电影失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_movies_by_status(self, status):
        """根据状态获取电影"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM movies WHERE status = ?', (status,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取状态为'{status}'的电影失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_tags(self):
        """获取所有电影标签"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT DISTINCT t.name, COUNT(it.item_id) as count
            FROM tags t
            JOIN item_tags it ON t.id = it.tag_id
            WHERE it.item_type = 'movie'
            GROUP BY t.name
            ORDER BY count DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取所有电影标签失败: {e}")
            return []
        finally:
            conn.close()
    
    def add_tag_to_movie(self, movie_id, tag_name):
        """为电影添加标签"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 确保标签存在
            tag_id = tag_name.lower().replace(' ', '_')
            cursor.execute('INSERT OR IGNORE INTO tags (id, name, type) VALUES (?, ?, ?)', 
                         (tag_id, tag_name, 'movie'))
            
            # 添加关联
            cursor.execute('''
            INSERT OR IGNORE INTO item_tags (item_id, tag_id, item_type)
            VALUES (?, ?, ?)
            ''', (movie_id, tag_id, 'movie'))
            
            # 更新电影的tags字段
            cursor.execute('SELECT tags FROM movies WHERE id = ?', (movie_id,))
            result = cursor.fetchone()
            if result:
                current_tags = result['tags'].split(',') if result['tags'] else []
                if tag_name not in current_tags:
                    current_tags.append(tag_name)
                    new_tags = ','.join(current_tags)
                    cursor.execute('UPDATE movies SET tags = ? WHERE id = ?', (new_tags, movie_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"为电影(ID={movie_id})添加标签'{tag_name}'失败: {e}")
            return False
        finally:
            conn.close()
    
    def remove_tag_from_movie(self, movie_id, tag_name):
        """从电影移除标签"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 获取标签ID
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
            result = cursor.fetchone()
            if not result:
                return False
                
            tag_id = result['id']
            
            # 移除关联
            cursor.execute('''
            DELETE FROM item_tags 
            WHERE item_id = ? AND tag_id = ? AND item_type = 'movie'
            ''', (movie_id, tag_id))
            
            # 更新电影的tags字段
            cursor.execute('SELECT tags FROM movies WHERE id = ?', (movie_id,))
            result = cursor.fetchone()
            if result and result['tags']:
                current_tags = result['tags'].split(',')
                if tag_name in current_tags:
                    current_tags.remove(tag_name)
                    new_tags = ','.join(current_tags)
                    cursor.execute('UPDATE movies SET tags = ? WHERE id = ?', (new_tags, movie_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"从电影(ID={movie_id})移除标签'{tag_name}'失败: {e}")
            return False
        finally:
            conn.close() 