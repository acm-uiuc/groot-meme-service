from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Meme(db.Model):
    __tablename__ = "memes"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), unique=True)
    netid = db.Column(db.String(100))
    title = db.Column(db.String(100))
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    votes = db.relationship('Vote', backref='meme', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'created_at': self.created_at.isoformat(),
            'title': self.title,
            'netid': self.netid,
            'votes': len(self.votes.all())
        }


class Vote(db.Model):
    __tablename__ = "votes"
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(100))
    meme_id = db.Column(db.Integer, db.ForeignKey('memes.id'))
