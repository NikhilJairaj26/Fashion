"""
Database models for the GlamDiva application
User (auth), UserProfile (styler), WardrobeItem (closet)
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# -----------------------------
# User
# -----------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('ix_users_email', 'email'),
        db.Index('ix_users_name', 'name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    wardrobe_items = db.relationship(
        'WardrobeItem',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    profile = db.relationship(
        'UserProfile',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.email}>'


# -----------------------------
# UserProfile
# -----------------------------
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    __table_args__ = (
        db.Index('ix_user_profiles_user_id', 'user_id', unique=True),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        unique=True,
        nullable=False,
        index=True
    )

    # Styler attributes
    skin_tone = db.Column(db.String(50))    # e.g., 'very fair', 'medium', 'deep'
    undertone = db.Column(db.String(50))    # 'cool', 'warm', 'neutral'
    eye_color = db.Column(db.String(50))    # e.g., 'brown', 'green', 'blue'
    hair_color = db.Column(db.String(50))   # e.g., 'black', 'brown'
    occasion = db.Column(db.String(20))     # NEW: 'work','casual','party','wedding','festive','sports','custom'

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='profile')

    def __repr__(self) -> str:
        return f'<UserProfile user_id={self.user_id}>'


# -----------------------------
# WardrobeItem
# -----------------------------
class WardrobeItem(db.Model):
    __tablename__ = 'wardrobe_items'
    __table_args__ = (
        db.Index('ix_wardrobe_items_user', 'user_id'),
        db.Index('ix_wardrobe_items_name', 'name'),
        db.Index('ix_wardrobe_items_category', 'category'),
        db.Index('ix_wardrobe_items_created', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)    # e.g., 'Top', 'Bottom'
    color = db.Column(db.String(60))                       # e.g., 'Navy Blue'
    notes = db.Column(db.String(255))
    image_url = db.Column(db.String(255))                  # optional future

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='wardrobe_items')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'category': self.category,
            'color': self.color,
            'notes': self.notes,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f'<WardrobeItem {self.name} user_id={self.user_id}>'
