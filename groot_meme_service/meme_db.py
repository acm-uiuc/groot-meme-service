import random
import time
from models import User, Meme

def addMeme(meme):
    current_time = time.time()
    new_meme = Meme(url,user,title,current_time)
    db.session.add(new_meme)
    db.session.commit()
    return 'success'


def getMemes(user=None, order='random'):
    if order == 'random':
        meme_list = db.session.query(Meme).all().order_by(func.random())
    elif order == 'latest':
        meme_list = db.session.query(Meme).all().order_by(Meme.time)
    elif order == 'top':
        meme_list = db.session.query(Meme).all().order_by(Meme.upvotes)
    elif order == 'rising':
        current_time = time.time()
        meme_list = db.session.query(Meme).all().order_by(Meme.upvotes / (current_time - Meme.time))
    if user:
       pass 

    memes = []
    for index in xrange(10):
        current_meme = meme_list[index]
        memes.append({'user': current_meme.user, 'url': current_meme.url, 'score': current_meme.score, 'title': current_meme.title})
    return memes
