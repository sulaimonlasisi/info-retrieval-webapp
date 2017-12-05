from flask import url_for, render_template, request, redirect, flash
from app import app
from app.forms import  SearchForm
from app.client import search
from collections import namedtuple
from typing import Text
from typing import Iterable
from flask_paginate import Pagination, get_page_parameter
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
    page = request.args.get(get_page_parameter(), type=int, default=1)
    if form.new_row.data:
      form.advanced_search_form.append_entry()
    #Doesn't return to 1 for pagination because of page > 1 condition here
    elif request.method == 'POST' or (page > 1):
        global results
        if request.method == 'POST' and form.validate_on_submit():            
            query_dict = {}
            results = []
            query_dict['lyrics'] = form.lyrics_snippet.data
            if (len(form.advanced_search_form) > 0):
                query_dict['artist'] = form.advanced_search_form[0].artist.data
                query_dict['title'] = form.advanced_search_form[0].title.data
                query_dict['genre'] = form.advanced_search_form[0].genre.data
            for result in search(query_dict):                    
                results.append(Result(Title = result['title'][0], Artist = result['artist'][0], Genre = result['genre'][0], Lyrics = result['lyrics'][0]))
        mini_results = []
        if (page-1):
          if (len(results) > (((page-1)*10)+10)):
            mini_results = results[((page-1)*10): (((page-1)*10)+10)]
          else:
            mini_results = results[((page-1)*10):]
        else:
            mini_results = results[0: 10]              
        pagination = Pagination(page=page, total=len(results), record_name='lyrics', per_page = 10, inner_window = 2, outer_window = 2)                   
        return render_template('results.html', search_result = mini_results,pagination=pagination)
    return render_template('search.html', title = 'Search', form = form)