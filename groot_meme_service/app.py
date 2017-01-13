# -*- coding: utf-8 -*-
'''
Copyright © 2016, ACM@UIUC
This file is part of the Groot Project.
The Groot Project is open source software, released under the University of
Illinois/NCSA Open Source License.  You should have received a copy of
this license in a file with the distribution.
'''

from flask import Flask, jsonify
import flask
import os
import requests
from models import db, Meme, Vote
from settings import MYSQL, GROOT_ACCESS_TOKEN
from flask_restful import Resource, Api, reqparse, inputs
from sqlalchemy.sql.expression import func
from utils import send_error, send_success

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    MYSQL['user'],
    MYSQL['password'],
    MYSQL['host'],
    MYSQL['dbname']
)
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=UTF-8'

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


def requires_admin(func):
    def decorated(*args, **kwargs):
        if not approve_meme_admin(flask.g.netid):
            return send_error("Nice try memelord, "
                              "but I can't let you do that.", 403)
        return func(*args, **kwargs)
    return decorated


@app.before_request
def authenticate_token():
    parser = reqparse.RequestParser()
    parser.add_argument('token', location='args', required=True,
                        dest='netid', type=authenticate_netid)
    args = parser.parse_args()
    flask.g.netid = args.netid


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
        parser.add_argument('author', location='args')
        parser.add_argument('page', location='args', default=1,
                            type=int)
        args = parser.parse_args()

        memes = Meme.query.order_by(order_funcs[args.order])

        if args.author:
            memes = memes.filter_by(netid=args.author)

        page = memes.filter(Meme.approved != 0).paginate(
            page=args.page, per_page=24)

        memes_dict = [m.to_dict() for m in page.items]

        # Check to see if token user has voted on each meme
        for meme in memes_dict:
            meme['upvoted'] = Vote.query.filter_by(
                netid=flask.g.netid,
                meme_id=meme['id']
                ).first() is not None

        return jsonify({
            'memes': memes_dict,
            'page': args.page,
            'num_pages': page.pages,
            'next_page': page.next_num if page.has_next else None,
            'prev_page': page.prev_num if page.has_prev else None
        })

    def post(self):
        ''' Endpoint for registering a meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('url', required=True,
                            type=inputs.regex('https?:\/\/.*\.(?:png|jpg)'))
        parser.add_argument('title')
        args = parser.parse_args()

        if Meme.query.filter_by(url=args.url).first():
            return send_error("This meme has already been submitted! "
                              "Lay off the stale memes.", 400)

        meme = Meme(
            url=args.url,
            title=args.title,
            netid=flask.g.netid
        )
        db.session.add(meme)
        db.session.commit()
        return jsonify(meme.to_dict())


class MemeResource(Resource):
    def get(self, meme_id):
        ''' Endpoint for accessing a single meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='args', required=False,
                            dest='netid', type=authenticate_netid)
        args = parser.parse_args()
        meme = Meme.query.filter_by(id=meme_id).first()
        if meme:
            meme_dict = meme.to_dict()
            meme_dict['upvoted'] = Vote.query.filter_by(
                netid=flask.g.netid,
                meme_id=meme_id
                ).first() is not None
            return jsonify(meme_dict)
        else:
            return send_error("No meme with id %s" % meme_id)

    @requires_admin
    def delete(self, meme_id):
        ''' Endpoint for deleting a meme :'( '''
        meme = Meme.query.filter_by(id=meme_id).first()
        if meme:
            db.session.delete(meme)
            db.session.commit()
            return "Deleted meme %s. ;_;7" % meme_id
        else:
            return send_error("No meme with id %s" % meme_id)


class MemeApprovalResource(Resource):
    @requires_admin
    def put(self, meme_id):
        meme = Meme.query.filter_by(id=meme_id).first()
        if not meme:
            return send_error("No meme with id %s" % meme_id)
        meme.approved = True
        db.session.add(meme)
        db.session.commit()
        return send_success("Approved meme %s" % meme_id)


class MemeUnapprovedResource(Resource):
    @requires_admin
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', location='args', default=1,
                            type=int)
        args = parser.parse_args()
        page = Meme.query.filter_by(approved=0).paginate(
            page=args.page, per_page=24)

        return jsonify({
            'memes': [m.to_dict() for m in page.items],
            'page': args.page,
            'num_pages': page.pages,
            'next_page': page.next_num if page.has_next else None,
            'prev_page': page.prev_num if page.has_prev else None
        })


class MemeVotingResource(Resource):
    def delete(self, meme_id):
        ''' Remove your vote for the requested meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='args', required=True,
                            dest='netid', type=authenticate_netid)
        netid = parser.parse_args().netid

        vote = Vote.query.filter_by(
            netid=netid, meme_id=meme_id).first()
        if vote:
            db.session.delete(vote)
            db.session.commit()
            return send_success("Deleted vote for %s" % meme_id)
        else:
            return send_error("You haven't voted for meme %s" % meme_id)

    def put(self, meme_id):
        ''' Cast your vote for the requested meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='args', required=True,
                            dest='netid', type=authenticate_netid)
        netid = parser.parse_args().netid

        if not Meme.query.filter_by(id=meme_id).first():
            return send_error("No meme with id %s" % meme_id)

        vote = Vote.query.filter_by(
            netid=netid, meme_id=meme_id).first()
        if not vote:
            vote = Vote(netid=netid, meme_id=meme_id)
        db.session.add(vote)
        db.session.commit()
        return send_success("Cast vote for %s" % meme_id)


api.add_resource(MemeResource, '/memes/<int:meme_id>', endpoint='meme')
api.add_resource(MemeListResource, '/memes', endpoint='memes')
api.add_resource(MemeApprovalResource, '/memes/<int:meme_id>/approve')
api.add_resource(MemeUnapprovedResource, '/memes/unapproved')
api.add_resource(MemeVotingResource, '/memes/vote/<int:meme_id>')
db.init_app(app)
db.create_all(app=app)


if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG)
