# word-tournament

## Running things
1. Set up a virtual environment for this project using your favorite environment manager (pipenv, virtualenv, conda...)
2. Make sure all the requirements are installed (`pip install -r requirements.txt` or similar)! 
3. From the top-level directory, `flask run`
4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Interacting with the database
We're using Flask's SQLAlchemy package for DB interaction. It abstracts a lot away, handling transactions etc. for you. 

Note: Currently, the db as-is on the master branch has some test users in the db already for use: liz, user2, user3, and user 4. All passwords are 1234.

I'll use the `Match` table for all my examples here, but you can do the same thing with other tables & column names.
### Basic queries
* Get all rows: `Match.query.all()` returns all matches
* Get the first result from a query: end with `.first()` instead of `.all()`
* Get all rows with a certain value in a column: `Match.query.filter_by(finished=True).all()` returns all matches with 
`True`/`1` in the `finished` column
* Return only a certain column: `Match.query.with_entities(Match.winner).all()` returns all matches, but only the winner column.
* Return specific column(s) and filter: `match.query.with_entities(Match.id, Match.winner).filter_by(finished=True).all()` 
returns the ID and winner of all finished matches.
* Get number of rows returned by a query: `Match.query.all().count()` 
 

### Accessing returned data
When you do `.all()`, you get an array of objects with column names as properties. You can iterate over a result and get 
data like this:
```
open_matches = Match.query.filter_by(finished=False).all()

for m in open_matches:
    match_id = m.id
    words = [m.word_1, m.word_2]
    round = m.round 
```   

## Getting data from the application to the view
Every page that needs data from the application has a function in `app/routes.py`. That function does the work to 
generate the data the page needs and handle database interaction, etc. It does everything but generate the HTML, basically.

At the end, each function directs the user somewhere. It either:
* redirects them to another page: `return redirect(url_for('login'))` or
* renders a page for the user: `return render_template('vote.html')`

To send data to a page view, pass further arguments to the `render_template()` function. For example:

In `app/routes.py`
```
    data = # some code getting all the votes a user submitted. 
    return render_template('my-votes.html', votes=data, num_votes=len(data))
```
In `app/templates/my-votes.html`
```
<p> Total votes: {{num_votes}} </p>
{% for v in votes %}
    <p>In the match between {{ v.word_1 }} and {{ v._word_2 }}, you picked {{ v.vote }}</p>
{% endfor %}
```

## File structure

### app
This folder holds most the good stuff. 
#### static
Javascript and CSS, and (if we had any) static website pages or images. Any web resources that don't need to get data from the application.

#### templates
HTML page templates that can take data from the application. Flask uses Jinja templating. For example:

```
{% for m in matches %} <!-- curly brace + % for basic python code (for, if, etc.) -->
<p>Match between {{ m.word_1 }} and {{ m.word_2 }}</p> <!-- double brace means print data here -->
{% endfor %} <!-- always end blocks with an end statement -->
```

##### Bootstrap
This folder has the basic Bootstrap templates that everything else inherits. 

##### base.html
All our pages inherit this. It includes js/css, sets title, and adds top bar to all pages.

##### Other pages
Other pages should be pretty self explanatory by their names.


#### \_\_init\_\_.py
This initializes the application & has the code to populate the database. If you want to reset the database on the next
run, uncomment the `reset_db()` call. You can modify the `reset_db()` function to only clear certain tables and/or to 
use different data. There is a small set of test data defined in the variable `TEST_DATA` at the top of the file.    

#### forms.py
Defines login, register, and voting forms. Voting form only kind of becuase it has to be dynamically generated... 
it's kind of hacky but it works.

#### models.py
Defines all the database models. Other places (especially `routes.py`) import from here in order to run DB queries.

#### routes.py
This is the workhorse! All the important stuff is here! Each page (or URL if you'd rather think of it that way, since 
there doesn't have to be an associated HTML page) is defined as a "route" `@app.route('/some_route_name')` and each route has
an associated function. That function does all the work you want to happen on the server side when a user visits 
`http://wordtournamentsite.com/some_route_name`. These functions pass data on to the templates as needed to show the
user data/handle interaction/etc.

### migrations
This is database stuff. You shouldn't have to touch anything in here directly.

### config.py
Some basic DB setup information, like URI and secret key.

### requirements.txt
Python library requirements. Before doing anything, be sure to `pip install -r requirements.txt`
(or similar).

### word-app.db
The actual database file.

### word-tournament.txt
List of words downloaded from Google Drive. `__init__.py` reads this file to populate the database. 
