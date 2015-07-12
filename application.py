import os
from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CsrfProtect
from flask_oauthlib.client import OAuth, OAuthException
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

csrf = CsrfProtect()
csrf.init_app(app)

# Setup Oauth2 - https://github.com/lepture/flask-oauthlib
if os.environ.has_key('GOOGLE_ID') and os.environ.has_key('GOOGLE_SECRET'):
    # set app configuration variables to environment variables
    app.config['GOOGLE_ID'] = os.environ['GOOGLE_ID']
    app.config['GOOGLE_SECRET'] = os.environ['GOOGLE_SECRET']
else:
    # set to None if they're not available
    app.config['GOOGLE_ID'] = None
    app.config['GOOGLE_SECRET'] = None
oauth = OAuth(app)

from models import Base, User, Category, Music
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

if True:
    engine = create_engine(os.environ['DATABASE_URL'])
    Base.metadata.bind = engine

    DBSession = scoped_session(sessionmaker(bind=engine))
    db_session = DBSession()

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    db_session = SQLAlchemy(app)

base_uri = '/catalog/'
api_uri = base_uri + 'api/'
selected_category = None

# Define Remote Oauth Provider
google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Login with Google's Oauth
@app.route('/login')
def login():
    if app.config['GOOGLE_ID'] and app.config['GOOGLE_SECRET']:
        return google.authorize(callback=url_for('authorized', _external=True))
    else:
        flash('Whoops, Google ID and Secret are missing', 'warning')
        return redirect(url_for('index'))


# Logout User
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_token', None)
    flash('You\'ve been successfully logged out..', 'success')
    return redirect(url_for('index'))



# Handle data returned from Oauth provider
@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['user_token'] = (resp['access_token'], '')
    me           = google.get('userinfo')
    access_token = resp['access_token']
    name         = me.data['name']
    picture      = me.data['picture']

    # Check if user already exists on database
    user = db_session.query(User).filter_by(access_token=access_token).first()
    if user is None:

    	user = User(access_token, name, picture)

        db_session.add(user)

    # store access token into database
    user.access_token = access_token
    db_session.commit()

    # store user data on session
    session['user_id'] = user.id
    session['user_token'] = user.access_token
    session['user_name'] = user.name
    session['user_picture'] = user.picture

    flash('You\'re logged in!', 'success')
    return redirect(url_for('index'))



# If user is already logged in
@google.tokengetter
def get_google_oauth_token():
    return session.get('user_token')

# Query helper
def base_query():
    """ returns the list of categories and musics """
    categories = db_session.query(Category).all()
    musics = db_session.query(Music).all()
    return categories, musics


# Process any form
def process_form(form):
    """ Catch POST data sent by client """
    form = dict(form)
    if form['thumbnail_url'][0] == "": # If no thumbnail received then we use a default one
        form['thumbnail_url'][0] = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/300px-No_image_available.svg.png'
    if not form.has_key('featured'):
        form['featured'] = [False]
    else:
        form['featured'] = [True]
    music = Music(title=form['music_title'][0],
                    youtube_url=form['youtube_url'][0],
                    thumbnail_url=form['thumbnail_url'][0],
                    description=form['music_description'][0],
                    featured=form['featured'][0],
                    category_id=form['music_category'][0])
    return music

# Return: Boolean
def authenticated():
    """ returns whether or not the session user is authenticated """
    if session.has_key('user_id') and session.has_key('user_token'):
        user = db_session.query(User).filter_by(id=session['user_id']).first()
        if user:
            return user.access_token == session['user_token']
    return False

# Return: Boolean
def is_editable(music):
    """ returns whether the music is owned by the session user """
    if authenticated():
        if music.sender_id == None:
            return False
        else:
            return session.has_key('user_id') and music.sender_id == session['user_id']
    else:
        return False

# Load sample data from a json file
@app.route(base_uri+'seed')
def seed_database(fixture_filename='sample_data.json'):
    categories, _ = base_query()
    if len(categories) != 0:
        pass
    else:
        import json
        with open(fixture_filename, 'rb') as f:
            fixtures = json.load(f)
        seed_categories = fixtures['categories']
        for p in seed_categories:
            category = Category(name=p['name'])
            db_session.add(category)
        fetch_musics = fixtures['musics']
        for c in fetch_musics:
            music = Music(title=c['title'],
                            youtube_url=c['youtube_url'],
                            thumbnail_url=c['thumbnail_url'],
                            description=c['description'],
                            featured=c['featured'],
                            category_id=c['category_id'])
            db_session.add(music)
        try:
            db_session.commit()
            flash('Database populated.', 'warning')
        except Exception as e:
            flash('Something imploded. {}'.format(e), 'danger')
    return redirect(url_for('index'))

# Catalog same as Index
@app.route('/catalog')
@app.route('/')
def index():
    """ Main Page """
    # call seed function
    seed_database()
    categories, _ = base_query()
    featured_musics = db_session.query(Music).filter_by(featured=True).order_by(Music.title)
    count = featured_musics.count()
    return render_template('index_musics.html',
                           categories=categories, musics=featured_musics,
                           count=count,
                           title='Featured Musics', title_link=None,
                           logged_in=authenticated, editable=is_editable, selected=categories)


