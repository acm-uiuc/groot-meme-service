from flask import Flask, jsonify
from models import db, Meme
from settings import mysql
from flask_restful import Resource, Api, reqparse, inputs
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
    mysql['user'],
    mysql['password'],
    mysql['host'],
    mysql['dbname']
)
api = Api(app)


class MemeListResource(Resource):
    def get(self):
        ''' Endpoint for viewing dank memes '''
        order_funcs = {
            'random': func.random(),
            'latest': Meme.created_at
        }
        parser = reqparse.RequestParser()
        parser.add_argument('order', choices=order_funcs.keys(),
                            default='latest')
        parser.add_argument('netid')
        args = parser.parse_args()

        memes = db.session.query(Meme).order_by(order_funcs[args.get('order')])

        if args.netid:
            memes = memes.filter_by(netid=args.netid)

        memes = memes.limit(25)

        return jsonify([m.to_dict() for m in memes])

    def post(self):
        ''' Endpoint for registering a meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('url', required=True,
                            type=inputs.regex('https?:\/\/.*\.(?:png|jpg)'))
        parser.add_argument('title')
        parser.add_argument('netid')
        args = parser.parse_args()

        meme = Meme(
            url=args.url,
            title=args.title,
            netid=args.netid
        )
        db.session.add(meme)
        db.session.commit()
        return jsonify(meme.to_dict())


class MemeResource(Resource):
    def get(self, meme_id):
        ''' Endpoint for accessing a single meme '''
        meme = db.session.query(Meme).filter_by(id=meme_id).first()
        print meme
        if meme:
            return jsonify(meme.to_dict())
        else:
            return "No meme with id %s" % meme_id, 404

api.add_resource(MemeResource, '/memes/<int:meme_id>', endpoint='meme')
api.add_resource(MemeListResource, '/memes', endpoint='memes')
db.init_app(app)
db.create_all(app=app)


if __name__ == "__main__":
    app.run(debug=True)
