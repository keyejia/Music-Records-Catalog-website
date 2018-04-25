from flask import (Flask, 
                   render_template, 
                   request, 
                   redirect, 
                   jsonify, 
                   url_for, 
                   flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Albums, Genre, User
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///albums.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "record website"

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='', redirect_uri = '')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(data["email"])
    if not user_id:
    	user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = "width: 300px;'\
			  'height:300px;'\
			  'border-radius: 150px;'\
			  '-webkit-border-radius: 150px;'\
			  '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


 # DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected') 
        return redirect('/genre')
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#Add user info into database
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

#Get user info from database
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

#Get user id from database
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# JSON APIs to view genre Information
@app.route('/genre/<int:genre_id>/album/JSON')
def genrealbumJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    items = session.query(Albums).filter_by(
        genre_id=genre_id).all()
    return jsonify(albumItems=[i.serialize for i in items])


@app.route('/genre/<int:genre_id>/album/<int:album_id>/JSON')
def albumItemJSON(genre_id, album_id):
    album_Item = session.query(Albums).filter_by(id=album_id).one()
    return jsonify(album_Item=album_Item.serialize)


@app.route('/genre/JSON')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(genres=[r.serialize for r in genres])


# Show all Genre
@app.route('/')
@app.route('/genre/')
def showGenre():
    genres = session.query(Genre).order_by(asc(Genre.name))
    if 'username' not in login_session:
        return render_template('publicgenre.html', genre=genres)
    else:
        return render_template('genre.html', genre=genres)

#Create a new Genre
@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGenre = Genre(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newGenre)
        flash('New Genre %s Successfully Created' % newGenre.name)
        session.commit()
        return redirect(url_for('showGenre'))
    else:
        return render_template('newGenre.html')

# Edit a Genre
@app.route('/genre/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    editedGenre = session.query(
        Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedGenre.user_id != login_session['user_id']:
    	flash('You are not authorized to edit this Genre')
    	return redirect(url_for('showGenre'))
    if request.method == 'POST':
        if request.form['name']:
            editedGenre.name = request.form['name']
            flash('Genre Successfully Edited %s' % editedGenre.name)
            return redirect(url_for('showGenre'))
    else:
        return render_template('editgenre.html', genre=editedGenre)


# Delete a Genre
@app.route('/genre/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    genreToDelete = session.query(
        Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if genreToDelete.user_id != login_session['user_id']:
    	flash('You are not authorized to delete this Genre')
    	return redirect(url_for('showGenre'))
    if request.method == 'POST':
        session.delete(genreToDelete)
        flash('%s Successfully Deleted' % genreToDelete.name)
        session.commit()
        return redirect(url_for('showGenre'))
    else:
        return render_template('deletegenre.html', genre=genreToDelete)

# Show a genre albums
@app.route('/genre/<int:genre_id>/')
@app.route('/genre/<int:genre_id>/albums/')
def showAlbums(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    albums = session.query(Albums).filter_by(
        genre_id=genre_id).all()
    if 'username' not in login_session:
        return render_template('publicalbums.html', albums=albums, genre=genre)
    else:
        return render_template('albums.html', albums=albums, genre=genre)

# Create a new album
@app.route('/genre/<int:genre_id>/albums/new/', methods=['GET', 'POST'])
def newAlbum(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Albums).filter_by(id=genre_id).one()
    if request.method == 'POST':
        newAlbum = Albums(name=request.form['name'], 
        				  artist=request.form['artist'], 
        				  year=request.form['year'], 
        				  description=request.form['description'], 
        				  image_address=request.form['image_address'], 
        				  genre_id=genre_id, 
        				  user_id=login_session['user_id'])
        session.add(newAlbum)
        session.commit()
        flash('New Album %s Successfully Created' % (newAlbum.name))
        return redirect(url_for('showAlbums', genre_id=genre_id))
    else:
        return render_template('newalbum.html', genre_id=genre_id)

# Edit a album item
@app.route('/genre/<int:genre_id>/albums/<int:album_id>/edit', methods=['GET', 'POST'])
def editalbum(genre_id, album_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedAlbum = session.query(Albums).filter_by(id=album_id).one()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if login_session['user_id'] != editedAlbum.user_id:
    	flash('You are not authorized to edit this Album')
    	return redirect(url_for('showAlbums', genre_id=genre_id))
    if request.method == 'POST':
        if request.form['name']:
            editedAlbum.name = request.form['name']
        if request.form['artist']:
            editedAlbum.artist = request.form['artist']
        if request.form['year']:
            editedAlbum.year = request.form['year']
        if request.form['description']:
            editedAlbum.description = request.form['description']
        if request.form['image_address']:
            editedAlbum.image_address = request.form['image_address']
        flash('Album was Successfully Edited')
        return redirect(url_for('showAlbums', genre_id=genre_id))
    else:
        return render_template('editalbum.html', 
								genre_id=genre_id, 
								album_id=album_id, 
								item=editedAlbum)

# Delete a album item
@app.route('/genre/<int:genre_id>/albums/<int:album_id>/delete', methods=['GET', 'POST'])
def deletealbum(genre_id, album_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    itemToDelete = session.query(Albums).filter_by(id=album_id).one()
    if login_session['user_id'] != itemToDelete.user_id:
    	flash('You are not authorized to delete this Album')
    	return redirect(url_for('showAlbums', genre_id=genre_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Album Successfully Deleted')
        return redirect(url_for('showAlbums', genre_id=genre_id))
    else:
        return render_template('deletealbum.html', item=itemToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)