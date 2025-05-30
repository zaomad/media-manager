import logging
import sqlite3
from app.database import get_db_connection

logger = logging.getLogger(__name__)

class BaseDAO:
    """基础数据访问对象，提供通用的数据库操作方法"""
    
    def __init__(self, table_name):
        self.table_name = table_name
    
    def get_all(self):
        """获取所有记录"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {self.table_name}')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取所有{self.table_name}记录失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_by_id(self, id):
        """根据ID获取记录"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {self.table_name} WHERE id = ?', (id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取{self.table_name}记录(ID={id})失败: {e}")
            return None
        finally:
            conn.close()
    
    def create(self, data):
        """创建新记录"""
        if 'id' not in data:
            logger.error(f"创建{self.table_name}记录失败: 缺少ID字段")
            return False
            
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 动态构建SQL语句
            fields = list(data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            fields_str = ', '.join(fields)
            
            sql = f'INSERT INTO {self.table_name} ({fields_str}) VALUES ({placeholders})'
            cursor.execute(sql, tuple(data.values()))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"创建{self.table_name}记录失败: {e}")
            return False
        finally:
            conn.close()
    
    def update(self, id, data):
        """更新记录"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 动态构建SQL语句
            set_clause = ', '.join([f'{key} = ?' for key in data.keys()])
            values = list(data.values())
            values.append(id)  # 添加WHERE条件的参数
            
            sql = f'UPDATE {self.table_name} SET {set_clause} WHERE id = ?'
            cursor.execute(sql, tuple(values))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"更新{self.table_name}记录(ID={id})失败: {e}")
            return False
        finally:
            conn.close()
    
    def delete(self, id):
        """删除记录"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {self.table_name} WHERE id = ?', (id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"删除{self.table_name}记录(ID={id})失败: {e}")
            return False
        finally:
            conn.close()
    
    def search(self, query, fields=None):
        """搜索记录"""
        if not fields:
            logger.error(f"搜索{self.table_name}记录失败: 未指定搜索字段")
            return []
            
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 构建LIKE条件
            like_conditions = [f"{field} LIKE ?" for field in fields]
            where_clause = " OR ".join(like_conditions)
            
            # 为每个字段准备模糊匹配参数
            params = [f"%{query}%" for _ in fields]
            
            sql = f'SELECT * FROM {self.table_name} WHERE {where_clause}'
            cursor.execute(sql, tuple(params))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"搜索{self.table_name}记录失败: {e}")
            return []
        finally:
            conn.close()
    
    def count(self):
        """获取记录总数"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) as count FROM {self.table_name}')
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"获取{self.table_name}记录总数失败: {e}")
            return 0
        finally:
            conn.close() 