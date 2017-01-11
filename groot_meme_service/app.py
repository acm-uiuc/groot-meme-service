from flask import Flask, request, jsonify
from models import db, Meme
from settings import mysql
from flask_restful import reqparse
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
    mysql['user'],
    mysql['password'],
    mysql['host'],
    mysql['dbname']
)


@app.route("/memes", methods=['GET'])
def get_memes():
    ''' Endpoint for viewing memes '''
    order_funcs = {
        'random': func.random(),
        'latest': Meme.uploaded_at
    }
    parser = reqparse.RequestParser()
    parser.add_argument('order', choices=order_funcs.keys(), default='latest')
    parser.add_argument('user')
    args = parser.parse_args()

    memes = db.session.query(Meme).order_by(order_funcs[args.get('order')])

    if 'user' in request.args:
        memes = memes.filter_by(netid=request.args['user'])

    memes = memes.limit(25)

    return jsonify([m.to_dict() for m in memes])


@app.route("/memes/<int:meme_id>", methods=['GET'])
def get_meme(meme_id):
    meme = db.session.query(Meme).filter_by(id=meme_id).first()
    print meme
    if meme:
        return jsonify(meme.to_dict())
    else:
        return "No meme with id %s" % meme_id, 404


@app.route("/memes", methods=['POST'])
def upload():
    ''' Endpoint for uploading memes '''
    parser = reqparse.RequestParser()
    parser.add_argument('url', required=True)
    parser.add_argument('title')
    parser.add_argument('url')
    args = parser.parse_args()

    meme = Meme(
        url=args.url,
        title=args.title,
        netid=args.netid
    )
    db.session.add(meme)
    db.session.commit()
    return jsonify(meme.to_dict())

if __name__ == "__main__":
    db.init_app(app)
    db.create_all(app=app)
    app.run(debug=True)
