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
    all_books = get_all_books()
    
    # 获取所有书籍中的唯一分类标签
    unique_genres = set()
    # 获取所有书籍中的唯一作者
    unique_authors = set()
    
    for book in all_books:
        if book.get('tags'):
            # 分割每本书的分类，并去除首尾空格
            genres = [g.strip() for g in book.get('tags').split(',')]
            for genre in genres:
                if genre:  # 确保标签不为空
                    unique_genres.add(genre)
        
        if book.get('author'):
            author = book.get('author').strip()
            if author:  # 确保作者不为空
                unique_authors.add(author)
    
    # 将集合转换为排序列表
    unique_genres = sorted(list(unique_genres))
    unique_authors = sorted(list(unique_authors))
    
    return render_template('books.html', books=all_books, genres=unique_genres, authors=unique_authors)

@app.route('/books/<string:book_id>')
def book_detail(book_id):
    book = get_book(book_id)
    return render_template('item_detail.html', item=book, item_type='book')

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
            'description': request.form.get('description', '')
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
    
    return render_template('book_form.html', genres=unique_genres)

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
        
        status = request.form.get('status')
        rating_value = request.form.get('rating', '')
        # 确保评分值是浮点数
        try:
            rating = float(rating_value)
        except (ValueError, TypeError):
            rating = 0.0
        notes = request.form.get('notes', '')
        publisher = request.form.get('publisher', '')
        isbn = request.form.get('isbn', '')
        
        # 处理是否拥有
        is_owned = 'is_owned' in request.form
        
        if book:
            # 准备更新数据
            updated_book = book.copy()
            updated_book.update({
                'title': title,
                'author': author,
                'publish_date': publish_date,
                'publisher': publisher,
                'isbn': isbn,
                'status': status,
                'rating': rating,
                'notes': notes,
                'tags': tags,
                'is_owned': is_owned,
                'description': request.form.get('description', ''),
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
                    # 更新书籍封面URL
                    updated_book['cover_url'] = f"/uploads/{unique_filename}"
            elif request.form.get('cover_url') != book.get('cover_url', ''):
                # 如果URL已更改，更新封面URL
                updated_book['cover_url'] = request.form.get('cover_url', '')
            
            # 更新数据库
            if update_book(book_id, updated_book):
                flash('图书已成功更新！', 'success')
                return redirect(url_for('book_detail', book_id=book_id))
            else:
                flash('更新图书失败。', 'danger')
                return redirect(url_for('books'))
        
        flash('未找到要编辑的图书。', 'danger')
        return redirect(url_for('books'))
    
    # 获取所有唯一的分类标签用于表单复选框
    all_books = get_all_books()
    unique_genres = set()
    for b in all_books:
        if b.get('tags'):
            genres = [g.strip() for g in b.get('tags').split(',')]
            for genre in genres:
                if genre:
                    unique_genres.add(genre)
    unique_genres = sorted(list(unique_genres))
    
    # 如果当前图书有分类，将其分割为列表
    book_genres = []
    if book and book.get('tags'):
        book_genres = [g.strip() for g in book.get('tags').split(',')]
    
    return render_template('book_form.html', book=book, genres=unique_genres, book_genres=book_genres)

@app.route('/movies')
def movies():
    all_movies = get_all_movies()
    
    # 获取所有电影中的唯一分类标签
    unique_genres = set()
    # 获取所有电影中的唯一导演
    unique_directors = set()
    # 获取所有电影中的唯一演员
    unique_actors = set()
    
    for movie in all_movies:
        if movie.get('genre'):
            # 分割每部电影的分类，并去除首尾空格
            genres = [g.strip() for g in movie.get('genre').split(',')]
            for genre in genres:
                if genre:  # 确保标签不为空
                    unique_genres.add(genre)
        
        if movie.get('director'):
            director = movie.get('director').strip()
            if director:  # 确保导演不为空
                unique_directors.add(director)
        
        if movie.get('cast'):
            # 分割每部电影的演员，并去除首尾空格
            actors = [a.strip() for a in movie.get('cast').split(',')]
            for actor in actors:
                if actor:  # 确保演员不为空
                    unique_actors.add(actor)
    
    # 将集合转换为排序列表
    unique_genres = sorted(list(unique_genres))
    unique_directors = sorted(list(unique_directors))
    unique_actors = sorted(list(unique_actors))
    
    return render_template('movies.html', movies=all_movies, genres=unique_genres, 
                           directors=unique_directors, actors=unique_actors)

@app.route('/movies/<string:movie_id>')
def movie_detail(movie_id):
    movie = get_movie(movie_id)
    return render_template('item_detail.html', item=movie, item_type='movie')

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
    all_music = get_all_music()
    
    # 获取所有音乐中的唯一分类标签
    unique_genres = set()
    # 获取所有音乐中的唯一艺术家
    unique_artists = set()
    
    for music_item in all_music:
        if music_item.get('genre'):
            # 分割每首音乐的分类，并去除首尾空格
            genres = [g.strip() for g in music_item.get('genre').split(',')]
            for genre in genres:
                if genre:  # 确保标签不为空
                    unique_genres.add(genre)
        
        if music_item.get('artist'):
            artist = music_item.get('artist').strip()
            if artist:  # 确保艺术家不为空
                unique_artists.add(artist)
    
    # 将集合转换为排序列表
    unique_genres = sorted(list(unique_genres))
    unique_artists = sorted(list(unique_artists))
    
    return render_template('music.html', musics=all_music, genres=unique_genres, artists=unique_artists)

@app.route('/music/<string:music_id>')
def music_detail(music_id):
    music_item = get_music(music_id)
    return render_template('item_detail.html', item=music_item, item_type='music')

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