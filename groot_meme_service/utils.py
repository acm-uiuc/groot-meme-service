from flask import make_response, jsonify


def send_error(message, code=400):
    return make_response(jsonify(dict(error=message)), code)
