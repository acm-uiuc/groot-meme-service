from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/meme_database'
db = SQLAlchemy(app)
import random
import time
import models
from models import *

####################################### commit data to db #####################################################
#@app.route('/upload', methods=['POST'])
def addMeme(url='',user='',title=''):
	current_time = time.time()
	new_meme = Meme(url,user,title,current_time)
	db.session.add(new_meme)
	db.session.commit()
	return 'success'

################################## retrieve data from db ##########################################################################
def getBrowseMemes(order='random'):
	if order == 'random':
		meme_list = db.session.query(Meme).all().order_by(func.random())
	elif order == 'latest':
		meme_list = db.session.query(Meme).all().order_by(Meme.time)
	elif order == 'top':
		meme_list = db.session.query(Meme).all().order_by(Meme.upvotes)
	elif order == 'rising':
		current_time = time.time()
		meme_list = db.session.query(Meme).all().order_by(Meme.upvotes / (current_time-Meme.time))

	memes = []
	for index in xrange(10):
		current_meme = meme_list[index]
		memes.append( {'user': current_meme.user, 'url': current_meme.url, 'score': current_meme.score, 'title': current_meme.title} )
	return memes


def getFilteredMemes(user=None, order='random'):
	if order == 'random':
		meme_list = db.session.query(Meme).all().order_by(func.random())
	elif order == 'latest':
		meme_list = db.session.query(Meme).all().order_by(Meme.time)
	elif order == 'top':
		meme_list = db.session.query(Meme).all().order_by(Meme.upvotes)
	elif order == 'rising':
		current_time = time.time()
		meme_list = db.session.query(Meme).all().order_by(Meme.upvotes / (current_time-Meme.time))
	meme_list = db.session.query(Meme).filter(user=user).all()
	
	memes = []
	for index in xrange(10):
		memes.append({'user': meme_list[index].user, 'url': meme_list[index].url, 'score': meme_list[index].score, 'title': meme_list[index].title})
	return memes



if __name__ == '__main__':
	app.debug = True
	app.run()