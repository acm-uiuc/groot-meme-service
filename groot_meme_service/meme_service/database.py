from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base
Base.metadata.create_all(engine)

class User(db.Model):
    __tablename__ = "users"
    name = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


class Meme(models.Model):
    __tablename__ = "memes"
    url = db.Column(db.String(100), primary_key=True)
    user = db.Column(db.String(100))
    upvotes = db.Column

    def __str__(self):
        return "%s %s %s" % (self.name, self.url, self.score)
