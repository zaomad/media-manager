from flask import render_template, request, jsonify, redirect, url_for, flash, send_from_directory, abort
from app import app
from app.models import (get_all_books, get_book, add_book, update_book, delete_book,
                       get_all_movies, get_movie, add_movie, update_movie, delete_movie,
                       get_all_music, get_music, add_music, update_music, delete_music,
                       search_books, search_movies, search_music)
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import time
from app.utils import get_common_genres, get_image_url, format_date
# 导入豆瓣服务
from app.douban.service import DoubanService

# 初始化豆瓣服务
douban_service = DoubanService()

# 配置文件上传
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 创建上传目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 检查允许的文件扩展名
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 添加全局上下文处理器，为所有模板添加now变量
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# 添加全局上下文处理器，为所有模板添加get_image_url函数
@app.context_processor
def inject_image_url():
    return {'get_image_url': get_image_url}

# 添加全局上下文处理器，为所有模板添加format_date函数
@app.context_processor
def inject_format_date():
    return {'format_date': format_date}

# 页面路由
@app.route('/')
def index():
    recent_books = get_all_books()[:3]
    recent_movies = get_all_movies()[:3]
    recent_music = get_all_music()[:3]
    return render_template('index.html', 
                           recent_books=recent_books,
                           recent_movies=recent_movies,
                           recent_music=recent_music)

@app.route('/books')
def books():
    books = get_all_books()
    
    # 处理状态显示
    for book in books:
        # 打印原始状态值，帮助调试
        logger.info(f"图书页面 - 原始状态值: {book.get('status')}")
        
        # 将旧的状态值映射到新的状态值
        if book.get('status') == 'unread':
            book['status'] = '未读'
        elif book.get('status') == 'reading':
            book['status'] = '在读'
        elif book.get('status') == 'read':
            book['status'] = '读过'
        # 确保"想读"、"在读"和"读过"状态保持不变
        elif book.get('status') != '想读' and book.get('status') != '在读' and book.get('status') != '读过' and book.get('status') != '未读':
            # 如果状态不是已知的中文状态，则默认设为"未读"
            logger.info(f"图书页面 - 状态值不是已知的中文状态，设为未读: {book.get('status')}")
            book['status'] = '未读'
        
        # 打印处理后的状态值，帮助调试
        logger.info(f"图书页面 - 处理后状态值: {book.get('status')}")
    
    # 获取所有唯一的分类标签
    all_genres = set()
    for book in books:
        if book.get('tags'):
            genres = [tag.strip() for tag in book['tags'].split(',')]
            all_genres.update(genres)
    
    # 获取所有唯一的作者
    all_authors = set()
    for book in books:
        if book.get('author'):
            all_authors.add(book['author'])
    
    return render_template('books.html', books=books, genres=sorted(all_genres), authors=sorted(all_authors))

@app.route('/books/<string:book_id>')
def book_detail(book_id):
    book = get_book(book_id)
    if not book:
        abort(404)
    
    # 打印原始状态值，帮助调试
    logger.info(f"书籍详情页 - 原始状态值: {book.get('status')}")
    
    # 处理状态显示
    if book.get('status') == 'unread':
        book['status'] = '未读'
    elif book.get('status') == 'reading':
        book['status'] = '在读'
    elif book.get('status') == 'read':
        book['status'] = '读过'
    # 确保"想读"状态保持不变
    elif book.get('status') != '想读' and book.get('status') != '在读' and book.get('status') != '读过' and book.get('status') != '未读':
        # 如果状态不是已知的中文状态，则默认设为"未读"
        logger.info(f"书籍详情页 - 状态值不是已知的中文状态，设为未读: {book.get('status')}")
        book['status'] = '未读'
    
    # 打印处理后的状态值，帮助调试
    logger.info(f"书籍详情页 - 处理后状态值: {book.get('status')}")
    
    return render_template('book_detail.html', book=book)

@app.route('/books/add', methods=['GET', 'POST'])
def add_book_route():
    if request.method == 'POST':
        # Get the rating value from the form
        rating_value = request.form.get('rating', '')
        # 确保评分值是浮点数
        try:
            rating = float(rating_value)
        except (ValueError, TypeError):
            rating = 0.0
        
        # 处理分类标签（包括复选框和自定义输入）
        genre_tags = request.form.getlist('genre_tags')
        custom_genre = request.form.get('custom_genre', '').strip()
        
        # 合并标签并去重
        all_genres = set(genre_tags)
        if custom_genre:
            # 处理自定义输入中可能包含的多个标签（逗号分隔）
            custom_tags = [tag.strip() for tag in custom_genre.split(',') if tag.strip()]
            all_genres.update(custom_tags)
        
        # 转换为逗号分隔的字符串
        genre_string = ', '.join(sorted(all_genres))
        
        # 处理是否拥有
        is_owned = 'is_owned' in request.form
        
        book_data = {
            'title': request.form.get('title'),
            'author': request.form.get('author'),
            'publisher': request.form.get('publisher', ''),
            'publish_date': request.form.get('year', ''),
            'status': request.form.get('status'),
            'rating': rating,
            'notes': request.form.get('notes', ''),
            'cover_url': request.form.get('cover_url', ''),
            'tags': genre_string,
            'isbn': request.form.get('isbn', ''),
            'is_owned': is_owned,
            'description': request.form.get('description', ''),
            'translator': request.form.get('translator', ''),
            'series': request.form.get('series', ''),
            'page_count': request.form.get('page_count', ''),
            'price': request.form.get('price', '')
        }
        
        # 处理封面上传
        if 'cover' in request.files and request.files['cover'].filename:
            file = request.files['cover']
            if file and allowed_file(file.filename):
                # 生成安全的文件名
                filename = secure_filename(file.filename)
                # 确保文件名唯一
                unique_filename = f"{int(time.time())}_{filename}"
                # 保存文件
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                # 更新书籍封面URL
                book_data['cover_url'] = f"/uploads/{unique_filename}"
        
        book_id = add_book(book_data)
        if book_id:
            flash('图书已成功添加！', 'success')
            return redirect(url_for('books'))
        else:
            flash('添加图书失败，请检查输入数据。', 'danger')
    
    # 获取所有唯一的分类标签用于表单复选框
    all_books = get_all_books()
    unique_genres = set()
    for book in all_books:
        if book.get('tags'):
            genres = [g.strip() for g in book.get('tags').split(',')]
            for genre in genres:
                if genre:
                    unique_genres.add(genre)
    unique_genres = sorted(list(unique_genres))
    
    # 创建空的book对象，避免模板中的book变量未定义错误
    empty_book = {
        'title': '',
        'author': '',
        'publisher': '',
        'publish_date': '',
        'status': '未读',
        'rating': 0,
        'notes': '',
        'cover_url': '',
        'tags': '',
        'isbn': '',
        'is_owned': False,
        'description': '',
        'translator': '',
        'series': '',
        'page_count': '',
        'price': '',
        'id': None  # 确保id为None，表示这是新书
    }
    
    return render_template('book_form.html', genres=unique_genres, book=empty_book, book_genres=[], title="添加书籍")

