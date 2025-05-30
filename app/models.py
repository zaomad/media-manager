import uuid
import logging
from datetime import datetime
from app.dao.book_dao import BookDAO
from app.dao.movie_dao import MovieDAO
from app.dao.music_dao import MusicDAO

# 设置日志
logger = logging.getLogger(__name__)

# 初始化数据访问对象
book_dao = BookDAO()
movie_dao = MovieDAO()
music_dao = MusicDAO()

# 书籍相关函数
def get_all_books():
    """获取所有书籍"""
    try:
        return book_dao.get_all()
    except Exception as e:
        logger.error(f"获取所有书籍失败: {e}")
        return []

def get_book(book_id):
    """通过ID获取特定书籍"""
    try:
        return book_dao.get_by_id(book_id)
    except Exception as e:
        logger.error(f"获取书籍(ID={book_id})失败: {e}")
        return None

def add_book(book_data):
    """添加新书籍"""
    try:
        book_id = str(uuid.uuid4())
        book_data['id'] = book_id
        book_data['created_at'] = datetime.now().isoformat()
        book_data['updated_at'] = datetime.now().isoformat()
        
        # 处理标签
        if 'tags' in book_data and isinstance(book_data['tags'], list):
            book_data['tags'] = ','.join(book_data['tags'])
        
        success = book_dao.create(book_data)
        return book_id if success else None
    except Exception as e:
        logger.error(f"添加书籍失败: {e}")
        return None

def update_book(book_id, book_data):
    """更新书籍信息"""
    try:
        # 确保ID不被更改
        book_data['id'] = book_id
        book_data['updated_at'] = datetime.now().isoformat()
        
        # 处理标签
        if 'tags' in book_data and isinstance(book_data['tags'], list):
            book_data['tags'] = ','.join(book_data['tags'])
        
        return book_dao.update(book_id, book_data)
    except Exception as e:
        logger.error(f"更新书籍(ID={book_id})失败: {e}")
        return False

def delete_book(book_id):
    """删除书籍"""
    try:
        return book_dao.delete(book_id)
    except Exception as e:
        logger.error(f"删除书籍(ID={book_id})失败: {e}")
        return False

def search_books(query):
    """搜索书籍"""
    try:
        return book_dao.search_books(query)
    except Exception as e:
        logger.error(f"搜索书籍失败: {e}")
        return []

def get_books_by_tag(tag):
    """根据标签获取书籍"""
    try:
        return book_dao.get_books_by_tag(tag)
    except Exception as e:
        logger.error(f"获取标签为'{tag}'的书籍失败: {e}")
        return []

def get_books_by_status(status):
    """根据状态获取书籍"""
    try:
        return book_dao.get_books_by_status(status)
    except Exception as e:
        logger.error(f"获取状态为'{status}'的书籍失败: {e}")
        return []

def get_book_tags():
    """获取所有书籍标签"""
    try:
        return book_dao.get_all_tags()
    except Exception as e:
        logger.error(f"获取所有书籍标签失败: {e}")
        return []

# 电影相关函数
def get_all_movies():
    """获取所有电影"""
    try:
        return movie_dao.get_all()
    except Exception as e:
        logger.error(f"获取所有电影失败: {e}")
        return []

def get_movie(movie_id):
    """通过ID获取特定电影"""
    try:
        return movie_dao.get_by_id(movie_id)
    except Exception as e:
        logger.error(f"获取电影(ID={movie_id})失败: {e}")
        return None

def add_movie(movie_data):
    """添加新电影"""
    try:
        movie_id = str(uuid.uuid4())
        movie_data['id'] = movie_id
        movie_data['created_at'] = datetime.now().isoformat()
        movie_data['updated_at'] = datetime.now().isoformat()
        
        # 处理标签
        if 'tags' in movie_data and isinstance(movie_data['tags'], list):
            movie_data['tags'] = ','.join(movie_data['tags'])
        
        success = movie_dao.create(movie_data)
        return movie_id if success else None
    except Exception as e:
        logger.error(f"添加电影失败: {e}")
        return None

def update_movie(movie_id, movie_data):
    """更新电影信息"""
    try:
        # 确保ID不被更改
        movie_data['id'] = movie_id
        movie_data['updated_at'] = datetime.now().isoformat()
        
        # 处理标签
        if 'tags' in movie_data and isinstance(movie_data['tags'], list):
            movie_data['tags'] = ','.join(movie_data['tags'])
        
        return movie_dao.update(movie_id, movie_data)
    except Exception as e:
        logger.error(f"更新电影(ID={movie_id})失败: {e}")
        return False

