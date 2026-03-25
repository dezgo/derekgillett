from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="Derek Gillett")
    tagline = db.Column(db.String(500), nullable=False, default="")
    footer_text = db.Column(db.String(200), nullable=False, default="")
    meta_description = db.Column(db.String(500), nullable=False, default="")


class SocialLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    icon_svg = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500), nullable=True)
    icon_svg = db.Column(db.Text, nullable=False)
    icon_bg_color = db.Column(db.String(100), nullable=False, default="rgba(74, 124, 255, 0.12)")
    icon_text_color = db.Column(db.String(100), nullable=False, default="var(--accent-blue)")
    tags = db.Column(db.String(500), nullable=False, default="")  # comma-separated
    sort_order = db.Column(db.Integer, nullable=False, default=0)
