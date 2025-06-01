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
        # 创建一个新的数据字典，只包含数据库表中存在的字段
        filtered_book_data = {}
        
        # 基本字段
        filtered_book_data['id'] = str(uuid.uuid4())
        filtered_book_data['created_at'] = datetime.now().isoformat()
        filtered_book_data['updated_at'] = datetime.now().isoformat()
        
        # 复制标准字段
        standard_fields = ['title', 'author', 'publisher', 'isbn', 'status', 'notes', 
                          'cover_url', 'description', 'is_owned', 'series', 'translator', 
                          'price', 'rating']
        
        for field in standard_fields:
            if field in book_data:
                filtered_book_data[field] = book_data[field]
        
        # 处理出版日期字段
        if 'publish_date' in book_data:
            filtered_book_data['publish_date'] = book_data['publish_date']
            logger.info(f"设置出版日期(publish_date): {filtered_book_data['publish_date']}")
        elif 'datePublished' in book_data:
            filtered_book_data['publish_date'] = book_data['datePublished']
            logger.info(f"从datePublished设置出版日期: {filtered_book_data['publish_date']}")
        
        # 处理标签
        if 'tags' in book_data:
            if isinstance(book_data['tags'], list):
                filtered_book_data['tags'] = ','.join(book_data['tags'])
            else:
                filtered_book_data['tags'] = book_data['tags']
        
        # 处理myTags字段
        if 'myTags' in book_data and book_data['myTags']:
            if isinstance(book_data['myTags'], list):
                tags = book_data['myTags']
            else:
                tags = book_data['myTags'].split(',')
            
            # 如果已有tags，添加myTags
            if 'tags' in filtered_book_data and filtered_book_data['tags']:
                existing_tags = filtered_book_data['tags'].split(',')
                for tag in tags:
                    if tag.strip() and tag.strip() not in existing_tags:
                        existing_tags.append(tag.strip())
                filtered_book_data['tags'] = ','.join(existing_tags)
            else:
                filtered_book_data['tags'] = ','.join(tags)
        
        # 处理状态
        if 'state' in book_data and book_data['state'] and 'status' not in filtered_book_data:
            filtered_book_data['status'] = book_data['state']
        
        # 处理评分
        if 'myRating' in book_data and 'rating' not in filtered_book_data:
            filtered_book_data['rating'] = float(book_data['myRating'])
        
        # 处理页数
        if 'totalPage' in book_data and book_data['totalPage']:
            try:
                filtered_book_data['page_count'] = int(book_data['totalPage'])
            except (ValueError, TypeError):
                # 如果转换失败，尝试提取数字部分
                import re
                match = re.search(r'\d+', str(book_data['totalPage']))
                if match:
                    filtered_book_data['page_count'] = int(match.group())
        elif 'pages' in book_data and book_data['pages']:
            try:
                filtered_book_data['page_count'] = int(book_data['pages'])
                logger.info(f"从pages设置页数: {filtered_book_data['page_count']}")
            except (ValueError, TypeError):
                logger.warning(f"页数转换失败: {book_data['pages']}")
        
        # 处理描述
        if 'desc' in book_data and 'description' not in filtered_book_data:
            filtered_book_data['description'] = book_data['desc']
        
        # 记录最终要保存的数据
        logger.info(f"最终要保存到数据库的图书数据: {filtered_book_data}")
        
        success = book_dao.create(filtered_book_data)
        return filtered_book_data['id'] if success else None
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
        
        # 处理myTags字段
        if 'myTags' in book_data and isinstance(book_data['myTags'], list):
            book_data['myTags'] = ','.join(book_data['myTags'])
        
        # 兼容性处理：将新格式映射到旧格式
        if 'state' in book_data and 'status' not in book_data:
            book_data['status'] = book_data['state']
        
        # 确保中文状态值被正确保存
        if 'status' in book_data:
            # 打印状态值，帮助调试
            logger.info(f"保存书籍状态: {book_data['status']}")
            # 保持中文状态值不变，不再转换为英文
            pass
        
        if 'myRating' in book_data and 'rating' not in book_data:
            book_data['rating'] = book_data['myRating']
        
        if 'datePublished' in book_data and 'publish_date' not in book_data:
            book_data['publish_date'] = book_data['datePublished']
        
        if 'totalPage' in book_data and 'page_count' not in book_data:
            book_data['page_count'] = book_data['totalPage']
        
        if 'desc' in book_data and 'description' not in book_data:
            book_data['description'] = book_data['desc']
        
        # 调用数据库更新操作
        result = book_dao.update(book_id, book_data)
        # 打印更新结果，帮助调试
        logger.info(f"更新书籍结果: {result}")
        return result
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
        if 'tags' in movie_data and isinstance(movie_data['tags'], str):
            # 如果tags是字符串，确保它是逗号分隔的
            tags = movie_data['tags'].split(',') if movie_data['tags'] else []
            movie_data['tags'] = ','.join([tag.strip() for tag in tags if tag.strip()])
        elif 'tags' in movie_data and isinstance(movie_data['tags'], list):
            movie_data['tags'] = ','.join(movie_data['tags'])
        
        # 记录状态值，帮助调试
        if 'status' in movie_data:
            logger.info(f"电影状态值: {movie_data['status']}")
        else:
            logger.warning("电影数据中缺少状态字段")
            movie_data['status'] = '未看'  # 设置默认状态
        
        # 处理中文状态值
        if movie_data.get('status') == '看过':
            movie_data['status'] = 'watched'
        elif movie_data.get('status') == '在看':
            movie_data['status'] = 'watching'
        elif movie_data.get('status') == '想看':
            movie_data['status'] = 'wanting'
        elif movie_data.get('status') == '未看':
            movie_data['status'] = 'unwatched'
        elif movie_data.get('status') not in ['watched', 'watching', 'unwatched', 'wanting']:
            # 如果不是已知的英文状态，则设置默认值
            logger.info(f"将未知电影状态 '{movie_data.get('status')}' 设置为 'unwatched'")
            movie_data['status'] = 'unwatched'
        
        # 记录评分值，帮助调试
        if 'rating' in movie_data:
            logger.info(f"电影评分值: {movie_data['rating']}")
        
        # 移除不存在于数据库表中的字段
        valid_fields = ['id', 'title', 'director', 'cast', 'year', 'genre', 'status', 
                        'rating', 'notes', 'poster_url', 'tags', 'created_at', 'updated_at']
        movie_data_copy = movie_data.copy()
        for key in movie_data_copy:
            if key not in valid_fields:
                logger.info(f"从电影数据中移除非数据库字段: {key}")
                del movie_data[key]
        
        # 记录详细信息
        logger.info(f"准备添加电影: {movie_data}")
        
        success = movie_dao.create(movie_data)
        if success:
            logger.info(f"成功添加电影 ID={movie_id}")
            return movie_id
        else:
            logger.error(f"添加电影失败，数据库操作未成功")
            return None
    except Exception as e:
        logger.error(f"添加电影失败: {e}", exc_info=True)
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
        if 'tags' in music_data and isinstance(music_data['tags'], str):
            # 如果tags是字符串，确保它是逗号分隔的，且没有空格
            if music_data['tags']:
                # 先分割标签
                tags = music_data['tags'].replace(", ", ",").split(',')
                # 去除每个标签前后空格，并过滤空标签
                clean_tags = [tag.strip() for tag in tags if tag.strip()]
                # 重新组合成逗号分隔的字符串，不带空格
                music_data['tags'] = ','.join(clean_tags)
        elif 'tags' in music_data and isinstance(music_data['tags'], list):
            # 如果是列表，确保每个元素都没有前后空格
            clean_tags = [tag.strip() for tag in music_data['tags'] if tag.strip()]
            music_data['tags'] = ','.join(clean_tags)
        
        # 同样处理genre字段，确保与tags保持一致的格式
        if 'genre' in music_data and isinstance(music_data['genre'], str):
            if music_data['genre']:
                # 处理genre字符串，确保没有空格
                genre = music_data['genre'].replace(", ", ",").split(',')
                clean_genre = [g.strip() for g in genre if g.strip()]
                music_data['genre'] = ','.join(clean_genre)
        
        # 确保有title字段
        if 'album' in music_data and not music_data.get('title'):
            music_data['title'] = music_data['album']
        
        # 记录状态值，帮助调试
        if 'status' in music_data:
            logger.info(f"音乐状态值: {music_data['status']}")
        else:
            logger.warning("音乐数据中缺少状态字段")
            music_data['status'] = '未听'  # 设置默认状态
        
        # 处理中文状态值
        if music_data.get('status') == '听过':
            music_data['status'] = 'listened'
        elif music_data.get('status') == '在听':
            music_data['status'] = 'listening'
        elif music_data.get('status') == '想听':
            music_data['status'] = 'wanting'
        elif music_data.get('status') == '未听':
            music_data['status'] = 'unlistened'
        elif music_data.get('status') not in ['listened', 'listening', 'unlistened', 'wanting']:
            # 如果不是已知的英文状态，则设置默认值
            logger.info(f"将未知音乐状态 '{music_data.get('status')}' 设置为 'unlistened'")
            music_data['status'] = 'unlistened'
        
        # 记录评分值，帮助调试
        if 'rating' in music_data:
            logger.info(f"音乐评分值: {music_data['rating']}")
        
        # 移除不存在于数据库表中的字段
        valid_fields = ['id', 'title', 'artist', 'album', 'year', 'genre', 'status', 
                        'rating', 'notes', 'cover_url', 'tags', 'created_at', 'updated_at']
        music_data_copy = music_data.copy()
        for key in music_data_copy:
            if key not in valid_fields:
                logger.info(f"从音乐数据中移除非数据库字段: {key}")
                del music_data[key]
        
        # 记录详细信息
        logger.info(f"准备添加音乐: {music_data}")
        
        success = music_dao.create(music_data)
        if success:
            logger.info(f"成功添加音乐 ID={music_id}")
            return music_id
        else:
            logger.error(f"添加音乐失败，数据库操作未成功")
            return None
    except Exception as e:
        logger.error(f"添加音乐失败: {e}", exc_info=True)
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