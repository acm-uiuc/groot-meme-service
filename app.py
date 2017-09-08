# -*- coding: utf-8 -*-
'''
Copyright © 2017, ACM@UIUC
This file is part of the Groot Project.
The Groot Project is open source software, released under the University of
Illinois/NCSA Open Source License.  You should have received a copy of
this license in a file with the distribution.
'''

from flask import Flask, jsonify
import flask
import os
import requests
from models import db, Meme, Vote, React
from settings import MYSQL, GROOT_ACCESS_TOKEN, GROOT_SERVICES_URL
from flask_restful import Resource, Api, reqparse
from sqlalchemy.sql.expression import func, text
from utils import (send_error, send_success, unknown_meme_response,
                   validate_imgur_link)
from datetime import datetime
import logging
logger = logging.getLogger('groot_meme_service')

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

api = Api(app)


def authenticate_netid(token):
    url = '/'.join([GROOT_SERVICES_URL, 'session', token])
    headers = {
        'Authorization': GROOT_ACCESS_TOKEN,
        'Accept': 'application/json'
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200 or 'token' not in r.json():
        logger.info("Denying authentication for token %s" % token)
        raise ValueError("Who do you think you are? "
                         "Unable to authenticate token.")
    netid = r.json().get('user')['name']
    flask.g.netid = netid
    logger.info("Authenticated user %s" % netid)
    return netid


def check_group_membership(netid, group):
    url = '/'.join([GROOT_SERVICES_URL, 'groups', 'committees', group])
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


def reject_failed_admin():
    logger.info("Rejecting admin request from %s" % flask.g.netid)
    return send_error("Nice try memelord, "
                      "but I can't let you do that.", 403)


def requires_admin(func):
    def decorated(*args, **kwargs):
        if not approve_meme_admin(flask.g.netid):
            return reject_failed_admin()
        logger.info("Authenticated admin request from %s" % flask.g.netid)
        return func(*args, **kwargs)
    return decorated


def require_token_auth(func):
    def wrapper(*args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('Meme-Token', location='headers',
                            required=True, dest='token',
                            type=authenticate_netid)
        args = parser.parse_args()
        return func(*args, **kwargs)
    return wrapper


class MemeListResource(Resource):
    @require_token_auth
    def get(self):
        ''' Endpoint for viewing dank memes '''
        order_queries = {
            'random': Meme.query.order_by(func.random()),
            'latest': Meme.query.order_by(Meme.created_at.desc()),
            'hottest': Meme.query.outerjoin(Vote).group_by(Meme.id).order_by(
                (func.timestampdiff(
                    text('second'),
                    datetime.now(),
                    Meme.created_at) /
                 func.count(Vote.id)).desc()
                ),
            'top': Meme.query.outerjoin(Vote).group_by(Meme.id).order_by(
                func.count(Vote.id).desc(), Meme.created_at.desc()),
            'unapproved': Meme.query.filter_by(approved=False).order_by(
                Meme.created_at)
        }
        parser = reqparse.RequestParser()
        parser.add_argument('order', choices=order_queries.keys(),
                            default='latest', location='args')
        parser.add_argument('author', location='args')
        parser.add_argument('page', location='args', default=1,
                            type=int)
        args = parser.parse_args()

        memes = order_queries[args.order]

        if args.order == 'unapproved':
            if not approve_meme_admin(flask.g.netid):
                return reject_failed_admin()
        else:
            memes = memes.filter(Meme.approved)

        if args.author:
            memes = memes.filter_by(netid=args.author)

        page = memes.paginate(page=args.page, per_page=24)

        memes_dict = [m.to_dict() for m in page.items]

        # Check to see if token user has voted on each meme
        for meme in memes_dict:
            meme['upvoted'] = Vote.query.filter_by(
                netid=flask.g.netid,
                meme_id=meme['id']
                ).first() is not None

        logger.info("Serving memes to %s from page %s" %
                    (flask.g.netid, args.page))

        return jsonify({
            'memes': memes_dict,
            'page': args.page,
            'num_pages': page.pages,
            'next_page': page.next_num if page.has_next else None,
            'prev_page': page.prev_num if page.has_prev else None
        })

    @require_token_auth
    def post(self):
        ''' Endpoint for registering a meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('url', required=True)
        parser.add_argument('title')
        args = parser.parse_args()

        if Meme.query.filter_by(url=args.url).first():
            return send_error("This meme has already been submitted! "
                              "Lay off the stale memes.", 400)
        try:
            args.url = validate_imgur_link(args.url)
        except ValueError as e:
            logger.info('%s sent an invalid imgur link.' % flask.g.netid)
            return send_error(str(e))

        meme = Meme(
            url=args.url,
            title=args.title,
            netid=flask.g.netid
        )
        db.session.add(meme)
        db.session.commit()
        logger.info("%s created new meme with id %s" %
                    (flask.g.netid, meme.id))
        return jsonify(meme.to_dict())


class MemeResource(Resource):
    @require_token_auth
    def get(self, meme_id):
        ''' Endpoint for accessing a single meme '''
        meme = Meme.query.filter_by(id=meme_id).first()
        if meme:
            meme_dict = meme.to_dict()
            meme_dict['upvoted'] = Vote.query.filter_by(
                netid=flask.g.netid,
                meme_id=meme_id
                ).first() is not None
            logger.info("Serving %s meme %s" % (flask.g.netid, meme_id))
            return jsonify(meme_dict)
        else:
            return unknown_meme_response(meme_id)

    @require_token_auth
    @requires_admin
    def delete(self, meme_id):
        ''' Endpoint for deleting a meme :'( '''
        meme = Meme.query.filter_by(id=meme_id).first()
        if meme:
            db.session.delete(meme)
            db.session.commit()
            logger.info("%s deleted meme %s" % (flask.g.netid, meme_id))
            return "Deleted meme %s. ;_;7" % meme_id
        else:
            return unknown_meme_response(meme_id)


class MemeApprovalResource(Resource):
    @require_token_auth
    @requires_admin
    def put(self, meme_id):
        meme = Meme.query.filter_by(id=meme_id).first()
        if not meme:
            return unknown_meme_response(meme_id)
        meme.approved = True
        db.session.add(meme)
        db.session.commit()
        logger.info("%s approved meme %s" % (flask.g.netid, meme_id))
        return send_success("Approved meme %s" % meme_id)


class MemeVotingResource(Resource):
    @require_token_auth
    def delete(self, meme_id, vote_type=1):
        ''' Remove your vote for the requested meme '''
        netid = flask.g.netid

        vote = Vote.query.filter_by(
            netid=netid, meme_id=meme_id).first()
        if vote:
            db.session.delete(vote)
            db.session.commit()
            logger.info("Deleted vote for %s by %s" % (flask.g.netid, meme_id))
            return send_success("Deleted vote for %s" % meme_id)
        else:
            logger.info("%s tried to delete non-existant vote for  %s" %
                        (flask.g.netid, meme_id))
            return send_error("You haven't voted for meme %s" % meme_id)

    @require_token_auth
    def put(self, meme_id, vote_type=1):
        ''' Cast your vote for the requested meme '''
        netid = flask.g.netid

        if not Meme.query.filter_by(id=meme_id).first():
            return unknown_meme_response(meme_id)

        if not vote_type>=0 and vote_type<len(list(React)):
            return unknown_react_response(vote_type)

        vote = Vote.query.filter_by(
            netid=netid, meme_id=meme_id).first()
        if not vote:
            vote = Vote(netid=netid, meme_id=meme_id, vote_type=React(vote_type))
        else:
            vote.vote_type=React(vote_type)

        db.session.add(vote)
        db.session.commit()
        logger.info("Logged vote for %s by %s of type %s" % (flask.g.netid, meme_id, React(vote_type)))
        return send_success("Cast vote for %s" % meme_id)


class MemeRandomResource(Resource):
    def get(self):
        ''' Public resource for getting a random meme '''
        return Meme.query.filter_by(approved=True).order_by(
            func.random()).first().to_dict()


api.add_resource(MemeResource, '/memes/<int:meme_id>', endpoint='meme')
api.add_resource(MemeListResource, '/memes', endpoint='memes')
api.add_resource(MemeApprovalResource, '/memes/<int:meme_id>/approve')
api.add_resource(MemeVotingResource, '/memes/<int:meme_id>/<int:vote_type>/vote')
api.add_resource(MemeRandomResource, '/memes/random')
db.init_app(app)
db.create_all(app=app)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
