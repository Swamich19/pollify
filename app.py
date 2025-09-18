import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------
# Logging setup
# ---------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---------------------------------------
# Base for SQLAlchemy
# ---------------------------------------
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# ---------------------------------------
# Flask app config
# ---------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://neondb_owner:npg_CiF6t3JRObDz@ep-green-mode-adiqj2jo-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SERVER_NAME"] = "whwt5f1w-5000.inc1.devtunnels.ms"
# ---------------------------------------
# Initialize extensions
# ---------------------------------------
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes after app + db init
from routes import *

# ---------------------------------------
# Setup database and default admin
# ---------------------------------------
with app.app_context():
    import models
    db.create_all()

    from models import User
    from werkzeug.security import generate_password_hash

    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        try:
            admin_user = User(
                username="admin",
                email="admin@pollify.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True,
            )
            db.session.add(admin_user)
            db.session.commit()
            logging.info("✅ Admin user created (username: admin, password: admin123)")
        except Exception as e:
            logging.error(f"❌ Failed to create admin user: {e}")
    else:
        logging.info("ℹ️ Admin user already exists.")

# ---------------------------------------
# Run app
# ---------------------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