# Returns a Json response
@app.route(api_uri+'catalog.json', methods=['GET'])
def categories_api():
    """ returns JSON response of categories and items """
    categories, _ = base_query()
    items = db_session.query(Music).order_by(Music.title)
    return jsonify(categories=[p.serialize for p in categories], items=[i.serialize for i in items])


# Return: objects
@app.route(base_uri+'categories/<int:category_id>', methods=['GET'])
def main_musics(category_id):
    """ show music by category """
    selected_category = None
    selected_category = category_id
    categories, _ = base_query()
    try:
        category = db_session.query(Category).filter_by(id=category_id).one()
    except:
        flash('Whoops, nothing found :(', 'danger')
        return redirect(url_for('index'))
    category_musics = db_session.query(Music).filter_by(category_id=category_id).order_by(Music.title)
    count = category_musics.count()
    return render_template('index_musics.html',
                           categories=categories, musics=category_musics, count=count,
                           title=category.name, logged_in=authenticated, editable=is_editable, selected=category_id)


# Return: objects
@app.route(base_uri+'musics/<int:music_id>', methods=['GET'])
def view_music(music_id):
    """ single music view """
    categories, _ = base_query()
    try:
        music = db_session.query(Music).filter_by(id=music_id).one()
    except:
        flash('Whoops, nothing found :(', 'danger')
        return redirect(url_for('index'))
    return render_template('view_music.html',
                           categories=categories, music=music,
                           title=music.title,
                           logged_in=authenticated,
                           form_delete=url_for('delete_music', music_id=music.id),
                           editable=is_editable)


# Add new item form
@app.route(base_uri+'music/new', methods=['GET', 'POST'])
def new_music():
    """ handle new music """
    if not authenticated():
        return redirect(url_for('login'))
    categories, _ = base_query()
    if request.method == 'POST':
        music = process_form(request.form)
        music.sender_id = session['user_id']
        db_session.add(music)
        try:
            db_session.commit()
            flash('Your music has been added', 'success')
            return redirect(url_for('view_music', music_id=music.id))
        except Exception as e:
            flash('Something went wring. {}'.format(e), 'danger')
            return redirect(url_for('index'))
    else:
        music = {"id": None, "title": "", "youtube_url": "", "thumbnail_url": "",
                  "description": "", "featured": False, "category_id": None}
        return render_template('edit_music.html',
                               categories=categories, music=music,
                               title='New Music',
                               form_action=url_for('new_music'),
                               logged_in=authenticated)


# Edit item form
@app.route(base_uri+'musics/<int:music_id>/edit', methods=['GET', 'POST'])
def edit_music(music_id):
    """ handle music edit """
    categories, _ = base_query()
    music = db_session.query(Music).filter_by(id=music_id).one()
    if not authenticated():
        return redirect(url_for('login'))
    elif not is_editable(music):
        flash('You dont have permission to edit this music', 'warning')
        return redirect(url_for('view_music', music_id=music_id))
    if request.method == 'POST':
        new_music_params = process_form(request.form)

        music.title = new_music_params.title
        music.youtube_url = new_music_params.youtube_url
        music.thumbnail_url = new_music_params.thumbnail_url
        music.description = new_music_params.description
        music.featured = new_music_params.featured
        music.category_id = new_music_params.category_id
        db_session.add(music)
        try:
            db_session.commit()
            flash('Music has been saved', 'success')
        except Exception as e:
            flash('Something went wrong. {}'.format(e), 'danger')
        return redirect(url_for('view_music', music_id=music_id))
    else:
        return render_template('edit_music.html',
                               categories=categories, music=music,
                               title='Editing: ' + music.title,
                               form_action=url_for('edit_music', music_id=music_id),
                               logged_in=authenticated)


# Handle's item deletion
@app.route(base_uri+'musics/<int:music_id>/delete', methods=['GET', 'POST'])
def delete_music(music_id):
    """ handle music deletion """
    categories, _ = base_query()
    music = db_session.query(Music).filter_by(id=music_id).one()
    if not authenticated():
        return redirect(url_for('login'))
    elif not is_editable(music):
        flash('You dont have permission to do that', 'warning')
        return redirect(url_for('view_music', music_id=music_id))
    if request.method == 'POST':
        category = db_session.query(Category).filter_by(id=music.category_id).one()
        db_session.delete(music)
        try:
            db_session.commit()
            flash('Music was deleted successfully', 'success')
            return redirect(url_for('index_musics', category_id=category.id))
        except Exception as e:
            flash('Something went wrong. {}'.format(e), 'danger')
            return redirect(url_for('view_music', music_id=music.id))
    return redirect(url_for('view_music', music_id=music.id))


# Start listening on port: 80000
if __name__ == '__main__':
    app.debug = True;
    app.run(host='0.0.0.0', port=8000)
