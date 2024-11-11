#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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
    venues = Venue.query.all()
    data = []
    city_state_map = {}

    for venue in venues:
      key = (venue.city, venue.state)
      if key not in city_state_map:
        city_state_map[key] = []

      city_state_map[key].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
      })

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
    # Get the venue by ID
    venue = Venue.query.get(venue_id)

    # Retrieve the current time to filter shows
    current_time = datetime.now()

    # Query for past shows with artist details
    past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue.id,
        Show.start_time < current_time,
    ).with_entities(
        Artist.id.label('artist_id'),
        Artist.name.label('artist_name'),
        Artist.image_link.label('artist_image_link'),
        Show.start_time.label('start_time')
    ).all()

    # Query for upcoming shows with artist details
    upcoming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue.id,
        Show.start_time >= current_time,
    ).with_entities(
        Artist.id.label('artist_id'),
        Artist.name.label('artist_name'),
        Artist.image_link.label('artist_image_link'),
        Show.start_time.label('start_time')
    ).all()

    # Format show data for template
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
        "image_link": venue.image_link,
        "past_shows": [{
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        } for show in past_shows],
        "upcoming_shows": [{
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    # Render the venue data to the template
    return render_template('pages/show_venue.html', venue=venue_data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


# @app.route('/venues/create', methods=['GET', 'POST'])
# def create_venue_submission():
#     form = VenueForm()
#
#     if request.method == 'POST' and form.validate_on_submit():
#         try:
#             # Create a new Venue instance using form data
#             venue = Venue(
#                 name=form.name.data,
#                 city=form.city.data,
#                 state=form.state.data,
#                 address=form.address.data,
#                 phone=form.phone.data,
#                 genres=form.genres.data,
#                 facebook_link=form.facebook_link.data,
#                 image_link=form.image_link.data,
#                 website=form.website_link.data,
#                 seeking_talent=form.seeking_talent.data,
#                 seeking_description=form.seeking_description.data
#             )
#             db.session.add(venue)
#             db.session.commit()
#             flash(f'Venue "{form.name.data}" was successfully listed!', 'success')
#             return redirect(url_for('index'))  # Redirect to home page on success
#
#         except Exception as e:
#             db.session.rollback()
#             flash(f'An error occurred. Venue "{form.name.data}" could not be listed.', 'error')
#             print(e)
#
#         finally:
#             db.session.close()
#
#     else:
#         # Flash form errors if validation fails
#         flash('There were errors in your form. Please review and try again.', 'error')
#
#     # Redirect to home page even on errors
#     return redirect(url_for('index'))

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
    artists = Artist.query.all()
    data = []

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len([show for show in artist.shows if show.start_time > datetime.now()])
        })

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
    # Get the artist by ID
    artist = Artist.query.get(artist_id)

    # Retrieve the current time to filter shows
    current_time = datetime.now()

    # Query for past shows with venue details
    past_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist.id,
        Show.start_time < current_time,
    ).with_entities(
        Venue.id.label('venue_id'),
        Venue.name.label('venue_name'),
        Venue.image_link.label('venue_image_link'),
        Show.start_time.label('start_time')
    ).all()

    # Query for upcoming shows with venue details
    upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist.id,
        Show.start_time >= current_time,
    ).with_entities(
        Venue.id.label('venue_id'),
        Venue.name.label('venue_name'),
        Venue.image_link.label('venue_image_link'),
        Show.start_time.label('start_time')
    ).all()

    # Format artist data for the template
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
        "image_link": artist.image_link,
        "past_shows": [{
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "venue_image_link": show.venue_image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        } for show in past_shows],
        "upcoming_shows": [{
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "venue_image_link": show.venue_image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    # Render the artist data to the template
    return render_template('pages/show_artist.html', artist=artist_data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)

  if not artist:
    flash(f'Artist with ID {artist_id} not found.')
    return redirect(url_for('artists'))

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

  form = ArtistForm(obj=artist_data)
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  if not artist:
    flash(f'Artist with ID {artist_id} not found.')
    return redirect(url_for('artists'))

  try:
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

  form = VenueForm(obj=venue_data)
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  if not venue:
    flash(f'Venue with ID {venue_id} not found.')
    return redirect(url_for('venues'))

  try:
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
