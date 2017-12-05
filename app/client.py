from app import app
import json
import os
import pdb
from datetime import datetime
from SolrClient import SolrClient



def search(query_dict):
  #pdb.set_trace()
  #instantiate solr connection
  solr = SolrClient('http://localhost:8983/solr')
  
  # Generic search if no query input given
  if len(query_dict) == 0:
  	query_string = '*:*'
  #retrieve value of field in table and prepare a query string
  else:
    query_string = ''
    query_op = ' OR '
    item_count = 0
    for key in query_dict:
      if len(query_dict[key]) > 0:
        if item_count > 0:
          query_string = query_string+query_op+key+':'+query_dict[key]
        else:
          query_string = query_string+key+':\"'+query_dict[key]+'\" '
          for word in query_dict[key].split():
            if key=="lyrics" and len(query_dict[key].split())>1:
              query_string = query_string+key+':'+word+' '
              #query_string = query_string+key+':'+query_dict[key]
          item_count +=1
  docs_list = []
  for res in solr.paging_query('lyrics',{ 'q':query_string, }, rows = 200, start = 0, max_start = 1000):
    for doc in res.data['response']['docs']:
      docs_list.append(doc)
  return docs_list