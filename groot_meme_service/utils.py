# -*- coding: utf-8 -*-
'''
Copyright © 2016, ACM@UIUC
This file is part of the Groot Project.
The Groot Project is open source software, released under the University of
Illinois/NCSA Open Source License.  You should have received a copy of
this license in a file with the distribution.
'''

from flask import make_response, jsonify
import flask
import logging
logger = logging.getLogger(__name__)


def send_error(message, code=400):
    return make_response(jsonify(dict(error=message)), code)


def send_success(message, code=200):
    return make_response(jsonify(dict(message=message)), code)


def unknown_meme_response(meme_id):
    logger.info("%s tried to access a nonexistant meme (%s)" %
                (flask.g.netid, meme_id))
    return send_error("No meme with id %s" % meme_id)
