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
FINAL_WINNER = None
NUM_WORDS = 0
NUM_ROUNDS = 0

from app.models import Word, Match
from app import routes, models
import random

WORD_LIST = 'word-tournament.txt'
TEST_DATA = ['apple', 'orange', 'blue', 'red', 'summer', 'winter', 'druid', 'wizard']

def init_data(file_name):
    with open(file_name, 'r') as f:
        words = f.readlines()
        words = [x.strip() for x in words]
    return words


def init_matches(word_list):
    L = word_list.copy()  # for non-destructive removal
    while L:
        pair = random.sample(L, k=2)
        L.remove(pair[0])
        L.remove(pair[1])

        word_1 = Word(word=pair[0], matched=True)
        word_2 = Word(word=pair[1], matched=True)
        db.session.add(word_1)
        db.session.add(word_2)

        match = Match(word_1=word_1.word, word_2=word_2.word)
        db.session.add(match)
    db.session.commit()

    global NUM_WORDS
    global NUM_ROUNDS
    NUM_WORDS = Word.query.count()
    NUM_ROUNDS = int(math.log(NUM_WORDS, 2))


#init_matches(init_data(WORD_LIST))
#init_matches(TEST_DATA)
