from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from sqlalchemy import MetaData

metadata = MetaData(schema="mentoria")
db = SQLAlchemy(metadata=metadata)
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    #app = Flask(__name__)
    #app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
   # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///js-mentoria.db'
   # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   # app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
   # app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///js-mentoria.db')
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///js-mentoria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB


    #@app.route("/")
    #def home():
        #return "Aplicação rodando!"


    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.courses import courses_bp
    from app.routes.topics import topics_bp
    from app.routes.lessons import lessons_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(topics_bp)
    app.register_blueprint(lessons_bp)

    with app.app_context():
        db.create_all()

    return app
