from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "library.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    from .models import User, Book, Transaction    #python relative imports
    with app.app_context():
        create_database()

    from .views import users, User1
    login_manager = LoginManager(app)
    login_manager.login_view = 'views.home'

    @login_manager.user_loader
    def load_user(user_id):
        return users.get("admin") if user_id == "1" else None

    return app

def create_database():
    if not path.exists('RFID PROJECT PYTHON CODE/instance/' + DB_NAME):
        db.create_all()
        print("Database Created")  