from app import app
import json
import os
import pdb
from datetime import datetime
from SolrClient import SolrClient
from qdr import QueryDocumentRelevance
import numpy as np



def search(query_dict):
  #pdb.set_trace()
  #instantiate solr connection
  solr = SolrClient('http://localhost:8983/solr')
  relevance_score_query = '' #Used to save exact lyric query to check relevance
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
          #pdb.set_trace()
          query_string = query_string+key+':\"'+query_dict[key]+'\" '
          for word in query_dict[key].split():
            if key=="lyrics" and len(query_dict[key].split())>1:
              query_string = query_string+key+':'+word+' '
          #this takes the lyrics query and ranks all documents returned based on it
          if key=="lyrics":
            relevance_score_query = query_dict[key]
          item_count +=1
  docs_list = []
  tfidf_relevance_dict = {}
  bm25_relevance_dict = {} #saves all retrieved docs and their relevance score - artist&title is used as key
  lm_jm_relevance_dict = {}
  lm_ad_relevance_dict = {}
  lm_dir_relevance_dict = {}
  scorer = QueryDocumentRelevance.load_from_file('app/corpus_tfIdf.txt') #load existing corpus with tf-idf metrics
  for res in solr.paging_query('lyrics',{ 'q':query_string, }, rows = 200, start = 0, max_start = 1000):
    for doc in res.data['response']['docs']:
      docs_list.append(doc)
      relevance_scores = scorer.score(doc['lyrics'][0].strip().encode('utf-8').split(), relevance_score_query.strip().encode('utf-8').split())
      bm25_relevance_dict[doc['artist'][0]+' '+doc['title'][0]]= relevance_scores['bm25']
      tfidf_relevance_dict[doc['artist'][0]+' '+doc['title'][0]]= relevance_scores['tfidf']
      lm_jm_relevance_dict[doc['artist'][0]+' '+doc['title'][0]]= relevance_scores['lm_jm']
      lm_ad_relevance_dict[doc['artist'][0]+' '+doc['title'][0]]= relevance_scores['lm_ad']
      lm_dir_relevance_dict[doc['artist'][0]+' '+doc['title'][0]]= relevance_scores['lm_dirichlet']

  

  #get map for each dictionary listed above
  map_scores_dict = {}
  map_scores_dict['bm25'] = get_map_val(bm25_relevance_dict)
  map_scores_dict['tfidf'] = get_map_val(tfidf_relevance_dict)
  map_scores_dict['lm_jm'] = get_map_val(lm_jm_relevance_dict)
  map_scores_dict['lm_ad'] = get_map_val(lm_ad_relevance_dict)
  map_scores_dict['lm_dir'] = get_map_val(lm_dir_relevance_dict)

  fw=open("map_values.txt", "a+")
  fw.write("Query: "+relevance_score_query+'\n')
  for key in map_scores_dict:
    fw.write(str(key)+" MAP Score: "+str(map_scores_dict[key])+'\n')
  fw.close()

  return docs_list



def get_map_val(rel_scores_dict):
  #Use median relevance of entire retrieved document to determine relevance
  #This is arbitrary and was discussed.
  median_relevance = np.median([rel_scores_dict[key] for key in rel_scores_dict])
  #go through list and calculate mean average precision
  #if relevance is less than median, it is not relevant
  #if it is greater than or equal, it is relevant
  item_ctr = 0
  rel_ctr = 0
  important_cnts = 10
  map_val = 0.0
  for key in rel_scores_dict:
    item_ctr+=1
    if rel_scores_dict[key] >= median_relevance:
      rel_ctr+=1
      map_val += (rel_ctr/item_ctr)
  map_val = map_val/len(rel_scores_dict)
  return map_val