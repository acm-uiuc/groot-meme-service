'''
Copyright © 2016, ACM@UIUC
This file is part of the Groot Project.
The Groot Project is open source software, released under the University of
Illinois/NCSA Open Source License.  You should have received a copy of
this license in a file with the distribution.
'''

from flask import make_response, jsonify


def send_error(message, code=400):
    return make_response(jsonify(dict(error=message)), code)


def send_success(message, code=200):
    return make_response(jsonify(dict(message=message)), code)
