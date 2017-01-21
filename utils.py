# -*- coding: utf-8 -*-
'''
Copyright © 2017, ACM@UIUC
This file is part of the Groot Project.
The Groot Project is open source software, released under the University of
Illinois/NCSA Open Source License.  You should have received a copy of
this license in a file with the distribution.
'''

from flask import make_response, jsonify
import flask
import logging
import re
import requests
logger = logging.getLogger(__name__)

imgur_re = re.compile(
    r'https?://?(\w+\.)?imgur.com/((\w*\d*)+)(\.[a-zA-Z]{3})?$')


def send_error(message, code=400):
    return make_response(jsonify(dict(error=message)), code)


def send_success(message, code=200):
    return make_response(jsonify(dict(message=message)), code)


def unknown_meme_response(meme_id):
    logger.info("%s tried to access a nonexistant meme (%s)" %
                (flask.g.netid, meme_id))
    return send_error("No meme with id %s" % meme_id)


def validate_imgur_link(url):
    if not url.startswith('http'):
        url = 'https://%s' % url
    match = re.search(imgur_re, url)
    if match:
        extension = match.groups()[-1]
        if extension is None:
            # Even if the image isn't a jpg, imgur will still serve the correct
            # image if any extension provided
            url += '.jpg'
        r = requests.head(url)
        if r.status_code != 200:
            raise ValueError("URL appears to be invalid.")
        return url
    elif '/a/' in url:
        raise ValueError("Imgur albums not supported.")
    elif '/gallery/' in url:
        raise ValueError("Imgur galleries not supported.")
    else:
        raise ValueError("Invalid imgur URL.")
