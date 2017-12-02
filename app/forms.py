from wtforms.fields import FieldList
from wtforms import StringField, validators, ValidationError, SubmitField, FormField
from flask_wtf import FlaskForm

class AdvancedSearchForm(FlaskForm):
  artist = StringField('Artist', [validators.Length(max=50)])
  genre = StringField('Genre', [ validators.Length(max=50)])
  title = StringField('Title', [ validators.Length(max=50)])

class SearchForm(FlaskForm):    
  lyrics_snippet = StringField('Lyrics Snippet', [validators.Length(max=150)])
  advanced_search_form = FieldList(FormField(AdvancedSearchForm), min_entries=0, max_entries=5)
  new_row = SubmitField("Advanced Search")
  submit = SubmitField("Send")
