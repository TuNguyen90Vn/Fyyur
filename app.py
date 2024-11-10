#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # Add any additional fields such as genres, website, etc.
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Query all venues, grouped by city and state
    venues = Venue.query.all()
    data = []
    city_state_map = {}

    for venue in venues:
      # Group venues by city and state
      key = (venue.city, venue.state)
      if key not in city_state_map:
        city_state_map[key] = []

      city_state_map[key].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
      })

    # Transform city_state_map into a structured list for rendering
    for location, venue_list in city_state_map.items():
      data.append({
        "city": location[0],
        "state": location[1],
        "venues": venue_list
      })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues_list = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(venues_list),
        "data": [{"id": venue.id, "name": venue.name} for venue in venues_list]
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    # Return structured data here; this could also render a template
    return render_template('pages/show_venue.html', venue=venue)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        data = request.form
        new_venue = Venue(
            name=data['name'],
            city=data['city'],
            state=data['state'],
            address=data['address'],
            phone=data['phone'],
            genres=request.form.getlist('genres'),
            facebook_link=data['facebook_link'],
            website=data.get('website'),
            seeking_talent=bool(data.get('seeking_talent')),
            seeking_description=data.get('seeking_description')
        )
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + data['name'] + ' was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    if venue:
      db.session.delete(venue)
      db.session.commit()
      flash(f'Venue {venue.name} was successfully deleted!')
    else:
      flash(f'Venue with ID {venue_id} not found.')
  except Exception as e:
    db.session.rollback()
    flash(f'An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()

  return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Query all artists from the database
    artists = Artist.query.all()
    data = []

    # Prepare data for each artist, including a count of upcoming shows
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len([show for show in artist.shows if show.start_time > datetime.now()])
        })

    # Render the artists page with the list of artists
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(artists),
        "data": [{"id": artist.id, "name": artist.name} for artist in artists]
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    # Render template or return structured data
    return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)

  if not artist:
    flash(f'Artist with ID {artist_id} not found.')
    return redirect(url_for('artists'))

  # Populate the form with the current artist data
  artist_data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  # Render the edit form template with artist data
  form = ArtistForm(obj=artist_data)
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  if not artist:
    flash(f'Artist with ID {artist_id} not found.')
    return redirect(url_for('artists'))

  try:
    # Update the artist’s details with form data
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form.get('website')
    artist.seeking_venue = bool(request.form.get('seeking_venue'))
    artist.seeking_description = request.form.get('seeking_description')
    artist.image_link = request.form.get('image_link')

    db.session.commit()
    flash(f'Artist {artist.name} was successfully updated!')
  except Exception as e:
    db.session.rollback()
    flash(f'An error occurred. Artist could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)

  if not venue:
    flash(f'Venue with ID {venue_id} not found.')
    return redirect(url_for('venues'))

  # Populate the form with the current venue data
  venue_data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  # Render the edit form template with venue data
  form = VenueForm(obj=venue_data)
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  if not venue:
    flash(f'Venue with ID {venue_id} not found.')
    return redirect(url_for('venues'))

  try:
    # Update the venue’s details with form data
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form.get('website')
    venue.seeking_talent = bool(request.form.get('seeking_talent'))
    venue.seeking_description = request.form.get('seeking_description')
    venue.image_link = request.form.get('image_link')

    db.session.commit()
    flash(f'Venue {venue.name} was successfully updated!')
  except Exception as e:
    db.session.rollback()
    flash(f'An error occurred. Venue could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        data = request.form
        new_artist = Artist(
            name=data['name'],
            city=data['city'],
            state=data['state'],
            phone=data['phone'],
            genres=request.form.getlist('genres'),
            facebook_link=data['facebook_link'],
            website=data.get('website'),
            seeking_venue=bool(data.get('seeking_venue')),
            seeking_description=data.get('seeking_description')
        )
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + data['name'] + ' was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        data = request.form
        new_show = Show(
            artist_id=data['artist_id'],
            venue_id=data['venue_id'],
            start_time=data['start_time']
        )
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
