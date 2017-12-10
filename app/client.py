from app import app
import json
import os
import pdb
from datetime import datetime
from SolrClient import SolrClient
from qdr import QueryDocumentRelevance



def search(query_dict):
  #pdb.set_trace()
  #instantiate solr connection
  solr = SolrClient('http://localhost:8983/solr')
  relevance_score_query = ''
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
  docs_relevance_list = {}
  scorer = QueryDocumentRelevance.load_from_file('app/corpus_tfIdf.txt')
  for res in solr.paging_query('lyrics',{ 'q':query_string, }, rows = 200, start = 0, max_start = 1000):
    for doc in res.data['response']['docs']:
      docs_list.append(doc)
      relevance_scores = scorer.score(doc['lyrics'][0].strip().encode('utf-8').split(), relevance_score_query.strip().encode('utf-8').split())
      docs_relevance_list[doc['artist'][0]+' '+doc['title'][0]]= relevance_scores
      #docs_relevance_list.append(doc['lyrics'][0])
  pdb.set_trace()

  #evaluate the docs_list using OKAPI BM-25
  '''
  okapi BM-25
  double okapiK1 = [1.0 1.2];
  double okapiB =[ 0.2 0.3 0.4];
  double okapiK3 = 1000;
  for(occur)
  {
          double idf = log((docN-DF[i]+0.5)/(DF[i]+0.5));
          double weight = ((okapiK1+1.0)*tf[i]) / (okapiK1*(1.0-okapiB+okapiB*docLength/docLengthAvg)+tf[i]);
          double tWeight = ((okapiK3+1)*qf[i])/(okapiK3+qf[i]);
          score+=idf*weight*tWeight;
  }

  Dirichlet
  double dirMu=[1500 2000 2500];
  for(all)
  {
          score+=log((tf[i]+dirMu*termPro[i])/(docLength+dirMu));
  }
  '''
  return docs_list