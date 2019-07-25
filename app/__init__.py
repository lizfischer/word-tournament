from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import math

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
VOTE_BATCH_SIZE = 10

from app.models import Word, Match, Vote
from app import routes, models
import random


WORD_LIST = 'word-tournament.txt'
TEST_DATA = ['apple', 'orange', 'blue', 'red', 'summer', 'winter', 'druid', 'wizard']


# Read words from file into array
def init_data(file_name):
    with open(file_name, 'r') as f:
        words = f.readlines()
        words = [x.strip() for x in words]
    return words


# Populate database with words and initial matches
def init_matches(word_list):
    while word_list:  # removes words from array until empty
        pair = random.sample(word_list, k=2)
        word_list.remove(pair[0])
        word_list.remove(pair[1])

        word_1 = Word(word=pair[0], matched=True)
        word_2 = Word(word=pair[1], matched=True)
        db.session.add(word_1)
        db.session.add(word_2)

        match = Match(word_1=word_1.word, word_2=word_2.word)
        db.session.add(match)
    db.session.commit()


def reset_db():
    # User.query.delete()
    Vote.query.delete()
    Match.query.delete()
    Word.query.delete()
    db.session.commit()

    # init_matches(init_data(WORD_LIST))  # use real data
    init_matches(TEST_DATA)  # use test data


# Modify above function to taste and uncomment this line to reset the database
reset_db()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

