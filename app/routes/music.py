@bp.route('/')
def index():
    # ... existing code ...
    
    # 修改筛选栏格式，使其与电影、图书页面一致
    return render_template('music/index.html', 
                          musics=musics, 
                          filter_options=filter_options,
                          current_filter=current_filter)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    form = MusicForm()
    if form.validate_on_submit():
        music = Music(
            # 不再使用title字段，或者设置为默认值
            # title=form.title.data,
            album=form.album.data,  # 使用专辑作为主要标识
            # ... 其他字段 ...
        )
        db.session.add(music)
        db.session.commit()
        flash('音乐添加成功！')
        return redirect(url_for('music.index'))
    return render_template('music/music_form.html', form=form, title="添加音乐")

# 同样修改编辑函数
@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    music = Music.query.get_or_404(id)
    form = MusicForm()
    if form.validate_on_submit():
        # 不再更新title字段
        # music.title = form.title.data
        music.album = form.album.data
        # ... 其他字段更新 ...
        
        db.session.commit()
        flash('音乐更新成功！')
        return redirect(url_for('music.index'))
    elif request.method == 'GET':
        # 不再设置title字段
        # form.title.data = music.title
        form.album.data = music.album
        # ... 其他字段设置 ...
    
    return render_template('music/music_form.html', form=form, title="编辑音乐")
# ... existing code ... 