from flask import Flask
import os

app = Flask(__name__, 
            static_folder='../static',
            template_folder='../templates')

# 确保数据目录存在
os.makedirs('../data', exist_ok=True)

# 设置密钥以便flash消息能够正常工作
app.secret_key = os.environ.get('SECRET_KEY', 'development_secret_key_123456789')

from app import routes 