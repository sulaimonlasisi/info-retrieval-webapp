from flask import url_for, render_template, request, redirect, flash
from app import app
from app.forms import  SearchForm
from app.client import search
from collections import namedtuple
from typing import Text
from typing import Iterable
import pdb

Result = namedtuple('Result', [
    'Title',
    'Artist',
    'Genre',
    'Lyrics',
])

@app.route('/')
@app.route('/index')
@app.route('/search', methods=['GET', 'POST'])
def lyrics_search():
    form = SearchForm()
    if form.new_row.data:
      form.advanced_search_form.append_entry()
    elif request.method == 'POST':
        if form.validate_on_submit():
            results = []
            query_dict = {}
            query_dict['lyrics'] = form.lyrics_snippet.data
            if (len(form.advanced_search_form) > 0):
                query_dict['artist'] = form.advanced_search_form[0].artist.data
                query_dict['title'] = form.advanced_search_form[0].title.data
                query_dict['genre'] = form.advanced_search_form[0].genre.data
            for result in search(query_dict):
                result_entry = Result(Title = result['title'][0], Artist = result['artist'][0], Genre = result['genre'][0], Lyrics = result['lyrics'][0])
                results.append(result_entry)                   
            return render_template('results.html', search_result = results)
    return render_template('search.html', title = 'Search', form = form)