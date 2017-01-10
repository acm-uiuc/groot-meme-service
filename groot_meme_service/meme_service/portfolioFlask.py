#import operator
import dbFunctions
from flask import Flask, request
app = Flask(__name__)


@app.route("/", methods=['GET'])
def getProjects():
    return "default return statement"

#This is an endpoint to view up to ten memes from the database, as json with sender, score, and url.
@app.route("/browse", methods=['GET'])
def browse():
    if 'order' in request.args:
        order = request.args.get('order')
        memes = dbFunctions.getBrowseMemes(order=order)
    else:
        memes = dbFunctions.getBrowseMemes()
    return memes


#endpoint to view up to ten memes by requested user
@app.route("/query", methods=['GET'])
def query():
    if 'user' in request.args:
        order = 'random'
        if 'order' in request.args:
            order = request.args.get('order')
        filtered = dbFunctions.getFilteredMemes(user=request.args.get('user'), order=order)
        return filtered
    return ('', 400)  # Bad request error


#endpoint to upload a meme
@app.route("/upload", methods=['POST', 'GET'])
def upload():
    title = 'STALE MEME'
    if 'title' in request.args:
        title = request.args.get('title')
    if 'user' in request.args and 'url' in request.args:
        dbFunctions.addMeme(user=request.args.get('user'), url=request.args.get('url'), title=title)
        return ('', 200) # Meme added successfully
    return ('', 400) # Bad request error


if __name__ == "__main__":
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port, debug = True)
    app.run(debug = True)