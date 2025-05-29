def add_book(book_data):
    """添加新书籍"""
    books = get_all_books()
    
    # 为新书籍分配ID
    new_id = 1
    if books:
        max_id = max(int(book['id']) for book in books if 'id' in book)
        new_id = max_id + 1
    
    # 确保添加时间字段
    if 'added_date' not in book_data:
        from datetime import datetime
        book_data['added_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # 确保is_favorite字段
    if 'is_favorite' not in book_data:
        book_data['is_favorite'] = False
    
    # 确保is_owned字段
    if 'is_owned' not in book_data:
        book_data['is_owned'] = True  # 默认为拥有
    
    # 设置ID
    book_data['id'] = new_id
    
    # 添加到列表
    books.append(book_data)
    
    # 保存到文件
    save_books(books)
    
    return new_id

def update_book(book_id, updated_data):
    """更新书籍信息"""
    books = get_all_books()
    
    # 查找要更新的书籍
    for book in books:
        if book.get('id') == book_id:
            # 保存原有的添加时间和收藏状态
            if 'added_date' not in updated_data and 'added_date' in book:
                updated_data['added_date'] = book['added_date']
            
            if 'is_favorite' not in updated_data and 'is_favorite' in book:
                updated_data['is_favorite'] = book['is_favorite']
                
            # 更新书籍数据
            book.update(updated_data)
            break
    
    # 保存到文件
    save_books(books)
    
    return True 