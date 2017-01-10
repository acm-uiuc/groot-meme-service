from dbFunctions import db
############################################################ DATABASE MODELS ##############################################################

class User(db.Model):
    __tablename__ = "users"
    email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name, email):
        self.email = email
        self.name = name


class Meme(db.Model):
    __tablename__ = "memes"
    url = db.Column(db.String(120), primary_key=True)
    user = db.Column(db.String(100))
    upvotes = db.Column(db.Integer)
    title = db.Column(db.String(100))
    time = db.Column(db.Integer)

    def __init__(self,url,user,title,time):
        self.url = url
        self.user = user
        self.upvotes = 0
        self.title = title
        self.time = time

###########################################################################################