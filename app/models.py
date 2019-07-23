import random
from app import db, login
from flask_login import UserMixin


class User (UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(45), index=True, unique=True)
    password = db.Column(db.String(45))

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Word(db.Model):
    word = db.Column(db.String(45), primary_key=True)
    rounds_done = db.Column(db.Integer, default=0)
    matched = db.Column(db.Boolean, default=0)

    def __repr__(self):
        return 'Word {}'.format(self.word)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    round = db.Column(db.Integer, default=0)
    finished = db.Column(db.Boolean, default=0)
    word_1 = db.Column(db.String(45), db.ForeignKey('word.word'))
    word_2 = db.Column(db.String(45), db.ForeignKey('word.word'))
    winner = db.Column(db.String(45), db.ForeignKey('word.word'))

    def __repr__(self):
        return 'Match {}, {}'.format(self.word_1, self.word_2)


class Vote(db.Model):
    match = db.Column(db.Integer, db.ForeignKey('match.id'), primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    vote = db.Column(db.String(45), db.ForeignKey('word.word'))

    def __repr__(self):
        return 'Vote {}, {}, {}'.format(self.user, self.match, self.vote)


