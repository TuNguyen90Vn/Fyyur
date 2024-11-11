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
    state = SelectField('State', choices=State.choices(), validators=[DataRequired(), is_valid_state])
    phone = StringField('Phone', validators=[is_valid_phone])
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

# class ShowForm(Form):
#     artist_id = StringField(
#         'artist_id'
#     )
#     venue_id = StringField(
#         'venue_id'
#     )
#     start_time = DateTimeField(
#         'start_time',
#         validators=[DataRequired()],
#         default= datetime.today()
#     )
#
# class VenueForm(Form):
#     name = StringField(
#         'name', validators=[DataRequired()]
#     )
#     city = StringField(
#         'city', validators=[DataRequired()]
#     )
#     state = SelectField(
#         'state', validators=[DataRequired()],
#         choices=[
#             ('AL', 'AL'),
#             ('AK', 'AK'),
#             ('AZ', 'AZ'),
#             ('AR', 'AR'),
#             ('CA', 'CA'),
#             ('CO', 'CO'),
#             ('CT', 'CT'),
#             ('DE', 'DE'),
#             ('DC', 'DC'),
#             ('FL', 'FL'),
#             ('GA', 'GA'),
#             ('HI', 'HI'),
#             ('ID', 'ID'),
#             ('IL', 'IL'),
#             ('IN', 'IN'),
#             ('IA', 'IA'),
#             ('KS', 'KS'),
#             ('KY', 'KY'),
#             ('LA', 'LA'),
#             ('ME', 'ME'),
#             ('MT', 'MT'),
#             ('NE', 'NE'),
#             ('NV', 'NV'),
#             ('NH', 'NH'),
#             ('NJ', 'NJ'),
#             ('NM', 'NM'),
#             ('NY', 'NY'),
#             ('NC', 'NC'),
#             ('ND', 'ND'),
#             ('OH', 'OH'),
#             ('OK', 'OK'),
#             ('OR', 'OR'),
#             ('MD', 'MD'),
#             ('MA', 'MA'),
#             ('MI', 'MI'),
#             ('MN', 'MN'),
#             ('MS', 'MS'),
#             ('MO', 'MO'),
#             ('PA', 'PA'),
#             ('RI', 'RI'),
#             ('SC', 'SC'),
#             ('SD', 'SD'),
#             ('TN', 'TN'),
#             ('TX', 'TX'),
#             ('UT', 'UT'),
#             ('VT', 'VT'),
#             ('VA', 'VA'),
#             ('WA', 'WA'),
#             ('WV', 'WV'),
#             ('WI', 'WI'),
#             ('WY', 'WY'),
#         ]
#     )
#     address = StringField(
#         'address', validators=[DataRequired()]
#     )
#     phone = StringField(
#         'phone'
#     )
#     image_link = StringField(
#         'image_link'
#     )
#     genres = SelectMultipleField(
#         # TODO implement enum restriction
#         'genres', validators=[DataRequired()],
#         choices=[
#             ('Alternative', 'Alternative'),
#             ('Blues', 'Blues'),
#             ('Classical', 'Classical'),
#             ('Country', 'Country'),
#             ('Electronic', 'Electronic'),
#             ('Folk', 'Folk'),
#             ('Funk', 'Funk'),
#             ('Hip-Hop', 'Hip-Hop'),
#             ('Heavy Metal', 'Heavy Metal'),
#             ('Instrumental', 'Instrumental'),
#             ('Jazz', 'Jazz'),
#             ('Musical Theatre', 'Musical Theatre'),
#             ('Pop', 'Pop'),
#             ('Punk', 'Punk'),
#             ('R&B', 'R&B'),
#             ('Reggae', 'Reggae'),
#             ('Rock n Roll', 'Rock n Roll'),
#             ('Soul', 'Soul'),
#             ('Other', 'Other'),
#         ]
#     )
#     facebook_link = StringField(
#         'facebook_link', validators=[URL()]
#     )
#     website_link = StringField(
#         'website_link'
#     )
#
#     seeking_talent = BooleanField( 'seeking_talent' )
#
#     seeking_description = StringField(
#         'seeking_description'
#     )
#
#
#
# class ArtistForm(Form):
#     name = StringField(
#         'name', validators=[DataRequired()]
#     )
#     city = StringField(
#         'city', validators=[DataRequired()]
#     )
#     state = SelectField(
#         'state', validators=[DataRequired()],
#         choices=[
#             ('AL', 'AL'),
#             ('AK', 'AK'),
#             ('AZ', 'AZ'),
#             ('AR', 'AR'),
#             ('CA', 'CA'),
#             ('CO', 'CO'),
#             ('CT', 'CT'),
#             ('DE', 'DE'),
#             ('DC', 'DC'),
#             ('FL', 'FL'),
#             ('GA', 'GA'),
#             ('HI', 'HI'),
#             ('ID', 'ID'),
#             ('IL', 'IL'),
#             ('IN', 'IN'),
#             ('IA', 'IA'),
#             ('KS', 'KS'),
#             ('KY', 'KY'),
#             ('LA', 'LA'),
#             ('ME', 'ME'),
#             ('MT', 'MT'),
#             ('NE', 'NE'),
#             ('NV', 'NV'),
#             ('NH', 'NH'),
#             ('NJ', 'NJ'),
#             ('NM', 'NM'),
#             ('NY', 'NY'),
#             ('NC', 'NC'),
#             ('ND', 'ND'),
#             ('OH', 'OH'),
#             ('OK', 'OK'),
#             ('OR', 'OR'),
#             ('MD', 'MD'),
#             ('MA', 'MA'),
#             ('MI', 'MI'),
#             ('MN', 'MN'),
#             ('MS', 'MS'),
#             ('MO', 'MO'),
#             ('PA', 'PA'),
#             ('RI', 'RI'),
#             ('SC', 'SC'),
#             ('SD', 'SD'),
#             ('TN', 'TN'),
#             ('TX', 'TX'),
#             ('UT', 'UT'),
#             ('VT', 'VT'),
#             ('VA', 'VA'),
#             ('WA', 'WA'),
#             ('WV', 'WV'),
#             ('WI', 'WI'),
#             ('WY', 'WY'),
#         ]
#     )
#     phone = StringField('Phone', validators=[Optional()])
#     genres = SelectMultipleField(
#         'genres', validators=[DataRequired()],
#         choices=[
#             ('Alternative', 'Alternative'),
#             ('Blues', 'Blues'),
#             ('Classical', 'Classical'),
#             ('Country', 'Country'),
#             ('Electronic', 'Electronic'),
#             ('Folk', 'Folk'),
#             ('Funk', 'Funk'),
#             ('Hip-Hop', 'Hip-Hop'),
#             ('Heavy Metal', 'Heavy Metal'),
#             ('Instrumental', 'Instrumental'),
#             ('Jazz', 'Jazz'),
#             ('Musical Theatre', 'Musical Theatre'),
#             ('Pop', 'Pop'),
#             ('Punk', 'Punk'),
#             ('R&B', 'R&B'),
#             ('Reggae', 'Reggae'),
#             ('Rock n Roll', 'Rock n Roll'),
#             ('Soul', 'Soul'),
#             ('Other', 'Other'),
#         ]
#      )
#     facebook_link = URLField('Facebook Link', validators=[Optional(), URL()])
#     image_link = URLField('Image Link', validators=[Optional(), URL()])
#     website_link = URLField('Website Link', validators=[Optional(), URL()])
#     seeking_venue = BooleanField( 'seeking_venue' )
#     seeking_description = StringField('seeking_description')

