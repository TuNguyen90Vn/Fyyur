from datetime import datetime
from flask_wtf import FlaskForm as Form, FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.fields.simple import URLField
from wtforms.validators import DataRequired, AnyOf, URL, Optional
import enum
import re
from wtforms import ValidationError

class Genre(enum.Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    HipHop = 'Hip-Hop'
    HeavyMetal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    MusicalTheatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    RB = 'R&B'
    Reggae = 'Reggae'
    Rock = 'Rock'
    Soul = 'Soul'
    Swing = 'Swing'
    Other = 'Other'

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]

class State(enum.Enum):
    AL = 'AL'
    AK = 'AK'
    AZ = 'AZ'
    AR = 'AR'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DE = 'DE'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    IA = 'IA'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    ME = 'ME'
    MD = 'MD'
    MA = 'MA'
    MI = 'MI'
    MN = 'MN'
    MS = 'MS'
    MO = 'MO'
    MT = 'MT'
    NE = 'NE'
    NV = 'NV'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NY = 'NY'
    NC = 'NC'
    ND = 'ND'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VT = 'VT'
    VA = 'VA'
    WA = 'WA'
    WV = 'WV'
    WI = 'WI'
    WY = 'WY'

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]

def is_valid_phone(form, field):
    phone_number = field.data
    regex = re.compile(r'^(?:\d{10}|\d{3}[-. ]\d{3}[-. ]\d{4})$')

    if not regex.match(phone_number):
        raise ValidationError(
            "Invalid phone number format. Expected formats: 1234567890, 123-456-7890, 123.456.7890, or 123 456 7890.")

def is_valid_genres(form, field):
    if not set(field.data).issubset(dict(Genre.choices()).keys()):
        raise ValidationError('Invalid genres.')

def is_valid_state(form, field):
    if not set(field.data).issubset(dict(State.choices()).keys()):
        raise ValidationError('Invalid state.')

class BaseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', choices=State.choices(), validators=[Optional()])
    phone = StringField('Phone', validators=[Optional(), is_valid_phone])
    genres = SelectMultipleField('Genres', choices=Genre.choices(), validators=[DataRequired(), is_valid_genres])
    facebook_link = URLField('Facebook Link', validators=[Optional(), URL()])
    image_link = URLField('Image Link', validators=[Optional(), URL()])
    website_link = URLField('Website Link', validators=[Optional(), URL()])
    seeking_description = StringField('Seeking Description', validators=[Optional()])

# VenueForm inherits from BaseForm and adds address and seeking_talent
class VenueForm(BaseForm):
    address = StringField('Address', validators=[DataRequired()])
    seeking_talent = BooleanField('Looking for Talent')

# ArtistForm inherits from BaseForm and adds seeking_venue
class ArtistForm(BaseForm):
    seeking_venue = BooleanField('Looking for Venues')

# ShowForm with specific fields for show creation
class ShowForm(FlaskForm):
    artist_id = StringField('Artist ID', validators=[DataRequired()])
    venue_id = StringField('Venue ID', validators=[DataRequired()])
    start_time = DateTimeField('Start Time', default=datetime.today(), validators=[DataRequired()])