@app.route('/books/<string:book_id>/delete', methods=['POST'])
def delete_book_route(book_id):
    """删除图书接口"""
    try:
        # 直接调用删除函数
        if delete_book(book_id):
            # 检查是否来自详情页的请求
            referrer = request.referrer
            if referrer and 'books/' + book_id in referrer:
                flash('图书已成功删除！', 'success')
                return redirect(url_for('books'))
            return jsonify({'success': True, 'message': '成功删除图书'}), 200
        else:
            return jsonify({'success': False, 'message': '未找到该书籍'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@app.route('/books/<string:book_id>/toggle-favorite', methods=['POST'])
def toggle_book_favorite(book_id):
    """切换图书收藏状态"""
    try:
        # 获取书籍
        book = get_book(book_id)
        
        if book:
            # 切换收藏状态
            is_favorite = not book.get('is_favorite', False)
            
            # 更新书籍信息
            book['is_favorite'] = is_favorite
            update_book(book_id, book)
            
            return jsonify({'success': True, 'is_favorite': is_favorite}), 200
        else:
            return jsonify({'success': False, 'message': '未找到该书籍'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@app.route('/books/<string:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    book = get_book(book_id)
    
    # 在GET请求时，确保状态显示正确
    if request.method == 'GET' and book:
        # 处理状态显示
        if book.get('status') == 'unread':
            book['status'] = '未读'
        elif book.get('status') == 'reading':
            book['status'] = '在读'
        elif book.get('status') == 'read':
            book['status'] = '读过'
        # 确保"想读"状态保持不变
        elif book.get('status') != '想读':
            # 如果状态不是已知的中文状态，则默认设为"未读"
            book['status'] = '未读'
    
    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title')
        author = request.form.get('author')
        publish_date = request.form.get('year', '')
        
        # 处理分类标签（包括复选框和自定义输入）
        genre_tags = request.form.getlist('genre_tags')
        custom_genre = request.form.get('custom_genre', '').strip()
        
        # 合并标签并去重
        all_genres = set(genre_tags)
        if custom_genre:
            # 处理自定义输入中可能包含的多个标签（逗号分隔）
            custom_tags = [tag.strip() for tag in custom_genre.split(',') if tag.strip()]
            all_genres.update(custom_tags)
        
        # 转换为逗号分隔的字符串
        tags = ', '.join(sorted(all_genres))
        
        # 获取状态值，直接使用表单中的值，不进行额外转换
        status = request.form.get('status')
        # 如果状态不是有效的选项之一，则设为默认值"未读"
        if status not in ['未读', '想读', '在读', '读过']:
            status = '未读'
        
        # 处理评分
        rating_str = request.form.get('rating', '0')
        try:
            rating = float(rating_str)
            # 确保评分在0-5之间
            rating = max(0, min(5, rating))
            # 保留一位小数，但不进行四舍五入到0.5
            rating = round(rating * 10) / 10  # 四舍五入到小数点后一位
        except ValueError:
            rating = 0
        
        # 处理是否拥有
        is_owned = 1 if request.form.get('is_owned') else 0
        
        # 创建图书数据字典
        book_data = {
            'title': title,
            'author': author,
            'publisher': request.form.get('publisher', ''),
            'publish_date': publish_date,
            'status': status,  # 直接使用表单中的状态值
            'rating': rating,
            'notes': request.form.get('notes', ''),
            'cover_url': request.form.get('cover_url', ''),
            'tags': tags,
            'isbn': request.form.get('isbn', ''),
            'is_owned': is_owned,
            'description': request.form.get('description', ''),
            'translator': request.form.get('translator', ''),
            'series': request.form.get('series', ''),
            'page_count': request.form.get('page_count', ''),
            'price': request.form.get('price', '')
        }
        
        # 更新图书信息
        update_book(book_id, book_data)
        
        flash('图书更新成功！', 'success')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # 获取所有唯一的分类标签
    unique_genres = set()
    all_books = get_all_books()
    for b in all_books:
        if b.get('tags'):
            genres = [tag.strip() for tag in b['tags'].split(',')]
            unique_genres.update(genres)
    
    # 获取图书的分类标签
    book_genres = []
    if book and book.get('tags'):
        book_genres = [tag.strip() for tag in book['tags'].split(',')]
    
    return render_template('book_form.html', genres=sorted(unique_genres), book=book, book_genres=book_genres, title="编辑书籍")

@app.route('/movies')
def movies():
    """电影页面"""
    movies = get_all_movies()
    
    # 处理状态显示
    for movie in movies:
        # 打印原始状态值，帮助调试
        logger.info(f"电影页面 - 原始状态值: {movie.get('status')}")
        
        # 将英文状态值映射到中文状态值
        if movie.get('status') == 'watched':
            movie['status'] = '已看'
        elif movie.get('status') == 'watching':
            movie['status'] = '想看'
        elif movie.get('status') == 'wanting':
            movie['status'] = '想看'
        elif movie.get('status') == 'unwatched':
            movie['status'] = '未看'
        # 确保中文状态保持不变
        elif movie.get('status') != '已看' and movie.get('status') != '想看' and movie.get('status') != '未看':
            # 如果状态不是已知的中文状态，则默认设为"未看"
            logger.info(f"电影页面 - 状态值不是已知的中文状态，设为未看: {movie.get('status')}")
            movie['status'] = '未看'
        
        # 打印处理后的状态值，帮助调试
        logger.info(f"电影页面 - 处理后状态值: {movie.get('status')}")
    
    # 获取所有导演
    directors = set()
    for movie in movies:
        if movie.get('director'):
            directors.add(movie['director'])
    
    # 获取所有演员
    actors = set()
    for movie in movies:
        if movie.get('cast'):
            cast_list = [actor.strip() for actor in movie['cast'].split(',')]
            actors.update(cast_list)
    
    # 获取所有电影分类
    genres = set()
    for movie in movies:
        if movie.get('genre'):
            genre_list = [genre.strip() for genre in movie['genre'].split(',')]
            genres.update(genre_list)
    
    return render_template('movies.html', movies=movies, genres=sorted(genres), directors=sorted(directors), actors=sorted(actors))

@app.route('/movies/<string:movie_id>')
def movie_detail(movie_id):
    """电影详情页面"""
    movie = get_movie(movie_id)
    if not movie:
        abort(404)
    
    # 打印原始状态值，帮助调试
    logger.info(f"电影详情页 - 原始状态值: {movie.get('status')}")
    
    # 将英文状态值映射到中文状态值
    if movie.get('status') == 'watched':
        movie['status'] = '已看'
    elif movie.get('status') == 'watching':
        movie['status'] = '想看'
    elif movie.get('status') == 'wanting':
        movie['status'] = '想看'
    elif movie.get('status') == 'unwatched':
        movie['status'] = '未看'
    # 确保中文状态保持不变
    elif movie.get('status') != '已看' and movie.get('status') != '想看' and movie.get('status') != '未看':
        # 如果状态不是已知的中文状态，则默认设为"未看"
        logger.info(f"电影详情页 - 状态值不是已知的中文状态，设为未看: {movie.get('status')}")
        movie['status'] = '未看'
    
    # 打印处理后的状态值，帮助调试
    logger.info(f"电影详情页 - 处理后状态值: {movie.get('status')}")
    
    return render_template('movie_detail.html', movie=movie)

@app.route('/movies/add', methods=['GET', 'POST'])
def add_movie_route():
    if request.method == 'POST':
        # 获取评分值
        rating_value = request.form.get('rating', '')
        try:
            rating = float(rating_value)
        except (ValueError, TypeError):
            rating = 0.0
            
        movie_data = {
            'title': request.form.get('title'),
            'director': request.form.get('director'),
            'cast': request.form.get('cast', ''),
            'year': request.form.get('year'),
            'genre': request.form.get('genre'),
            'status': request.form.get('status'),
            'rating': rating,
            'notes': request.form.get('notes', ''),
            'poster_url': request.form.get('poster_url', ''),
            'tags': request.form.get('tags', '')
        }
        
        # 处理海报上传
        if 'poster' in request.files and request.files['poster'].filename:
            file = request.files['poster']
            if file and allowed_file(file.filename):
                # 生成安全的文件名
                filename = secure_filename(file.filename)
                # 确保文件名唯一
                unique_filename = f"{int(time.time())}_{filename}"
                # 保存文件
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                # 更新电影海报URL
                movie_data['poster_url'] = f"/uploads/{unique_filename}"
        
        movie_id = add_movie(movie_data)
        if movie_id:
            flash('电影已成功添加！', 'success')
            return redirect(url_for('movies'))
        else:
            flash('添加电影失败，请检查输入数据。', 'danger')
    
    return render_template('movie_form.html')

@app.route('/movies/edit/<string:movie_id>', methods=['GET', 'POST'])
def edit_movie_route(movie_id):
    movie = get_movie(movie_id)
    if request.method == 'POST' and movie:
        # 获取评分值
        rating_value = request.form.get('rating', '')
        try:
            rating = float(rating_value)
        except (ValueError, TypeError):
            rating = 0.0
            
        # 准备更新数据
        updated_movie = movie.copy()
        updated_movie.update({
            'title': request.form.get('title'),
            'director': request.form.get('director'),
            'year': request.form.get('year'),
            'genre': request.form.get('genre'),
            'status': request.form.get('status'),
            'cast': request.form.get('cast', ''),
            'rating': rating,
            'notes': request.form.get('notes', ''),
            'tags': request.form.get('tags', ''),
            'updated_at': datetime.now().isoformat()
        })
        
        # 处理海报上传
        if 'poster' in request.files and request.files['poster'].filename:
            file = request.files['poster']
            if file and allowed_file(file.filename):
                # 生成安全的文件名
                filename = secure_filename(file.filename)
                # 确保文件名唯一
                unique_filename = f"{int(time.time())}_{filename}"
                # 保存文件
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                # 更新电影海报URL
                updated_movie['poster_url'] = f"/uploads/{unique_filename}"
        elif request.form.get('poster_url') != movie.get('poster_url', ''):
            # 如果URL已更改，更新海报URL
            updated_movie['poster_url'] = request.form.get('poster_url', '')
        
        # 更新数据库
        if update_movie(movie_id, updated_movie):
            flash('电影已成功更新！', 'success')
            return redirect(url_for('movie_detail', movie_id=movie_id))
        else:
            flash('更新电影失败。', 'danger')
            return redirect(url_for('movies'))
    return render_template('movie_form.html', movie=movie)

@app.route('/movies/<string:movie_id>/delete', methods=['POST'])
def delete_movie_route(movie_id):
    """删除电影接口"""
    try:
        # 直接调用删除函数
        if delete_movie(movie_id):
            # 检查是否来自详情页的请求
            referrer = request.referrer
            if referrer and 'movies/' + movie_id in referrer:
                flash('电影已成功删除！', 'success')
                return redirect(url_for('movies'))
            return jsonify({'success': True, 'message': '成功删除电影'}), 200
        else:
            return jsonify({'success': False, 'message': '未找到该电影'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@app.route('/music')
def music():
    """音乐页面"""
    musics = get_all_music()
    
    # 处理状态显示
    for music in musics:
        # 打印原始状态值，帮助调试
        logger.info(f"音乐页面 - 原始状态值: {music.get('status')}")
        
        # 将英文状态值映射到中文状态值
        if music.get('status') == 'listened':
            music['status'] = '已听'
        elif music.get('status') == 'listening':
            music['status'] = '想听'
        elif music.get('status') == 'wanting':
            music['status'] = '想听'
        elif music.get('status') == 'unlistened':
            music['status'] = '未听'
        # 确保中文状态保持不变
        elif music.get('status') != '已听' and music.get('status') != '想听' and music.get('status') != '未听':
            # 如果状态不是已知的中文状态，则默认设为"未听"
            logger.info(f"音乐页面 - 状态值不是已知的中文状态，设为未听: {music.get('status')}")
            music['status'] = '未听'
        
        # 打印处理后的状态值，帮助调试
        logger.info(f"音乐页面 - 处理后状态值: {music.get('status')}")
    
    # 获取所有艺术家
    artists = set()
    for music in musics:
        if music.get('artist'):
            artists.add(music['artist'])
    
    # 获取所有专辑
    albums = set()
    for music in musics:
        if music.get('album'):
            albums.add(music['album'])
    
    # 获取所有音乐分类
    genres = set()
    for music in musics:
        if music.get('genre'):
            genre_list = [genre.strip() for genre in music['genre'].split(',')]
            genres.update(genre_list)
    
    return render_template('music.html', musics=musics, genres=sorted(genres), artists=sorted(artists), albums=sorted(albums))

@app.route('/music/<string:music_id>')
def music_detail(music_id):
    """音乐详情页面"""
    music = get_music(music_id)
    if not music:
        abort(404)
    
    # 打印原始状态值，帮助调试
    logger.info(f"音乐详情页 - 原始状态值: {music.get('status')}")
    
    # 将英文状态值映射到中文状态值
    if music.get('status') == 'listened':
        music['status'] = '已听'
    elif music.get('status') == 'listening':
        music['status'] = '想听'
    elif music.get('status') == 'wanting':
        music['status'] = '想听'
    elif music.get('status') == 'unlistened':
        music['status'] = '未听'
    # 确保中文状态保持不变
    elif music.get('status') != '已听' and music.get('status') != '想听' and music.get('status') != '未听':
        # 如果状态不是已知的中文状态，则默认设为"未听"
        logger.info(f"音乐详情页 - 状态值不是已知的中文状态，设为未听: {music.get('status')}")
        music['status'] = '未听'
    
    # 打印处理后的状态值，帮助调试
    logger.info(f"音乐详情页 - 处理后状态值: {music.get('status')}")
    
    return render_template('music_detail.html', music=music)

@app.route('/music/add', methods=['GET', 'POST'])
def add_music_route():
    if request.method == 'POST':
        # 获取评分值
        rating_value = request.form.get('rating', '')
        try:
            rating = float(rating_value)
        except (ValueError, TypeError):
            rating = 0.0
            
        music_data = {
            'title': request.form.get('album'),  # 使用album作为title
            'album': request.form.get('album'),
            'artist': request.form.get('artist'),
            'year': request.form.get('year'),
            'genre': request.form.get('genre'),
            'status': request.form.get('status'),
            'rating': rating,
            'notes': request.form.get('notes', ''),
            'cover_url': request.form.get('cover_url', ''),
            'tags': request.form.get('tags', '')
        }
        
        # 处理封面上传
        if 'cover' in request.files and request.files['cover'].filename:
            file = request.files['cover']
            if file and allowed_file(file.filename):
                # 生成安全的文件名
                filename = secure_filename(file.filename)
                # 确保文件名唯一
                unique_filename = f"{int(time.time())}_{filename}"
                # 保存文件
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                # 更新音乐封面URL
                music_data['cover_url'] = f"/uploads/{unique_filename}"
        
        music_id = add_music(music_data)
        if music_id:
            flash('音乐已成功添加！', 'success')
            return redirect(url_for('music'))
        else:
            flash('添加音乐失败，请检查输入数据。', 'danger')
    
    return render_template('music_form.html')

@app.route('/music/edit/<string:music_id>', methods=['GET', 'POST'])
def edit_music_route(music_id):
    music_item = get_music(music_id)
    if request.method == 'POST' and music_item:
        # 获取评分值
        rating_value = request.form.get('rating', '')
        try:
            rating = float(rating_value)
        except (ValueError, TypeError):
            rating = 0.0
            
        # 准备更新数据
        updated_music = music_item.copy()
        updated_music.update({
            'title': request.form.get('album'),  # 使用album作为title
            'album': request.form.get('album'),
            'artist': request.form.get('artist'),
            'year': request.form.get('year'),
            'genre': request.form.get('genre'),
            'status': request.form.get('status'),
            'rating': rating,
            'notes': request.form.get('notes', ''),
            'tags': request.form.get('tags', ''),
            'updated_at': datetime.now().isoformat()
        })
        
        # 处理封面上传
        if 'cover' in request.files and request.files['cover'].filename:
            file = request.files['cover']
            if file and allowed_file(file.filename):
                # 生成安全的文件名
                filename = secure_filename(file.filename)
                # 确保文件名唯一
                unique_filename = f"{int(time.time())}_{filename}"
                # 保存文件
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                # 更新音乐封面URL
                updated_music['cover_url'] = f"/uploads/{unique_filename}"
        elif request.form.get('cover_url') != music_item.get('cover_url', ''):
            # 如果URL已更改，更新封面URL
            updated_music['cover_url'] = request.form.get('cover_url', '')
        
        # 更新数据库
        if update_music(music_id, updated_music):
            flash('音乐已成功更新！', 'success')
            return redirect(url_for('music_detail', music_id=music_id))
        else:
            flash('更新音乐失败。', 'danger')
            return redirect(url_for('music'))
    return render_template('music_form.html', music=music_item)

@app.route('/music/<string:music_id>/delete', methods=['POST'])
def delete_music_route(music_id):
    """删除音乐接口"""
    try:
        # 直接调用删除函数
        if delete_music(music_id):
            # 检查是否来自详情页的请求
            referrer = request.referrer
            if referrer and 'music/' + music_id in referrer:
                flash('音乐已成功删除！', 'success')
                return redirect(url_for('music'))
            return jsonify({'success': True, 'message': '成功删除音乐'}), 200
        else:
            return jsonify({'success': False, 'message': '未找到该音乐'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

# API路由
@app.route('/api/books', methods=['GET'])
def api_get_books():
    return jsonify(get_all_books())

@app.route('/api/books/<string:book_id>', methods=['GET'])
def api_get_book(book_id):
    return jsonify(get_book(book_id))

@app.route('/api/books', methods=['POST'])
def api_add_book():
    book_data = request.json
    book_id = add_book(book_data)
    return jsonify({'id': book_id, 'message': 'Book added successfully'})

@app.route('/api/books/<string:book_id>', methods=['PUT'])
def api_update_book(book_id):
    book_data = request.json
    update_book(book_id, book_data)
    return jsonify({'message': 'Book updated successfully'})

@app.route('/api/books/<string:book_id>', methods=['DELETE'])
def api_delete_book(book_id):
    delete_book(book_id)
    return jsonify({'message': 'Book deleted successfully'})

@app.route('/api/movies', methods=['GET'])
def api_get_movies():
    return jsonify(get_all_movies())

@app.route('/api/movies/<string:movie_id>', methods=['GET'])
def api_get_movie(movie_id):
    return jsonify(get_movie(movie_id))

@app.route('/api/movies', methods=['POST'])
def api_add_movie():
    movie_data = request.json
    movie_id = add_movie(movie_data)
    return jsonify({'id': movie_id, 'message': 'Movie added successfully'})

@app.route('/api/movies/<string:movie_id>', methods=['PUT'])
def api_update_movie(movie_id):
    movie_data = request.json
    update_movie(movie_id, movie_data)
    return jsonify({'message': 'Movie updated successfully'})

@app.route('/api/movies/<string:movie_id>', methods=['DELETE'])
def api_delete_movie(movie_id):
    delete_movie(movie_id)
    return jsonify({'message': 'Movie deleted successfully'})

@app.route('/api/music', methods=['GET'])
def api_get_music():
    return jsonify(get_all_music())

@app.route('/api/music/<string:music_id>', methods=['GET'])
def api_get_music_item(music_id):
    return jsonify(get_music(music_id))

@app.route('/api/music', methods=['POST'])
def api_add_music():
    music_data = request.json
    # 确保使用album作为主要标识，不使用title
    if 'title' in music_data:
        # 如果API请求中包含title字段，将其值复制到album字段
        if not music_data.get('album'):
            music_data['album'] = music_data.pop('title')
        else:
            # 如果已有album字段，则删除title字段
            music_data.pop('title')
    
    # 确保必要字段存在
    if not music_data.get('album'):
        return jsonify({'error': '缺少必要字段: album'}), 400
    
    # 设置默认状态
    if not music_data.get('status'):
        music_data['status'] = 'unlistened'
        
    music_id = add_music(music_data)
    return jsonify({'id': music_id, 'message': 'Music added successfully'})

@app.route('/api/music/<string:music_id>', methods=['PUT'])
def api_update_music(music_id):
    music_data = request.json
    # 确保使用album作为主要标识，不使用title
    if 'title' in music_data:
        # 如果API请求中包含title字段，将其值复制到album字段
        if not music_data.get('album'):
            music_data['album'] = music_data.pop('title')
        else:
            # 如果已有album字段，则删除title字段
            music_data.pop('title')
    
    # 获取现有音乐数据以保留未更新的字段
    existing_music = get_music(music_id)
    if existing_music and not music_data.get('status'):
        music_data['status'] = existing_music.get('status', 'unlistened')
            
    update_music(music_id, music_data)
    return jsonify({'message': 'Music updated successfully'})

@app.route('/api/music/<string:music_id>', methods=['DELETE'])
def api_delete_music(music_id):
    delete_music(music_id)
    return jsonify({'message': 'Music deleted successfully'})

@app.route('/bookshelf')
def bookshelf():
    # 获取所有书籍，但只显示拥有的书籍
    all_books = get_all_books()
    owned_books = [book for book in all_books if book.get('is_owned')]
    
    # 处理状态显示
    for book in owned_books:
        # 打印原始状态值，帮助调试
        logger.info(f"书架页面 - 原始状态值: {book.get('status')}")
        
        # 将旧的状态值映射到新的状态值
        if book.get('status') == 'unread':
            book['status'] = '未读'
        elif book.get('status') == 'reading':
            book['status'] = '在读'
        elif book.get('status') == 'read':
            book['status'] = '读过'
        # 确保"想读"、"在读"和"读过"状态保持不变
        elif book.get('status') != '想读' and book.get('status') != '在读' and book.get('status') != '读过' and book.get('status') != '未读':
            # 如果状态不是已知的中文状态，则默认设为"未读"
            logger.info(f"书架页面 - 状态值不是已知的中文状态，设为未读: {book.get('status')}")
            book['status'] = '未读'
        
        # 打印处理后的状态值，帮助调试
        logger.info(f"书架页面 - 处理后状态值: {book.get('status')}")
    
    # 获取所有书籍中的唯一分类标签（支持逗号分隔的多个标签）
    unique_genres = set()
    for book in all_books:
        if book.get('tags'):
            # 分割每本书的分类，并去除首尾空格
            genres = [g.strip() for g in book.get('tags').split(',')]
            for genre in genres:
                if genre:  # 确保标签不为空
                    unique_genres.add(genre)
    
    # 获取所有书籍中的唯一作者
    unique_authors = set()
    for book in all_books:
        if book.get('author'):
            author = book.get('author').strip()
            if author:  # 确保作者不为空
                unique_authors.add(author)
    
    # 将集合转换为排序列表
    unique_genres = sorted(list(unique_genres))
    unique_authors = sorted(list(unique_authors))
    
    return render_template('bookshelf.html', books=owned_books, genres=unique_genres, authors=unique_authors)

@app.route('/private/novels')
def private_novels():
    return render_template('private_novels.html')

@app.route('/private/artists')
def private_artists():
    return render_template('private_artists.html')

@app.route('/private/collections')
def private_collections():
    return render_template('private_collections.html')

# 添加WebDAV相关导入
import io
import logging
import sys
import threading
from app.config import get_config, update_config
from app.webdav_sync import sync_data, test_connection, get_available_backups

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 自定义过滤器，将时间戳转换为ISO格式
@app.template_filter('timestamp_to_iso')
def timestamp_to_iso(timestamp):
    if timestamp:
        return datetime.fromtimestamp(timestamp).isoformat()
    return None

# 设置页面
@app.route('/settings')
def settings():
    # 获取配置
    config = get_config()
    
    # 获取数据目录和配置目录
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
    
    # 统计数据
    stats = {
        'books': len(get_all_books()),
        'movies': len(get_all_movies()),
        'music': len(get_all_music())
    }
    
    return render_template('settings.html', 
                          config=config, 
                          data_dir=data_dir, 
                          config_dir=config_dir,
                          stats=stats)

# WebDAV设置保存
@app.route('/settings/webdav/save', methods=['POST'])
def save_webdav_settings():
    # 获取表单数据
    webdav_url = request.form.get('webdav_url', '')
    webdav_username = request.form.get('webdav_username', '')
    webdav_password = request.form.get('webdav_password', '')
    webdav_path = request.form.get('webdav_path', '/media-manager/')
    sync_interval = request.form.get('sync_interval', '3600')
    
    # 确保路径以/开头和结尾
    if not webdav_path.startswith('/'):
        webdav_path = '/' + webdav_path
    if not webdav_path.endswith('/'):
        webdav_path += '/'
    
    # 确保同步间隔是整数
    try:
        sync_interval = int(sync_interval)
        if sync_interval < 60:
            sync_interval = 60  # 最小1分钟
    except ValueError:
        sync_interval = 3600  # 默认1小时
    
    # 更新配置
    update_config('webdav.url', webdav_url)
    update_config('webdav.username', webdav_username)
    update_config('webdav.password', webdav_password)
    update_config('webdav.remote_path', webdav_path)
    update_config('webdav.sync_interval', sync_interval)
    
    flash('WebDAV设置已保存', 'success')
    return redirect(url_for('settings'))

# 切换WebDAV启用状态
@app.route('/settings/webdav/toggle', methods=['POST'])
def toggle_webdav():
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        # 更新配置
        update_config('webdav.enabled', enabled)
        
        return jsonify({'success': True, 'enabled': enabled})
    except Exception as e:
        logger.error(f"切换WebDAV状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# 测试WebDAV连接
@app.route('/settings/webdav/test', methods=['POST'])
def test_webdav_connection():
    try:
        data = request.get_json()
        
        # 临时更新配置用于测试
        temp_config = get_config()
        temp_config['webdav']['url'] = data.get('webdav_url', '')
        temp_config['webdav']['username'] = data.get('webdav_username', '')
        temp_config['webdav']['password'] = data.get('webdav_password', '')
        temp_config['webdav']['remote_path'] = data.get('webdav_path', '/media-manager/')
        temp_config['webdav']['enabled'] = True
        
        # 测试连接
        success, message = test_connection()
        
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        logger.error(f"测试WebDAV连接失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# 捕获同步日志
class LogCapture:
    def __init__(self):
        self.log_capture_string = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_capture_string)
        self.log_handler.setLevel(logging.INFO)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # 添加处理器
        logger = logging.getLogger()
        logger.addHandler(self.log_handler)
    
    def get_log(self):
        log_contents = self.log_capture_string.getvalue()
        # 重置日志缓冲区
        self.log_capture_string.truncate(0)
        self.log_capture_string.seek(0)
        return log_contents
    
    def close(self):
        # 移除处理器
        logger = logging.getLogger()
        logger.removeHandler(self.log_handler)
        self.log_capture_string.close()

# 获取可用备份列表
@app.route('/settings/webdav/backups', methods=['GET'])
def get_webdav_backups():
    try:
        backups = get_available_backups()
        return jsonify({'success': True, 'backups': backups})
    except Exception as e:
        logger.error(f"获取备份列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# 仅上传同步
@app.route('/settings/webdav/upload', methods=['POST'])
def upload_webdav_now():
    try:
        # 捕获日志
        log_capture = LogCapture()
        
        # 执行上传同步
        success = sync_data(force=True, direction='upload')
        
        # 获取日志
        log = log_capture.get_log()
        log_capture.close()
        
        if success:
            return jsonify({'success': True, 'message': '上传成功', 'log': log})
        else:
            return jsonify({'success': False, 'message': '上传失败，请检查日志', 'log': log})
    except Exception as e:
        logger.error(f"上传失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# 仅下载同步
@app.route('/settings/webdav/download', methods=['POST'])
def download_webdav_now():
    try:
        # 获取请求数据
        data = request.get_json() or {}
        backup_path = data.get('backup_path')
        
        # 捕获日志
        log_capture = LogCapture()
        
        # 执行下载同步
        success = sync_data(force=True, direction='download', backup_path=backup_path)
        
        # 获取日志
        log = log_capture.get_log()
        log_capture.close()
        
        if success:
            return jsonify({'success': True, 'message': '下载成功', 'log': log})
        else:
            return jsonify({'success': False, 'message': '下载失败，请检查日志', 'log': log})
    except Exception as e:
        logger.error(f"下载失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# 添加导航栏链接
@app.context_processor
def inject_nav_links():
    return {
        'nav_links': [
            {'url': url_for('index'), 'text': '首页', 'icon': 'bi-house'},
            {'url': url_for('books'), 'text': '书籍', 'icon': 'bi-book'},
            {'url': url_for('movies'), 'text': '电影', 'icon': 'bi-film'},
            {'url': url_for('music'), 'text': '音乐', 'icon': 'bi-music-note-beamed'},
            {'url': url_for('bookshelf'), 'text': '书架', 'icon': 'bi-bookshelf'},
            {'url': url_for('settings'), 'text': '设置', 'icon': 'bi-gear'}
        ]
    }

# 豆瓣搜索页面
@app.route('/douban/search')
def douban_search():
    """豆瓣搜索页面"""
    try:
        # 添加日志记录
        logger.info("访问豆瓣搜索页面")
        return render_template('douban/search.html')
    except Exception as e:
        logger.error(f"渲染豆瓣搜索页面失败: {str(e)}")
        flash('页面加载失败，请稍后再试', 'danger')
        return redirect(url_for('index'))

# 豆瓣搜索API
@app.route('/api/douban/search', methods=['GET'])
def api_douban_search():
    """豆瓣搜索API"""
    try:
        keyword = request.args.get('keyword', '')
        item_type = request.args.get('type', 'all')
        page = int(request.args.get('page', 1))
        count = int(request.args.get('count', 20))
        
        logger.info(f"豆瓣搜索API请求: keyword={keyword}, type={item_type}, page={page}, count={count}")
        
        if not keyword:
            logger.warning("豆瓣搜索API请求缺少关键词")
            return jsonify({'success': False, 'message': '请输入搜索关键词', 'results': []}), 400
        
        results = douban_service.search(keyword, item_type, page, count)
        
        # 如果是音乐搜索，尝试补充艺术家信息
        if item_type == 'music':
            for result in results:
                # 从描述中提取艺术家信息
                if 'description' in result and result['description'] and not result.get('artist'):
                    parts = result['description'].split('/')
                    if len(parts) > 0 and parts[0].strip():
                        # 将艺术家信息添加到结果中
                        result['artist'] = parts[0].strip()
        
        logger.info(f"豆瓣搜索API返回结果: {len(results)}个结果")
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        logger.error(f"豆瓣搜索API异常: {str(e)}")
        return jsonify({'success': False, 'message': f'搜索失败: {str(e)}', 'results': []}), 500

# 豆瓣电影详情页面
@app.route('/douban/movie/<string:movie_id>')
def douban_movie_detail(movie_id):
    """豆瓣电影详情页面"""
    movie = douban_service.get_movie_detail_for_import(movie_id)
    if not movie:
        flash('无法获取电影信息，请稍后再试', 'danger')
        return redirect(url_for('douban_search'))
    
    return render_template('douban/movie_detail.html', movie=movie)

@app.route('/douban/book/<string:book_id>/import', methods=['POST'])
def import_douban_book(book_id):
    """导入豆瓣图书"""
    # 验证ID
    logger.info(f"开始导入豆瓣图书，ID: {book_id}")
    
    if not book_id or book_id.strip() == '':
        logger.error("导入图书失败: 无效的图书ID (为空)")
        flash('无效的图书ID', 'danger')
        return redirect(url_for('douban_search'))
    
    book = douban_service.get_book_detail_for_import(book_id)
    if not book:
        logger.error(f"导入图书失败: 无法获取图书信息，ID: {book_id}")
        flash('无法获取图书信息，请稍后再试', 'danger')
        return redirect(url_for('douban_search'))
    
    # 记录详细信息，用于调试
    logger.info(f"准备导入豆瓣图书，原始API数据: {book}")
    
    # 用户可以修改的字段
    status = request.form.get('status', '想读')
    logger.info(f"用户选择的状态: {status}")
    book['status'] = status  # 使用status字段而不是state字段
    
    # 处理评分 - 保持用户输入的评分
    rating = request.form.get('rating', '0')
    try:
        book['rating'] = float(rating)  # 直接使用表单中的评分
        logger.info(f"用户评分: {book['rating']}")
    except (ValueError, TypeError):
        book['rating'] = 0.0
        logger.warning(f"评分转换失败，使用默认值0: {rating}")
    
    # 处理是否拥有
    book['is_owned'] = 'is_owned' in request.form
    logger.info(f"是否拥有: {book['is_owned']}")
    
    # 不保存封面图片，将cover_url设为空
    book['cover_url'] = ''
    
    # 确保出版日期字段正确映射
    if 'publish_date' in book:
        logger.info(f"出版日期(publish_date): {book['publish_date']}")
    else:
        logger.warning("未找到publish_date字段")
    
    # 删除豆瓣ID，让系统生成新的UUID
    if 'id' in book:
        logger.info(f"删除豆瓣图书ID: {book['id']}，准备生成新UUID")
        del book['id']
    
    # 添加图书
    try:
        # 记录最终要保存到数据库的数据
        logger.info(f"最终保存到数据库的图书数据: {book}")
        book_id = add_book(book)
        if book_id:
            logger.info(f"图书导入成功，新ID: {book_id}")
            flash('图书已成功导入！', 'success')
            return redirect(url_for('book_detail', book_id=book_id))
        else:
            logger.error("图书导入失败: add_book返回空ID")
            flash('导入图书失败，请稍后再试', 'danger')
            return redirect(url_for('douban_search'))
    except Exception as e:
        logger.error(f"图书导入异常: {str(e)}")
        flash(f'导入图书失败: {str(e)}', 'danger')
        return redirect(url_for('douban_search'))

# 豆瓣音乐详情页面
@app.route('/douban/music/<string:music_id>')
def douban_music_detail(music_id):
    """豆瓣音乐详情页面"""
    # 获取来源URL，检查是否从搜索结果页面跳转
    referer = request.referrer or ""
    artist_from_search = request.args.get('artist', '')
    
    # 从API获取音乐详情
    music = douban_service.get_music_detail_for_import(music_id)
    if not music:
        flash('无法获取音乐信息，请稍后再试', 'danger')
        return redirect(url_for('douban_search'))
    
    # 记录详细信息，用于调试
    logger.info(f"豆瓣音乐详情: {music}")
    
    # 如果URL参数中包含艺术家信息，优先使用
    if artist_from_search:
        music['artist'] = artist_from_search
        logger.info(f"从URL参数获取艺术家信息: {artist_from_search}")
    
    # 确保艺术家信息存在
    if not music.get('artist'):
        # 尝试从描述中提取艺术家信息
        if music.get('description'):
            desc = music['description']
            first_line = desc.split('\n')[0] if '\n' in desc else desc
            for separator in ['/', ':', '：', '-', '–', '—']:
                if separator in first_line:
                    parts = first_line.split(separator)
                    if len(parts) > 0 and parts[0].strip():
                        music['artist'] = parts[0].strip()
                        break
        
        # 如果仍然没有艺术家信息，尝试从专辑标题推断
        if not music.get('artist'):
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
                '第二人生': '五月天',
                '步步': '五月天',
                '新长征路上的摇滚': '崔健',
            }
            
            title = music.get('title', '')
            if title in special_albums:
                music['artist'] = special_albums[title]
    
    # 记录最终的艺术家信息
    logger.info(f"最终艺术家信息: {music.get('artist', '未知')}")
    
    return render_template('douban/music_detail.html', music=music)

# 导入豆瓣电影
@app.route('/douban/movie/<string:movie_id>/import', methods=['POST'])
def import_douban_movie(movie_id):
    """导入豆瓣电影"""
    # 验证ID
    logger.info(f"开始导入豆瓣电影，ID: {movie_id}")
    
    if not movie_id or movie_id.strip() == '':
        logger.error("导入电影失败: 无效的电影ID (为空)")
        flash('无效的电影ID', 'danger')
        return redirect(url_for('douban_search'))
    
    movie = douban_service.get_movie_detail_for_import(movie_id)
    if not movie:
        logger.error(f"导入电影失败: 无法获取电影信息，ID: {movie_id}")
        flash('无法获取电影信息，请稍后再试', 'danger')
        return redirect(url_for('douban_search'))
    
    # 记录详细信息，用于调试
    logger.info(f"准备导入豆瓣电影，原始API数据: {movie}")
    
    # 用户可以修改的字段
    status = request.form.get('status', '未看')
    logger.info(f"用户选择的状态: {status}")
    movie['status'] = status
    
    # 处理评分
    rating = request.form.get('rating', '0')
    try:
        movie['rating'] = float(rating)  # 直接使用表单中的评分
        logger.info(f"用户评分: {movie['rating']}")
    except (ValueError, TypeError):
        movie['rating'] = 0.0
        logger.warning(f"评分转换失败，使用默认值0: {rating}")
    
    movie['notes'] = request.form.get('notes', '')
    
    # 不保存图片URL
    movie['poster_url'] = ''
    
    # 删除豆瓣ID，让系统生成新的UUID
    if 'id' in movie:
        # 删除豆瓣ID前记录日志
        logger.info(f"删除豆瓣电影ID: {movie['id']}，准备生成新UUID")
        del movie['id']
    
    # 添加电影
    movie_id = add_movie(movie)
    if movie_id:
        flash('电影已成功导入到媒体库！', 'success')
        return redirect(url_for('movie_detail', movie_id=movie_id))
    else:
        flash('导入电影失败，请稍后再试。', 'danger')
        return redirect(url_for('douban_search'))

# 导入豆瓣音乐
@app.route('/douban/music/<string:music_id>/import', methods=['POST'])
def import_douban_music(music_id):
    """导入豆瓣音乐"""
    # 验证ID
    logger.info(f"开始导入豆瓣音乐，ID: {music_id}")
    
    if not music_id or music_id.strip() == '':
        logger.error("导入音乐失败: 无效的音乐ID (为空)")
        flash('无效的音乐ID', 'danger')
        return redirect(url_for('douban_search'))
    
    music = douban_service.get_music_detail_for_import(music_id)
    if not music:
        logger.error(f"导入音乐失败: 无法获取音乐信息，ID: {music_id}")
        flash('无法获取音乐信息，请稍后再试', 'danger')
        return redirect(url_for('douban_search'))
    
    # 记录详细信息，用于调试
    logger.info(f"准备导入豆瓣音乐: {music}")
    
    # 用户可以修改的字段
    status = request.form.get('status', '未听')
    logger.info(f"用户选择的状态: {status}")
    music['status'] = status
    
    # 处理评分
    rating = request.form.get('rating', '0')
    try:
        music['rating'] = float(rating)  # 直接使用表单中的评分
        logger.info(f"用户评分: {music['rating']}")
    except (ValueError, TypeError):
        music['rating'] = 0.0
        logger.warning(f"评分转换失败，使用默认值0: {rating}")
    
    music['notes'] = request.form.get('notes', '')
    
    # 获取用户输入的艺术家信息
    music['artist'] = request.form.get('artist', '')
    
    # 记录用户提供的艺术家信息
    logger.info(f"用户提供的艺术家信息: {music['artist']}")
    
    # 不保存图片URL
    music['cover_url'] = ''
    
    # 删除豆瓣ID，让系统生成新的UUID
    if 'id' in music:
        # 删除豆瓣ID前记录日志
        logger.info(f"删除豆瓣音乐ID: {music['id']}，准备生成新UUID")
        del music['id']
    
    # 添加音乐
    music_id = add_music(music)
    if music_id:
        flash('音乐已成功导入到媒体库！', 'success')
        return redirect(url_for('music_detail', music_id=music_id))
    else:
        flash('导入音乐失败，请稍后再试。', 'danger')
        return redirect(url_for('douban_search'))

# 豆瓣API获取电影详情
@app.route('/api/douban/movie/<string:movie_id>', methods=['GET'])
def api_douban_movie_detail(movie_id):
    """豆瓣API获取电影详情"""
    movie = douban_service.get_movie_detail_for_import(movie_id)
    if not movie:
        return jsonify({'success': False, 'message': '无法获取电影信息'}), 400
    
    return jsonify({'success': True, 'movie': movie})

# 豆瓣API获取图书详情
@app.route('/api/douban/book/<string:book_id>', methods=['GET'])
def api_douban_book_detail(book_id):
    """豆瓣API获取图书详情"""
    book = douban_service.get_book_detail_for_import(book_id)
    if not book:
        return jsonify({'success': False, 'message': '无法获取图书信息'}), 400
    
    return jsonify({'success': True, 'book': book})

# 豆瓣API获取音乐详情
@app.route('/api/douban/music/<string:music_id>', methods=['GET'])
def api_douban_music_detail(music_id):
    """豆瓣API获取音乐详情"""
    music = douban_service.get_music_detail_for_import(music_id)
    if not music:
        return jsonify({'success': False, 'message': '无法获取音乐信息'}), 400
    
    return jsonify({'success': True, 'music': music})

# 豆瓣图书详情页面
@app.route('/douban/book/<string:book_id>')
def douban_book_detail(book_id):
    """豆瓣图书详情页面"""
    book = douban_service.get_book_detail_for_import(book_id)
    if not book:
        flash('无法获取图书信息，请稍后再试', 'danger')
        return redirect(url_for('douban_search'))
    
    # 记录详细信息，用于调试
    logger.info(f"豆瓣图书详情: {book}")
    
    return render_template('douban/book_detail.html', book=book) 