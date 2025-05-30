import logging
from app.dao.base_dao import BaseDAO
from app.database import get_db_connection

logger = logging.getLogger(__name__)

class MusicDAO(BaseDAO):
    """音乐数据访问对象"""
    
    def __init__(self):
        super().__init__('music')
    
    def search_music(self, query):
        """搜索音乐"""
        search_fields = ['title', 'artist', 'album', 'genre', 'notes', 'tags']
        return self.search(query, search_fields)
    
    def get_music_by_tag(self, tag):
        """根据标签获取音乐"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT m.* FROM music m
            JOIN item_tags it ON m.id = it.item_id
            JOIN tags t ON it.tag_id = t.id
            WHERE t.name = ? AND it.item_type = 'music'
            ''', (tag,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取标签为'{tag}'的音乐失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_music_by_artist(self, artist):
        """根据艺术家获取音乐"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM music WHERE artist LIKE ?', (f"%{artist}%",))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取艺术家为'{artist}'的音乐失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_music_by_album(self, album):
        """根据专辑获取音乐"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM music WHERE album LIKE ?', (f"%{album}%",))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取专辑为'{album}'的音乐失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_tags(self):
        """获取所有音乐标签"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT DISTINCT t.name, COUNT(it.item_id) as count
            FROM tags t
            JOIN item_tags it ON t.id = it.tag_id
            WHERE it.item_type = 'music'
            GROUP BY t.name
            ORDER BY count DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取所有音乐标签失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_artists(self):
        """获取所有艺术家"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT DISTINCT artist, COUNT(*) as count
            FROM music
            WHERE artist IS NOT NULL AND artist != ''
            GROUP BY artist
            ORDER BY count DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取所有艺术家失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_albums(self):
        """获取所有专辑"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT DISTINCT album, artist, COUNT(*) as count
            FROM music
            WHERE album IS NOT NULL AND album != ''
            GROUP BY album, artist
            ORDER BY count DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取所有专辑失败: {e}")
            return []
        finally:
            conn.close()
    
    def add_tag_to_music(self, music_id, tag_name):
        """为音乐添加标签"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 确保标签存在
            tag_id = tag_name.lower().replace(' ', '_')
            cursor.execute('INSERT OR IGNORE INTO tags (id, name, type) VALUES (?, ?, ?)', 
                         (tag_id, tag_name, 'music'))
            
            # 添加关联
            cursor.execute('''
            INSERT OR IGNORE INTO item_tags (item_id, tag_id, item_type)
            VALUES (?, ?, ?)
            ''', (music_id, tag_id, 'music'))
            
            # 更新音乐的tags字段
            cursor.execute('SELECT tags FROM music WHERE id = ?', (music_id,))
            result = cursor.fetchone()
            if result:
                current_tags = result['tags'].split(',') if result['tags'] else []
                if tag_name not in current_tags:
                    current_tags.append(tag_name)
                    new_tags = ','.join(current_tags)
                    cursor.execute('UPDATE music SET tags = ? WHERE id = ?', (new_tags, music_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"为音乐(ID={music_id})添加标签'{tag_name}'失败: {e}")
            return False
        finally:
            conn.close()
    
    def remove_tag_from_music(self, music_id, tag_name):
        """从音乐移除标签"""
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
            WHERE item_id = ? AND tag_id = ? AND item_type = 'music'
            ''', (music_id, tag_id))
            
            # 更新音乐的tags字段
            cursor.execute('SELECT tags FROM music WHERE id = ?', (music_id,))
            result = cursor.fetchone()
            if result and result['tags']:
                current_tags = result['tags'].split(',')
                if tag_name in current_tags:
                    current_tags.remove(tag_name)
                    new_tags = ','.join(current_tags)
                    cursor.execute('UPDATE music SET tags = ? WHERE id = ?', (new_tags, music_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"从音乐(ID={music_id})移除标签'{tag_name}'失败: {e}")
            return False
        finally:
            conn.close() 