from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import meme_db


@app.route("/browse", methods=['GET'])
def browse():
    ''' Endpoint for viewing memes '''
    if 'order' in request.args:
        order = request.args.get('order')
        memes = meme_db.getBrowseMemes(order=order)
    else:
        memes = meme_db.getBrowseMemes()
    return memes


@app.route("/query", methods=['GET'])
def query():
    ''' Endpoint for searching memes '''
    if 'user' in request.args:
        order = 'random'
        if 'order' in request.args:
            order = request.args.get('order')
        filtered = meme_db.getFilteredMemes(
            user=request.args.get('user'),
            order=order)
        return filtered
    return ('', 400)  # Bad request error


@app.route("/upload", methods=['POST', 'GET'])
def upload():
    ''' Endpoint for uploading memes '''
    title = 'STALE MEME'
    if 'title' in request.args:
        title = request.args.get('title')
    if 'user' in request.args and 'url' in request.args:
        meme_db.addMeme(
            request.args.get('user'),
            request.args.get('url'),
            title)
        return ('', 200)  # Meme added successfully
    return ('', 400)  # Bad request error


if __name__ == "__main__":
    app.run(debug=True)
