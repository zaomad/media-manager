from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, URLField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, URL, NumberRange

class MusicForm(FlaskForm):
    # 专辑作为主要字段
    album = StringField('专辑', validators=[DataRequired(message='请输入专辑名称')])
    artist = StringField('艺术家', validators=[DataRequired(message='请输入艺术家名称')])
    year = IntegerField('发行年份', validators=[Optional(), NumberRange(min=1900, max=2100)])
    genre = StringField('类型/分类', validators=[Optional()])
    cover = URLField('封面图片URL', validators=[Optional(), URL(message='请输入有效的URL')])
    rating = SelectField('评分', choices=[('未评分', '未评分'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], validators=[Optional()])
    notes = TextAreaField('笔记/评论', validators=[Optional()])
    submit = SubmitField('提交') 