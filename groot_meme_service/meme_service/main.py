from flask import Flask, request
from flask.json import jsonify
import os
from database import db_session, init_db, User, Meme

# create new application
app = Flask(__name__)
init_db()

# create endpoints
@app.route('/browse', methods=['GET'])
def browse():
    """
    This is an endpoint to view up to ten random memes from the database,
    sent as a json formatted as array of dictionaries with sender, score, and url.
    """
    try:
        indices = random.sample(xrange( len(Meme.query.all()) ), 10)
    except ValueError:
        indices = range(0, len(Meme.query.all()) )
    meme_objects = []
    for index in indices:
        current_meme = Meme.query.all()[index]
        meme_objects.append( {'user': current_meme.user, 'url': current_meme.url, 'score': current_meme.score} )
    return jsonify(meme_objects)

@app.route('/query', methods=['GET'])
def query():
    """
    This is an endpoint to view a random meme by the specified author
    """
    if 'user' in request.args:
        filtered = Meme.query.filter( Meme.user=request.args.get('user') )
        index = random.randint(0, filtered.count()-1)
        meme_object = {'user': filtered[index].user, 'url': filtered[index].url, 'score': filtered[index].score}
        return jsonify(meme_object)
    return ('', 400)

@app.route('upload', methods=['POST'])
def upload():
    """
    This is an endpoint to upload memes from the client to the groot server
    """
    if 'user' in request.args and 'url' in request.args:
        # add url validation later
        val = URLValidator(verify_exists=True)
        try:
            val( request.args.get('url') )  # throws ValidationError if url does not exist
    
        meme_object = Meme(user=request.args.get('user'), score=0, url=request.args.get('url'))
        db_session.add(meme_object)
        db_session.commit()
        return ('', 200)
    return ('', 400)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.run()