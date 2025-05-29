from flask import render_template, request, jsonify, redirect, url_for, flash, send_from_directory, abort
from app import app
from app.models import (get_all_books, get_book, add_book, update_book, delete_book,
                       get_all_movies, get_movie, add_movie, update_movie, delete_movie,
                       get_all_music, get_music, add_music, update_music, delete_music)
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import time
from app.models import save_books
from app.utils import get_common_genres, get_image_url

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
        if book.get('genre'):
            # 分割每本书的分类，并去除首尾空格
            genres = [g.strip() for g in book.get('genre').split(',')]
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
        
        book_data = {
            'title': request.form.get('title'),
            'author': request.form.get('author'),
            'year': request.form.get('year'),
            'genre': genre_string,
            'cover_url': request.form.get('cover_url'),
            'description': request.form.get('description'),
            'rating': rating,
            'status': request.form.get('status'),
            'notes': request.form.get('notes'),
            'is_owned': request.form.get('is_owned') == 'on',
            'is_favorite': False,
            'added_date': datetime.now().strftime('%Y-%m-%d')
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
        elif not book_data.get('cover_url'):
            # 如果没有上传封面且没有提供URL，确保cover_url为空字符串而不是None
            book_data['cover_url'] = ''
        
        book_id = add_book(book_data)
        flash('图书已成功添加！', 'success')
        return redirect(url_for('books'))
    
    # 获取所有唯一的分类标签用于表单复选框
    all_books = get_all_books()
    unique_genres = set()
    for book in all_books:
        if book.get('genre'):
            genres = [g.strip() for g in book.get('genre').split(',')]
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
        # 获取所有书籍
        books = get_all_books()
        
        # 查找要修改的书籍
        book = next((book for book in books if book.get('id') == book_id), None)
        
        if book:
            # 切换收藏状态
            book['is_favorite'] = not book.get('is_favorite', False)
            
            # 保存更新后的数据
            save_books(books)
            
            return jsonify({'success': True, 'is_favorite': book['is_favorite']}), 200
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
        year = request.form.get('year')
        
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
        genre = ', '.join(sorted(all_genres))
        
        status = request.form.get('status')
        rating_value = request.form.get('rating', '')
        # 确保评分值是浮点数
        try:
            rating = float(rating_value)
        except (ValueError, TypeError):
            rating = 0.0
        description = request.form.get('description', '')
        notes = request.form.get('notes', '')
        is_owned = request.form.get('is_owned') == 'on'
        
        # 查找要编辑的书籍
        books = get_all_books()
        book = next((b for b in books if b.get('id') == book_id), None)
        
        if book:
            # 保存旧数据
            old_added_date = book.get('added_date', '')
            old_is_favorite = book.get('is_favorite', False)
            old_cover_url = book.get('cover_url', '')
            
            # 更新书籍信息
            book.update({
                'title': title,
                'author': author,
                'year': year,
                'genre': genre,
                'status': status,
                'rating': rating,
                'description': description,
                'notes': notes,
                'is_owned': is_owned,
                # 保留原有字段
                'added_date': old_added_date,
                'is_favorite': old_is_favorite,
                'cover_url': old_cover_url
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
                    book['cover_url'] = f"/uploads/{unique_filename}"
            elif request.form.get('cover_url') != old_cover_url:
                # 如果URL已更改，更新封面URL
                book['cover_url'] = request.form.get('cover_url', '')
            
            # 保存到文件
            save_books(books)
            
            flash('图书已成功更新！', 'success')
            return redirect(url_for('book_detail', book_id=book_id))
        
        flash('未找到要编辑的图书。', 'danger')
        return redirect(url_for('books'))
    
    # 获取所有唯一的分类标签用于表单复选框
    all_books = get_all_books()
    unique_genres = set()
    for b in all_books:
        if b.get('genre'):
            genres = [g.strip() for g in b.get('genre').split(',')]
            for genre in genres:
                if genre:
                    unique_genres.add(genre)
    unique_genres = sorted(list(unique_genres))
    
    # 如果当前图书有分类，将其分割为列表
    book_genres = []
    if book and book.get('genre'):
        book_genres = [g.strip() for g in book.get('genre').split(',')]
    
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
        movie_data = {
            'title': request.form.get('title'),
            'director': request.form.get('director'),
            'cast': request.form.get('cast'),
            'year': request.form.get('year'),
            'genre': request.form.get('genre'),
            'poster_url': request.form.get('poster_url'),
            'description': request.form.get('description'),
            'rating': request.form.get('rating'),
            'status': request.form.get('status'),
            'notes': request.form.get('notes')
        }
        add_movie(movie_data)
        return redirect(url_for('movies'))
    return render_template('movie_form.html')

@app.route('/movies/edit/<string:movie_id>', methods=['GET', 'POST'])
def edit_movie_route(movie_id):
    movie = get_movie(movie_id)
    if request.method == 'POST':
        # 保存原有数据
        old_created_at = movie.get('created_at', '')
        old_is_favorite = movie.get('is_favorite', False)
        
        movie_data = {
            'id': movie_id,
            'title': request.form.get('title'),
            'director': request.form.get('director'),
            'cast': request.form.get('cast'),
            'year': request.form.get('year'),
            'genre': request.form.get('genre'),
            'poster_url': request.form.get('poster_url'),
            'description': request.form.get('description'),
            'rating': request.form.get('rating'),
            'status': request.form.get('status'),
            'notes': request.form.get('notes'),
            # 保留原有字段
            'created_at': old_created_at,
            'is_favorite': old_is_favorite
        }
        update_movie(movie_id, movie_data)
        flash('电影已成功更新！', 'success')
        return redirect(url_for('movie_detail', movie_id=movie_id))
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
        music_data = {
            'album': request.form.get('album'),
            'artist': request.form.get('artist'),
            'status': request.form.get('status', 'unlistened'),
            'year': request.form.get('year'),
            'genre': request.form.get('genre'),
            'cover_url': request.form.get('cover_url'),
            'rating': request.form.get('rating'),
            'notes': request.form.get('notes')
        }
        add_music(music_data)
        return redirect(url_for('music'))
    return render_template('music_form.html')

@app.route('/music/edit/<string:music_id>', methods=['GET', 'POST'])
def edit_music_route(music_id):
    music_item = get_music(music_id)
    if request.method == 'POST':
        # 保存原有数据
        old_created_at = music_item.get('created_at', '')
        old_is_favorite = music_item.get('is_favorite', False)
        
        music_data = {
            'id': music_id,
            'album': request.form.get('album'),
            'artist': request.form.get('artist'),
            'status': request.form.get('status', 'unlistened'),
            'year': request.form.get('year'),
            'genre': request.form.get('genre'),
            'cover_url': request.form.get('cover_url'),
            'rating': request.form.get('rating'),
            'notes': request.form.get('notes'),
            # 保留原有字段
            'created_at': old_created_at,
            'is_favorite': old_is_favorite
        }
        update_music(music_id, music_data)
        flash('音乐已成功更新！', 'success')
        return redirect(url_for('music_detail', music_id=music_id))
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
    owned_books = [book for book in all_books if book.get('is_owned', False)]
    
    # 获取所有书籍中的唯一分类标签（支持逗号分隔的多个标签）
    unique_genres = set()
    for book in all_books:
        if book.get('genre'):
            # 分割每本书的分类，并去除首尾空格
            genres = [g.strip() for g in book.get('genre').split(',')]
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