from flask import Flask
from RAG.config import Config
from RAG.app import routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 确保设置了 secret_key 以支持 session
    if not app.config.get('SECRET_KEY'):
        app.secret_key = 'your_default_secret_key'  # 如果 Config 中没有设置 SECRET_KEY，则使用默认值

    app.register_blueprint(routes.bp)

    return app