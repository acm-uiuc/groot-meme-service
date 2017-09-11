# -*- coding: utf-8 -*-
'''
Copyright © 2017, ACM@UIUC
This file is part of the Groot Project.
The Groot Project is open source software, released under the University of
Illinois/NCSA Open Source License.  You should have received a copy of
this license in a file with the distribution.
'''

from flask import Flask, jsonify, request
import os
from models import db, Meme, Vote, React
from settings import MYSQL, IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET
from flask_uploads import UploadSet, configure_uploads
from imgurpython import ImgurClient
from flask_restful import Resource, Api, reqparse
from sqlalchemy.sql.expression import func, text
from utils import (send_error, send_success, unknown_meme_response,
                   unknown_react_response, validate_imgur_link)
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

imgur_images = UploadSet('ImageUploads',
                         ('jpg', 'png', 'gif'),
                         default_dest=lambda app: app.root_path)
configure_uploads(app, (imgur_images))
imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)

api = Api(app)


class MemeListResource(Resource):
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
        parser.add_argument('netid', location='args')
        parser.add_argument('page', location='args', default=1,
                            type=int)
        args = parser.parse_args()

        memes = order_queries[args.order]

        if args.order != 'unapproved':
            memes = memes.filter(Meme.approved)

        if args.author:
            memes = memes.filter_by(netid=args.author)

        page = memes.paginate(page=args.page, per_page=24)

        memes_dict = [m.to_dict() for m in page.items]

        # Check to see if token user has voted on each meme
        if args.netid:
            for meme in memes_dict:
                meme['upvoted'] = Vote.query.filter_by(
                    netid=args.netid,
                    meme_id=meme['id']
                    ).first() is not None

        logger.info("Serving memes to %s from page %s" %
                    (args.netid, args.page))

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
        parser.add_argument('url')
        parser.add_argument('title')
        parser.add_argument('netid', required=True)
        args = parser.parse_args()
        image_url = None

        if 'photo' in request.files:
            # Save file sent in request
            fname = imgur_images.save(request.files['photo'])

            # Upload to imgur
            try:
                uploaded = imgur_client.upload_from_path(fname)
                image_url = uploaded.get('link')
            except:
                send_error("Failed to upload file.", 500)

            # Delete local file
            os.remove(fname)
        if Meme.query.filter_by(url=args.url).first():
            return send_error("This meme has already been submitted! "
                              "Lay off the stale memes.", 400)
        elif args.url:
            image_url = args.url

        if not image_url:
            return send_error("Must submit a URL or upload image", 400)
        try:
            image_url = validate_imgur_link(image_url)
        except ValueError as e:
            logger.info('%s sent an invalid imgur link.' % args.netid)
            return send_error(str(e))

        meme = Meme(
            url=image_url,
            title=args.title,
            netid=args.netid
        )
        db.session.add(meme)
        db.session.commit()
        logger.info("%s created new meme with id %s" %
                    (args.netid, meme.id))
        return jsonify(meme.to_dict())


class MemeResource(Resource):
    def get(self, meme_id):
        ''' Endpoint for accessing a single meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('netid')
        args = parser.parse_args()

        meme = Meme.query.filter_by(id=meme_id).first()
        if meme:
            meme_dict = meme.to_dict()
            if args.netid:
                meme_dict['upvoted'] = Vote.query.filter_by(
                    netid=args.netid,
                    meme_id=meme_id
                    ).first() is not None
            return jsonify(meme_dict)
        else:
            return unknown_meme_response(meme_id)

    def delete(self, meme_id):
        ''' Endpoint for deleting a meme :'( '''
        meme = Meme.query.filter_by(id=meme_id).first()
        if meme:
            db.session.delete(meme)
            db.session.commit()
            return "Deleted meme %s. ;_;7" % meme_id
        else:
            return unknown_meme_response(meme_id)


class MemeApprovalResource(Resource):
    def put(self, meme_id):
        meme = Meme.query.filter_by(id=meme_id).first()
        if not meme:
            return unknown_meme_response(meme_id)
        meme.approved = True
        db.session.add(meme)
        db.session.commit()
        return send_success("Approved meme %s" % meme_id)


class MemeVotingResource(Resource):
    def delete(self, meme_id):
        ''' Remove your vote for the requested meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('netid', required=True)
        args = parser.parse_args()

        vote = Vote.query.filter_by(
            netid=args.netid, meme_id=meme_id).first()
        if vote:
            db.session.delete(vote)
            db.session.commit()
            logger.info("Deleted vote for %s by %s" % (args.netid, meme_id))
            return send_success("Deleted vote for %s" % meme_id)
        else:
            logger.info("%s tried to delete non-existant vote for  %s" %
                        (args.netid, meme_id))
            return send_error("You haven't voted for meme %s" % meme_id)

    def put(self, meme_id):
        ''' Cast your vote for the requested meme '''
        parser = reqparse.RequestParser()
        parser.add_argument('netid', required=True)
        args = parser.parse_args()

        if not request.json or 'vote_type' not in request.json:
            vote_type = 'like'
        else:
            vote_type = request.json['vote_type']

        if not Meme.query.filter_by(id=meme_id).first():
            return unknown_meme_response(meme_id)

        try:
            vote_type_enum = React(vote_type)
        except KeyError:
            return unknown_react_response(vote_type)

        vote = Vote.query.filter_by(
            netid=args.netid, meme_id=meme_id).first()
        if not vote:
            vote = Vote(
                netid=args.netid, meme_id=meme_id, vote_type=vote_type_enum
            )
        else:
            vote.vote_type = vote_type_enum

        db.session.add(vote)
        db.session.commit()
        logger.info("Logged vote for %s by %s of type %s" %
                    (args.netid, meme_id, React(vote_type)))
        return send_success("Cast vote for %s" % meme_id)


class MemeRandomResource(Resource):
    def get(self):
        ''' Public resource for getting a random meme '''
        return Meme.query.filter_by(approved=True).order_by(
            func.random()).first().to_dict()


api.add_resource(MemeResource, '/memes/<int:meme_id>', endpoint='meme')
api.add_resource(MemeListResource, '/memes', endpoint='memes')
api.add_resource(MemeApprovalResource, '/memes/<int:meme_id>/approve')
api.add_resource(MemeVotingResource, '/memes/<int:meme_id>/vote')
api.add_resource(MemeRandomResource, '/memes/random')
db.init_app(app)
db.create_all(app=app)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
