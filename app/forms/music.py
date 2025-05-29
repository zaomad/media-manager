from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class MusicForm(FlaskForm):
    # ... existing code ...
    
    # 确保专辑是必填项
    album = StringField('专辑', validators=[DataRequired(message='请输入专辑名称')])
    
    # 移除单曲相关字段
    # single = BooleanField('单曲')  # 可以注释或删除此行
    
    # ... existing code ... 