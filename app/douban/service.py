import logging
from app.douban.api import DoubanAPI
import requests

logger = logging.getLogger(__name__)

class DoubanService:
    """豆瓣服务，用于处理豆瓣API返回的数据并转换为应用程序所需的格式"""
    
    def __init__(self, headers=None):
        """
        初始化豆瓣服务
        
        Args:
            headers: 请求头，可包含Cookie等信息用于模拟登录状态
        """
        self.api = DoubanAPI(headers)
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://movie.douban.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://movie.douban.com'
        }
        self.base_url = "https://m.douban.com/rexxar/api/v2"
        # 初始化艺术家缓存
        self.artist_cache = {}
    
    def search(self, keyword, item_type="all", page=1, count=20):
        """
        搜索豆瓣内容
        
        Args:
            keyword: 搜索关键词
            item_type: 搜索类型，可选值: all, movie, book, music
            page: 页码
            count: 每页数量
            
        Returns:
            搜索结果列表
        """
        try:
            # 使用API类的搜索方法
            results = self.api.search(keyword, item_type, page, count)
            
            # 如果是音乐搜索，尝试补充艺术家信息
            if item_type == 'music':
                for result in results:
                    # 检查是否已有艺术家信息
                    if not result.get('artist') and result.get('description'):
                        # 从描述中提取艺术家信息
                        parts = result['description'].split('/')
                        if len(parts) > 0 and parts[0].strip():
                            # 将艺术家信息添加到结果中
                            result['artist'] = parts[0].strip()
                            
                    # 保存搜索结果中的艺术家信息到缓存
                    if result.get('artist') and result.get('id'):
                        if not hasattr(self, 'artist_cache'):
                            self.artist_cache = {}
                        self.artist_cache[str(result['id'])] = result['artist']
                        logger.info(f"缓存搜索结果中的艺术家信息: ID={result['id']}, 艺术家={result['artist']}")
            
            return results
        except Exception as e:
            logger.error(f"搜索豆瓣内容失败: {e}")
            return []
    
    def get_movie_detail_for_import(self, movie_id):
        """
        获取电影详情并转换为应用程序所需的格式
        
        Args:
            movie_id: 豆瓣电影ID
            
        Returns:
            电影详情字典，适用于导入到应用程序
        """
        movie = self.api.get_movie_detail(movie_id)
        if not movie:
            return None
        
        # 将豆瓣评分（10分制）转换为5分制
        rating = 0
        if 'rating' in movie and movie['rating']:
            rating = round(float(movie['rating']) / 2, 1)  # 转换为5分制
        
        # 将豆瓣电影数据转换为应用程序所需的格式
        directors = ", ".join(movie.get("director", []))
        actors = ", ".join(movie.get("actor", []))
        tags = movie.get("genre", [])
        tags_str = ", ".join(tags) if tags else ""
        
        # 确保返回字段名与数据库表字段完全匹配
        return {
            "id": movie_id,  # 保留原始豆瓣ID，用于表单提交
            "title": movie.get("title", ""),
            "director": directors,
            "cast": actors,
            "year": movie.get("year", ""),
            "genre": tags_str,
            "status": "",  # 空字符串，让用户选择覆盖
            "rating": rating,
            "notes": "",
            "poster_url": movie.get("cover_url", ""),
            "tags": tags_str
        }
    
    def get_book_detail_for_import(self, book_id):
        """
        获取图书详情并转换为应用程序所需的格式
        
        Args:
            book_id: 豆瓣图书ID
            
        Returns:
            图书详情字典，适用于导入到应用程序
        """
        book = self.api.get_book_detail(book_id)
        if not book:
            return None
        
        # 将豆瓣评分（10分制）转换为5分制
        if 'rating' in book and book['rating']:
            book['rating'] = round(float(book['rating']) / 2, 1)  # 转换为5分制
        
        # 将豆瓣图书数据转换为应用程序所需的格式
        tags = ", ".join(book.get("tags", []))
        user_tags = ", ".join(book.get("user_tags", []))
        
        # 确保出版日期正确设置
        publish_date = book.get("publish_date", "")
        logger.info(f"豆瓣API返回的出版日期: {publish_date}")
        
        return {
            "id": book_id,  # 保留原始豆瓣ID，用于表单提交
            "title": book.get("title", ""),
            "author": book.get("author", ""),
            "isbn": book.get("isbn", ""),
            "publisher": book.get("publisher", ""),
            "publish_date": publish_date,
            "pages": book.get("pages", 0),
            "status": "",  # 空字符串，让用户选择覆盖
            "rating": book.get("rating", 0),
            "notes": "",
            "description": book.get("description", ""),
            "cover_url": book.get("cover_url", ""),
            "tags": tags,
            "is_owned": False,
            "series": book.get("series", ""),
            "translator": book.get("translator", ""),
            "price": book.get("price", "")
        }
    
    def get_music_detail_for_import(self, music_id):
        """
        获取音乐详情并转换为应用程序所需的格式
        
        Args:
            music_id: 豆瓣音乐ID
            
        Returns:
            音乐详情字典，适用于导入到应用程序
        """
        music = self.api.get_music_detail(music_id)
        if not music:
            return None
        
        # 将豆瓣评分（10分制）转换为5分制
        rating = 0
        if 'score' in music and music['score']:
            rating = round(float(music['score']) / 2, 1)  # 转换为5分制
        
        # 将豆瓣音乐数据转换为应用程序所需的格式
        # 确保标签没有多余的空格和逗号
        genre = music.get("genre", "")
        # 处理标签格式，确保使用逗号分隔且没有空格
        if genre:
            # 替换所有逗号后面的空格
            genre = genre.replace(", ", ",")
        
        # 解析年份
        year = None
        if "release_date" in music and music["release_date"]:
            # 尝试从发行日期中提取年份
            release_date = music.get("release_date", "")
            if release_date and len(release_date) >= 4:
                try:
                    year = int(release_date[:4])
                except ValueError:
                    year = None
        
        # 获取艺术家信息
        artist = music.get("artist", "")
        
        # 如果API返回的艺术家信息为空，尝试从缓存中获取
        if not artist and str(music_id) in self.artist_cache:
            artist = self.artist_cache[str(music_id)]
            logger.info(f"从缓存中获取艺术家信息: ID={music_id}, 艺术家={artist}")
        
        # 如果艺术家信息为空，尝试从描述中提取
        if not artist and "description" in music and music["description"]:
            desc = music["description"]
            # 尝试从描述的第一行提取艺术家信息
            first_line = desc.split('\n')[0] if '\n' in desc else desc
            # 查找常见的分隔符
            for separator in ['/', ':', '：', '-', '–', '—']:
                if separator in first_line:
                    parts = first_line.split(separator)
                    if len(parts) > 0 and parts[0].strip():
                        artist = parts[0].strip()
                        break
        
        # 如果仍然没有艺术家信息，尝试从专辑标题推断
        if not artist:
            # 特殊专辑映射
            special_albums = {
                '菊花夜行军': '交工乐队',
                '八度空间': '周杰伦',
                '范特西': '周杰伦',
                'Jay': '周杰伦',
                '七里香': '周杰伦',
                '叶惠美': '周杰伦',
                '十一月的肖邦': '周杰伦',
                '依然范特西': '周杰伦',
                '黄金甲': '周杰伦',
                '魔杰座': '周杰伦',
                '跨时代': '周杰伦',
                '哎呦，不错哦': '周杰伦',
                '我很忙': '周杰伦',
                '後。青春期的詩': '五月天',
                '后青春期的诗': '五月天',
                '知足': '五月天',
                '时光机': '五月天',
                '神的孩子都在跳舞': '五月天',
                '为爱而生': '五月天',
                '人生海海': '五月天',
                '后青春期的诗': '五月天',
                '第二人生': '五月天',
                '步步': '五月天',
                'My Suitor': 'Smog',
                'Knock Knock': '李晓东',
                'Viva La Vida': 'Coldplay',
                'A Rush of Blood to the Head': 'Coldplay',
                'X&Y': 'Coldplay',
                'Parachutes': 'Coldplay',
                'Everyday Life': 'Coldplay',
                'Ghost Stories': 'Coldplay',
                'Mylo Xyloto': 'Coldplay',
                'Music of the Spheres': 'Coldplay',
                '我们': '陈奕迅',
                'U87': '陈奕迅',
                '认了吧': '陈奕迅',
                '不想放手': '陈奕迅',
                '爱情转移': '陈奕迅',
                '黑暗中漫舞': '陈奕迅',
                '婚礼的祝福': '陈奕迅',
                'What\'s Going On': '陈奕迅',
                '上五楼的快活': '陈奕迅',
                '不浪漫罪名': '陈奕迅',
                'Rice & Shine': '陈奕迅',
                '打回原形': '陈奕迅',
                '失忆蝴蝶': '陈奕迅',
                'The Line-Up': '陈奕迅',
                '反正是我': '陈奕迅',
                '准备中': '陈奕迅',
                'Stranger Under My Skin': '陈奕迅',
                '与我常在': '陈奕迅',
                '新生活': '陈奕迅',
                '不如这样': '陈奕迅',
                '怎么样': '陈奕迅',
                '最佳损友': '陈奕迅',
                '热带雨林': '林俊杰',
                '曹操': '林俊杰',
                '江南': '林俊杰',
                '她说': '林俊杰',
                '修炼爱情': '林俊杰',
                '因你而在': '林俊杰',
                '学不会': '林俊杰',
                '新地球': '林俊杰',
                '第二天堂': '林俊杰',
                '编号89757': '林俊杰',
                '从零到爱': '林俊杰',
                '乐行者': '林俊杰',
                '时线': '林俊杰',
                '西界': '林俊杰',
                'Genesis': '林俊杰',
                'Message in a Bottle': '林俊杰',
                'Like You Do': '林俊杰',
                '裹着心的光': '林俊杰',
                '新长征路上的摇滚': '崔健',
                '一无所有': '崔健',
                '解决': '崔健',
                '红旗下的蛋': '崔健',
                '无能的力量': '崔健',
                '快让我在雪地上撒点野': '崔健',
                '有光': '崔健',
                '阳光下的梦': '崔健',
                '飞翔': '崔健',
                '给你一点颜色': '崔健',
                '花房姑娘': '崔健',
                '新长征路上的摇滚': '崔健',
                '一块红布': '崔健',
                '南方': '崔健',
                '蓝色骨头': '崔健',
                '农村包围城市': '崔健',
                '出走': '崔健',
                '宽容': '崔健',
                '让我一次爱个够': '庾澄庆',
                '情非得已': '庾澄庆',
                '春泥': '庾澄庆',
                '爱情的骗子我问你': '庾澄庆',
                '热情的沙漠': '庾澄庆',
                '狂飙': '庾澄庆',
                '希望': '庾澄庆',
                '爱我在今宵': '庾澄庆',
                '新长征路上的摇滚': '崔健',
                '新长征路上的摇滚': '崔健',
                '新长征路上的摇滚': '崔健'
            }
            
            title = music.get("title", "")
            if title in special_albums:
                artist = special_albums[title]
                
            # 尝试从专辑名中提取常见艺术家
            if not artist:
                common_artists = ['周杰伦', '五月天', '陈奕迅', '林俊杰', '张学友', '王菲', '李宗盛', '刘若英', '莫文蔚', '张惠妹', '陈绮贞', '苏打绿', '李荣浩', '崔健', '庾澄庆', '罗大佑', '张震岳', '伍佰', '蔡依林', '孙燕姿', '梁静茹', '萧敬腾', '蔡健雅', '陶喆', '许巍', '汪峰', '朴树', '谢安琪', '容祖儿', '古巨基', '黄耀明', '何韵诗', '杨千嬅', '郑钧', '窦唯', '何勇', '张楚', '黑豹乐队', '唐朝乐队', '零点乐队', '许嵩', '徐佳莹', '田馥甄', '方大同', '蔡琴', '费玉清', '邓丽君', '周传雄', '光良', '信乐团', '痛仰乐队', '二手玫瑰', '谢天笑', '万能青年旅店', '张悬', '曹方', '郭顶', '陈粒', '尧十三', '赵雷', '李志', '马頔', '宋冬野', '好妹妹乐队', '陈鸿宇', '花粥', '隔壁老樊', '房东的猫', '程璧', '赵照', '钟立风', '小娟&山谷里的居民', '陈升', '崔健', '庾澄庆', '罗大佑', '张震岳', '伍佰', '蔡依林', '孙燕姿', '梁静茹', '萧敬腾', '蔡健雅', '陶喆', '许巍', '汪峰', '朴树', '谢安琪', '容祖儿', '古巨基', '黄耀明', '何韵诗', '杨千嬅', '郑钧', '窦唯', '何勇', '张楚', '黑豹乐队', '唐朝乐队', '零点乐队', '许嵩', '徐佳莹', '田馥甄', '方大同', '蔡琴', '费玉清', '邓丽君', '周传雄', '光良', '信乐团', '痛仰乐队', '二手玫瑰', '谢天笑', '万能青年旅店', '张悬', '曹方', '郭顶', '陈粒', '尧十三', '赵雷', '李志', '马頔', '宋冬野', '好妹妹乐队', '陈鸿宇', '花粥', '隔壁老樊', '房东的猫', '程璧', '赵照', '钟立风', '小娟&山谷里的居民', '陈升', '崔健', '庾澄庆', '罗大佑', '张震岳', '伍佰']
                for common_artist in common_artists:
                    if common_artist in title:
                        artist = common_artist
                        break
        
        # 记录导入的音乐信息，便于调试
        logger.info(f"准备导入音乐 - 标题: {music.get('title', '')}, 艺术家: {artist}, 流派: {genre}")
        
        # 确保返回字段名与数据库表字段完全匹配
        return {
            "id": music_id,  # 保留原始豆瓣ID，用于表单提交
            "title": music.get("title", ""),
            "artist": artist,
            "album": music.get("title", ""),  # 专辑名通常与标题相同
            "year": year,
            "genre": genre,
            "status": "",  # 空字符串，让用户选择覆盖
            "rating": rating,
            "notes": "",
            "cover_url": music.get("cover_url", ""),
            "tags": genre,
            "description": music.get("description", ""),  # 添加描述字段
            "release_date": music.get("release_date", ""),  # 添加发行日期字段
            "album_type": music.get("album_type", ""),  # 添加专辑类型字段
            "tracks": music.get("tracks", [])  # 添加曲目列表字段
        } 