import json
import os
import uuid
from datetime import datetime

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.json')
MOVIES_FILE = os.path.join(DATA_DIR, 'movies.json')
MUSIC_FILE = os.path.join(DATA_DIR, 'music.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化数据文件
def init_data_file(file_path, initial_data=None):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump(initial_data or [], f)

init_data_file(BOOKS_FILE)
init_data_file(MOVIES_FILE)
init_data_file(MUSIC_FILE)

# 通用函数
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# 书籍相关函数
def get_all_books():
    """获取所有书籍"""
    if not os.path.exists(BOOKS_FILE):
        return []
    
    try:
        with open(BOOKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_books(books):
    """保存所有书籍数据"""
    with open(BOOKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=4)

def get_book(book_id):
    """通过ID获取特定书籍"""
    books = get_all_books()
    for book in books:
        if str(book.get('id')) == str(book_id):
            return book
    return None

def add_book(book_data):
    books = get_all_books()
    book_id = str(uuid.uuid4())
    book_data['id'] = book_id
    book_data['created_at'] = datetime.now().isoformat()
    book_data['updated_at'] = datetime.now().isoformat()
    books.append(book_data)
    save_books(books)
    return book_id

def update_book(book_id, book_data):
    books = get_all_books()
    for i, book in enumerate(books):
        if book.get('id') == book_id:
            book_data['updated_at'] = datetime.now().isoformat()
            books[i] = book_data
            save_books(books)
            return True
    return False

def delete_book(book_id):
    """删除书籍"""
    books = get_all_books()
    books = [book for book in books if str(book.get('id')) != str(book_id)]
    save_books(books)
    return True

# 电影相关函数
def get_all_movies():
    """获取所有电影"""
    if not os.path.exists(MOVIES_FILE):
        return []
    
    try:
        with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_movies(movies):
    """保存所有电影数据"""
    with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)

def get_movie(movie_id):
    """通过ID获取特定电影"""
    movies = get_all_movies()
    for movie in movies:
        if str(movie.get('id')) == str(movie_id):
            return movie
    return None

def add_movie(movie_data):
    movies = get_all_movies()
    movie_id = str(uuid.uuid4())
    movie_data['id'] = movie_id
    movie_data['created_at'] = datetime.now().isoformat()
    movie_data['updated_at'] = datetime.now().isoformat()
    movies.append(movie_data)
    save_movies(movies)
    return movie_id

def update_movie(movie_id, movie_data):
    movies = get_all_movies()
    for i, movie in enumerate(movies):
        if movie.get('id') == movie_id:
            movie_data['updated_at'] = datetime.now().isoformat()
            movies[i] = movie_data
            save_movies(movies)
            return True
    return False

def delete_movie(movie_id):
    """删除电影"""
    movies = get_all_movies()
    movies = [movie for movie in movies if str(movie.get('id')) != str(movie_id)]
    save_movies(movies)
    return True

# 音乐相关函数
def get_all_music():
    """获取所有音乐"""
    if not os.path.exists(MUSIC_FILE):
        return []
    
    try:
        with open(MUSIC_FILE, 'r', encoding='utf-8') as f:
            music_items = json.load(f)
            # 处理历史数据，将title迁移到album
            for item in music_items:
                # 如果有title但没有album，将title的值赋给album
                if 'title' in item and not item.get('album'):
                    item['album'] = item.pop('title')
                # 如果同时有title和album，保留album并删除title
                elif 'title' in item:
                    item.pop('title')
            return music_items
    except:
        return []

def save_music(music_items):
    """保存所有音乐数据"""
    # 确保没有title字段
    for item in music_items:
        if 'title' in item:
            # 如果没有album，则使用title的值
            if not item.get('album'):
                item['album'] = item.pop('title')
            else:
                # 否则直接删除title
                item.pop('title')
    
    with open(MUSIC_FILE, 'w', encoding='utf-8') as f:
        json.dump(music_items, f, ensure_ascii=False, indent=4)

def get_music(music_id):
    """通过ID获取特定音乐"""
    music_items = get_all_music()
    for music in music_items:
        if str(music.get('id')) == str(music_id):
            # 确保没有title字段
            if 'title' in music and not music.get('album'):
                music['album'] = music.pop('title')
            elif 'title' in music:
                music.pop('title')
            return music
    return None

def add_music(music_data):
    # 确保使用album而不是title
    if 'title' in music_data and not music_data.get('album'):
        music_data['album'] = music_data.pop('title')
    elif 'title' in music_data:
        music_data.pop('title')
        
    music_items = get_all_music()
    music_id = str(uuid.uuid4())
    music_data['id'] = music_id
    music_data['created_at'] = datetime.now().isoformat()
    music_data['updated_at'] = datetime.now().isoformat()
    music_items.append(music_data)
    save_music(music_items)
    return music_id

def update_music(music_id, music_data):
    # 确保使用album而不是title
    if 'title' in music_data and not music_data.get('album'):
        music_data['album'] = music_data.pop('title')
    elif 'title' in music_data:
        music_data.pop('title')
        
    music_items = get_all_music()
    for i, music in enumerate(music_items):
        if music.get('id') == music_id:
            music_data['updated_at'] = datetime.now().isoformat()
            music_items[i] = music_data
            save_music(music_items)
            return True
    return False

def delete_music(music_id):
    """删除音乐"""
    music_items = get_all_music()
    music_items = [music for music in music_items if str(music.get('id')) != str(music_id)]
    save_music(music_items)
    return True 