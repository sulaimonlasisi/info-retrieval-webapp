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
  	query_op = ' AND '
  	item_count = 0
  	for key in query_dict:
  	  if len(query_dict[key]) > 0:
  		  if item_count > 0:
  		    query_string = query_string+query_op+key+':'+query_dict[key]
  		  else:
  		    query_string = query_string+key+':'+query_dict[key]
  		  item_count +=1
  res = solr.query('lyrics',{ 'q':query_string, })
  return res.data['response']['docs']