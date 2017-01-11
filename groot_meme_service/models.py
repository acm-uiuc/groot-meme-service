from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Meme(db.Model):
    __tablename__ = "memes"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), unique=True)
    netid = db.Column(db.String(100))
    title = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'uploaded_at': self.uploaded_at.isoformat(),
            'title': self.title,
            'netid': self.netid
        }
