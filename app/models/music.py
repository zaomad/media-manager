class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # title字段可能仍需保留用于数据库兼容性，但不再通过表单填写
    # title = db.Column(db.String(100), nullable=True)  # 可以设为nullable=True
    album = db.Column(db.String(255), nullable=False)  # 确保专辑是必填的
    
    # 如果有单曲相关字段，可以移除或标记为不使用
    # single = db.Column(db.Boolean, default=False)  # 可以注释或删除此行
    
    # ... existing code ... 