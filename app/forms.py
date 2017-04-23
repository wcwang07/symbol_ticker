from flask.ext.wtf import Form 
from wtforms import StringField 
from wtforms.validators import DataRequired

class CountrySearch(Form):
    country_name = StringField('country_name', validators=[DataRequired()]) 
