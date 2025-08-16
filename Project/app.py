from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
from models import db, User
from routes import init_routes
import os

def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = '请先登录'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 初始化路由
    init_routes(app)
    
    # 创建必要的目录
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('templates/errors', exist_ok=True)
    
    return app

def init_db():
    """初始化数据库"""
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员用户
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@medical.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("默认管理员用户已创建: admin/admin123")

if __name__ == '__main__':
    app = create_app()
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000) 