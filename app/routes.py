from flask import render_template, flash, redirect, url_for
from app import app, db, VOTE_BATCH_SIZE, NUM_ROUNDS
from flask_login import current_user, login_user, logout_user
from app.forms import LoginForm, RegistrationForm, VoteForm
from app.models import User, Match, Vote, Word
from wtforms import RadioField
from wtforms.validators import DataRequired
import math

FINAL_WINNER = None

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('vote'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If logged in, go to home!
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Make a form
    form = LoginForm()
    if form.validate_on_submit():
        # Look up the submitted username
        user = User.query.filter_by(username=form.username.data).first()
        # If it wasn't a valid user, prompt again
        if user is None or user.password != form.password.data:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # Log in a valid user and take them home!
        login_user(user, remember=form.remember_me.data)
        return redirect('/index')
    # Show the log in page the first time...
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    global FINAL_WINNER
    if FINAL_WINNER is not None:
        flash('Voting is done! The winner is "' + FINAL_WINNER + '"', 'info')
        return render_template('index.html')

    if not current_user.is_authenticated:
        redirect(url_for('login'))

    user_votes = [r for (r,) in Vote.query.with_entities(Vote.match).filter_by(user=current_user.id).all()]
    matches = Match.query.filter_by(finished=0).filter(Match.id.notin_(user_votes)).order_by(Match.round).limit(VOTE_BATCH_SIZE)

    if matches.count() < 1:
        flash('Nothing for you to vote on now. Try again later!', 'info')
        return render_template('index.html')

    class F(VoteForm):  # subclass for dynamic form population
        pass
    for match in matches:
        setattr(F, str(match.id), RadioField(choices=[(match.word_1, match.word_1), (match.word_2, match.word_2)],
                                             validators=[DataRequired()]))
    form = F()

    if form.validate_on_submit():
        for field in form:
            if field.type == "RadioField":
                # Register vote
                match_id = int(field.name)
                chosen_word = field.data
                v = Vote(match=match_id, user=current_user.id, vote=chosen_word)
                db.session.add(v)

                # Check vote count
                count = Vote.query.filter_by(match=match_id, vote=chosen_word).count()
                if count == 2:
                    # close match & set winner
                    match = Match.query.get(match_id)
                    match.finished = 1
                    match.winner = chosen_word

                    winner = Word.query.get(chosen_word)
                    Word.query.get(match.word_1).rounds_done += 1
                    Word.query.get(match.word_2).rounds_done += 1

                    # check if tournament is over
                    print(NUM_ROUNDS)
                    if winner.rounds_done >= NUM_ROUNDS:
                        FINAL_WINNER = chosen_word
                        db.session.commit()
                        return redirect(url_for('vote'))

                    # check if winner can be paired
                    unmatched = Word.query.filter_by(matched=0).filter_by(rounds_done=winner.rounds_done)
                    # pair winner OR set as winner to waiting.matched = 1
                    if unmatched.count() > 0:
                        pair_word = unmatched.first()
                        new_match = Match(round=int(match.round + 1), word_1=chosen_word, word_2=pair_word.word)
                        db.session.add(new_match)
                        winner.matched = True
                        pair_word.matched = True

                    else:
                        winner.matched = False
        db.session.commit()
        return redirect(url_for('vote'))

    return render_template('index.html', matches=matches, form=form)


@app.route('/myvotes')
def myvotes():
    user_votes = Vote.query.filter_by(user=current_user.id).all()
    data = []
    for vote in user_votes:
        match = Match.query.get(vote.match)
        highlight_index = 0
        if vote.vote == match.word_2:
            highlight_index = 1
        data.append([match.word_1, match.word_2, highlight_index])
    return render_template('my-votes.html', votes=data, count=len(user_votes))


@app.route('/tournament')
def tournament():
    data = {}
    starting_round = NUM_ROUNDS - 1
    starting_match = Match.query.filter_by(round=starting_round).first()
    tournament_recurse(data, starting_match, starting_round)

    for i in range(0, NUM_ROUNDS):
        # Add matches that didn't lead anywhere
        whole_round = Match.query.filter_by(round=i).all()
        for m in whole_round:
            if m not in data[i]:
                data[i].append(m)

        # add empties
        num_full = len(data[i])
        num_empty = 2**(NUM_ROUNDS - i - 1) - num_full
        for x in range(0, num_empty):
            data[i].append(None)

    return render_template('tournament.html', data=data)


def tournament_recurse(data, match, round):
    if not round in data:
        data[round] = []
    data[round].append(match)

    # If the match was None, try all possible points in the next round
    if not match:
        new_starts = Match.query.filter_by(round=round-1).all()
        for match in new_starts:
            tournament_recurse(data, match, round-1)
        return
    if round > 0:  # if there is a previous round
        words = [match.word_1, match.word_2]
        for word in words:
            prev_match = Match.query.filter_by(round=round-1).filter_by(winner=word).first()
            tournament_recurse(data, prev_match, round-1)

    return
