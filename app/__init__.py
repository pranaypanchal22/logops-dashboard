from flask import Flask
from .db import close_db, init_db
from .routes import bp

def create_app():
    app = Flask(__name__)
    init_db()

    app.register_blueprint(bp)

    app.teardown_appcontext(close_db)
    return app
