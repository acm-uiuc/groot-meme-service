# -*- coding: utf-8 -*-
'''
Copyright © 2016, ACM@UIUC
This file is part of the Groot Project.
The Groot Project is open source software, released under the University of
Illinois/NCSA Open Source License.  You should have received a copy of
this license in a file with the distribution.
'''

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Meme(db.Model):
    __tablename__ = "memes"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), unique=True)
    netid = db.Column(db.String(100))
    title = db.Column(db.String(100))
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    votes = db.relationship('Vote', backref='meme', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'created_at': self.created_at.isoformat(),
            'title': self.title,
            'author': self.netid,
            'votes': self.votes.count()
        }


class Vote(db.Model):
    __tablename__ = "votes"
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(100), index=True)
    meme_id = db.Column(db.Integer, db.ForeignKey('memes.id'))
