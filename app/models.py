from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class Agent(UserMixin, db.Model):
    __tablename__ = 'agents'

    id = db.Column(db.Integer, primary_key=True)
    codename = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rank = db.Column(db.String(20), default='Recruit', nullable=False)
    xp = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Agent {self.codename}>'

@login_manager.user_loader
def load_user(agent_id):
    return Agent.query.get(int(agent_id))