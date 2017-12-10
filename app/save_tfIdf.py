import json
from qdr import Trainer
import pdb
 
#data = json.load(open(file, "r"))
lyrics_data = json.load(open('../all_songs.json', 'r'))
corpus = [] 
# Access data
for lyric in lyrics_data:
  #pdb.set_trace()
  corpus.append(lyric['lyrics'].strip().split())
# load corpus -- it's an iterable of documents, each document is a
# list of byte strings
model = Trainer()
model.train(corpus)
model.serialize_to_file("corpus_tfIdf.txt")