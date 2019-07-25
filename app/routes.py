from flask import render_template, flash, redirect, url_for
from app import app, db, VOTE_BATCH_SIZE
from flask_login import current_user, login_user, logout_user
from app.forms import LoginForm, RegistrationForm, VoteForm
from app.models import User, Match, Vote, Word
from wtforms import RadioField
from wtforms.validators import DataRequired
import math

FINAL_WINNER = None
NUM_WORDS = Word.query.count()
NUM_ROUNDS = int(math.log(NUM_WORDS, 2))


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
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Check if the tournament is over
    global FINAL_WINNER
    if FINAL_WINNER is not None:
        flash('Voting is done! The winner is "' + FINAL_WINNER + '"', 'info')
        return render_template('vote.html')

    # Get matches for this user
    user_votes = [r for (r,) in Vote.query.with_entities(Vote.match).filter_by(user=current_user.id).all()]
    matches = Match.query.filter_by(finished=0).filter(Match.id.notin_(user_votes)).order_by(Match.round).limit(VOTE_BATCH_SIZE)

    if matches.count() < 1:
        flash('Nothing for you to vote on now. Try again later!', 'info')
        return render_template('vote.html')

    # Make voting form
    class F(VoteForm):  # subclass for dynamic form population
        pass
    for match in matches:
        setattr(F, str(match.id), RadioField(choices=[(match.word_1, match.word_1), (match.word_2, match.word_2)],
                                             validators=[DataRequired()]))
    form = F()

    # Process form input
    if form.validate_on_submit():
        for field in form:
            if field.type == "RadioField":  # ignores initial hidden field & submit field
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
        # save your work!
        db.session.commit()
        # send the user on their way
        return redirect(url_for('vote'))

    return render_template('vote.html', matches=matches, form=form)


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


# TOURNAMENT STATUS PAGE
@app.route('/tournament')
def tournament():

    # Get voting activity for all users, and put in an easier-to-read structure to send to the template
    votes_query = db.engine.execute("SELECT User.username, count(*) as total FROM User INNER JOIN Vote ON Vote.user=User.id GROUP BY User.username")
    voter_activity = [{"user": row[0], "num_votes": row[1]} for row in votes_query]

    # Get match stats
    finished_matches = Match.query.filter_by(finished=True).count()
    open_matches = Match.query.filter_by(finished=False).count()
    latest_pending_round = Match.query.filter_by(finished=True).order_by(Match.round.desc()).first().round + 1  # db.engine.execute("SELECT Match.round FROM Match ORDER BY round DESC LIMIT(1)")
    earliest_pending_round = Match.query.filter_by(finished=False).order_by(Match.round).first().round + 1

    # Send all this data to the template!
    return render_template('tournament-status.html', voter_activity=voter_activity,
                           finished_matches=finished_matches, open_matches=open_matches,
                           latest_pending_round=latest_pending_round, earliest_pending_round=earliest_pending_round,
                           total_rounds=NUM_ROUNDS)