def delete_movie(movie_id):
    """删除电影"""
    try:
        return movie_dao.delete(movie_id)
    except Exception as e:
        logger.error(f"删除电影(ID={movie_id})失败: {e}")
        return False

def search_movies(query):
    """搜索电影"""
    try:
        return movie_dao.search_movies(query)
    except Exception as e:
        logger.error(f"搜索电影失败: {e}")
        return []

def get_movies_by_tag(tag):
    """根据标签获取电影"""
    try:
        return movie_dao.get_movies_by_tag(tag)
    except Exception as e:
        logger.error(f"获取标签为'{tag}'的电影失败: {e}")
        return []

def get_movies_by_status(status):
    """根据状态获取电影"""
    try:
        return movie_dao.get_movies_by_status(status)
    except Exception as e:
        logger.error(f"获取状态为'{status}'的电影失败: {e}")
        return []

def get_movie_tags():
    """获取所有电影标签"""
    try:
        return movie_dao.get_all_tags()
    except Exception as e:
        logger.error(f"获取所有电影标签失败: {e}")
        return []

# 音乐相关函数
def get_all_music():
    """获取所有音乐"""
    try:
        return music_dao.get_all()
    except Exception as e:
        logger.error(f"获取所有音乐失败: {e}")
        return []

def get_music(music_id):
    """通过ID获取特定音乐"""
    try:
        return music_dao.get_by_id(music_id)
    except Exception as e:
        logger.error(f"获取音乐(ID={music_id})失败: {e}")
        return None

def add_music(music_data):
    """添加新音乐"""
    try:
        music_id = str(uuid.uuid4())
        music_data['id'] = music_id
        music_data['created_at'] = datetime.now().isoformat()
        music_data['updated_at'] = datetime.now().isoformat()
        
        # 处理标签
        if 'tags' in music_data and isinstance(music_data['tags'], list):
            music_data['tags'] = ','.join(music_data['tags'])
        
        # 确保有title字段
        if 'album' in music_data and not music_data.get('title'):
            music_data['title'] = music_data['album']
        
        success = music_dao.create(music_data)
        return music_id if success else None
    except Exception as e:
        logger.error(f"添加音乐失败: {e}")
        return None

def update_music(music_id, music_data):
    """更新音乐信息"""
    try:
        # 确保ID不被更改
        music_data['id'] = music_id
        music_data['updated_at'] = datetime.now().isoformat()
        
        # 处理标签
        if 'tags' in music_data and isinstance(music_data['tags'], list):
            music_data['tags'] = ','.join(music_data['tags'])
        
        # 确保有title字段
        if 'album' in music_data and not music_data.get('title'):
            music_data['title'] = music_data['album']
        
        return music_dao.update(music_id, music_data)
    except Exception as e:
        logger.error(f"更新音乐(ID={music_id})失败: {e}")
        return False

def delete_music(music_id):
    """删除音乐"""
    try:
        return music_dao.delete(music_id)
    except Exception as e:
        logger.error(f"删除音乐(ID={music_id})失败: {e}")
        return False

def search_music(query):
    """搜索音乐"""
    try:
        return music_dao.search_music(query)
    except Exception as e:
        logger.error(f"搜索音乐失败: {e}")
        return []

def get_music_by_tag(tag):
    """根据标签获取音乐"""
    try:
        return music_dao.get_music_by_tag(tag)
    except Exception as e:
        logger.error(f"获取标签为'{tag}'的音乐失败: {e}")
        return []

def get_music_by_artist(artist):
    """根据艺术家获取音乐"""
    try:
        return music_dao.get_music_by_artist(artist)
    except Exception as e:
        logger.error(f"获取艺术家为'{artist}'的音乐失败: {e}")
        return []

def get_music_by_album(album):
    """根据专辑获取音乐"""
    try:
        return music_dao.get_music_by_album(album)
    except Exception as e:
        logger.error(f"获取专辑为'{album}'的音乐失败: {e}")
        return []

def get_music_tags():
    """获取所有音乐标签"""
    try:
        return music_dao.get_all_tags()
    except Exception as e:
        logger.error(f"获取所有音乐标签失败: {e}")
        return []

def get_music_artists():
    """获取所有艺术家"""
    try:
        return music_dao.get_all_artists()
    except Exception as e:
        logger.error(f"获取所有艺术家失败: {e}")
        return []

def get_music_albums():
    """获取所有专辑"""
    try:
        return music_dao.get_all_albums()
    except Exception as e:
        logger.error(f"获取所有专辑失败: {e}")
        return [] 