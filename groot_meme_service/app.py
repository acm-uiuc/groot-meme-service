from flask import Flask, jsonify, abort
import os
import requests
from models import db, Meme
from settings import MYSQL, GROOT_ACCESS_TOKEN
from flask_restful import Resource, Api, reqparse, inputs
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
    MYSQL['user'],
    MYSQL['password'],
    MYSQL['host'],
    MYSQL['dbname']
)

PORT = 42069
DEBUG = os.environ.get('MEME_DEBUG', False)
SERVICES_URL = 'http://localhost:8000'

api = Api(app)


def authenticate_netid(token):
    url = '/'.join([SERVICES_URL, 'session', token])
    headers = {
        'Authorization': GROOT_ACCESS_TOKEN,
        'Accept': 'application/json'
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200 or 'token' not in r.json():
        raise ValueError("Who do you think you are? "
                         "Unable to authenticate token.")
    return r.json().get('user')['name']


def check_group_membership(netid, group):
    url = '/'.join([SERVICES_URL, 'groups', 'committees', group])
    headers = {
        'Authorization': GROOT_ACCESS_TOKEN
    }
    params = {
        'isMember': netid
    }
    r = requests.get(url, headers=headers, params=params)
    return r.json()['isValid']


def approve_meme_admin(netid):
    meme_groups = ['top4', 'admin', 'corporate']
    return any(check_group_membership(netid, g) for g in meme_groups)


class MemeListResource(Resource):
    def get(self):
        ''' Endpoint for viewing dank memes '''
        order_funcs = {
            'random': func.random(),
            'latest': Meme.created_at
        }
        parser = reqparse.RequestParser()
        parser.add_argument('order', choices=order_funcs.keys(),
                            default='latest', location='args')
        parser.add_argument('netid', location='args')
        args = parser.parse_args()

        memes = db.session.query(Meme).order_by(order_funcs[args.order])

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
        parser.add_argument('token', location='args', required=True,
                            dest='netid', type=authenticate_netid)
        args = parser.parse_args()

        # TODO: Meme Approval
        netid = authenticate_netid(args.token)

        if db.session.query(Meme).filter_by(url=args.url).first():
            return "This meme has already been submitted!", 400

        meme = Meme(
            url=args.url,
            title=args.title,
            netid=netid
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

    def delete(self, meme_id):
        ''' Endpoint for deleting a meme :'( '''
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='args', required=True,
                            dest='netid', type=authenticate_netid)
        args = parser.parse_args()
        if not approve_meme_admin(args.netid):
            return "Nice try memelord, but I can't let you do that.", 403
        meme = db.session.query(Meme).filter_by(id=meme_id).first()
        if meme:
            db.session.delete(meme)
            db.session.commit()
            return "Deleted meme %s" % meme_id
        else:
            return "No meme with id %s" % meme_id, 404


api.add_resource(MemeResource, '/memes/<int:meme_id>', endpoint='meme')
api.add_resource(MemeListResource, '/memes', endpoint='memes')
db.init_app(app)
db.create_all(app=app)


if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG)
