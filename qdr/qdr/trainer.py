'''
"Train" the query-document relevance model (compute document counts from
a corpus)
'''

import gzip
import pdb

from contextlib import closing

# the model is written to a flat text file with the following format:
#
# first line is the total number of documents
# subsequent lines contain the token, total count, total document count
#   separated by tabs

def load_model(inputfile):
    '''
    Return total docs, counts dict
    '''
    with closing(gzip.GzipFile(inputfile, 'r')) as f:
        ndocs = int(f.readline().strip().decode('utf-8'))
        counts = {}
        for line in f:
            word, count1, count2 = line.strip().decode('utf-8').split('\t')
            word = word.encode('utf-8')
            #count1 = count1.encode('utf-8')
            #count2 = count2.encode('utf-8')
            counts[word] = [int(count1), int(count2)]
    return ndocs, counts

def write_model(ndocs, counts, outputfile):
    '''Write to output file'''
    with closing(gzip.GzipFile(outputfile, 'w')) as f:
        f.write(str(ndocs).encode('utf-8'))
        f.write('\n'.encode('utf-8'))
        for word, count in counts.items():
            f.write(word.encode('utf-8'))
            f.write('\t'.encode('utf-8'))
            f.write(str(count[0]).encode('utf-8'))
            f.write('\t'.encode('utf-8'))
            f.write(str(count[1]).encode('utf-8'))
            f.write('\n'.encode('utf-8'))
            #, '\t'.encode('utf-8'), str(count[0]).encode('utf-8'), \
            #    '\t'.encode('utf-8'), str(count[1]).encode('utf-8'))


class Trainer(object):
    '''
    Compute document counts from a corpus

    To support TF-IDF, BM25 and language model ranking functions need:
    
    a unigram language model (token -> total count in corpus)
    corpus document counts (token -> total documents in corpus)
    number total docs in corpus for TFIDF
    average document length (=total words / total docs) for BM25
    '''
    def __init__(self):
        # _counts: word -> (total count, total document count)
        self._counts = {}
        self._total_docs = 0

    def train(self, corpus):
        '''
        Add the documents in corpus to the current model
        corpus = iterator of documents, each document is list of tokens, e.g.
        corpus = [['words', 'in', 'doc1'], ['document', 'two', 'here']]
        '''
        for doc in corpus:
            if len(doc) > 0:
                self._total_docs += 1
                doc_words = set()
                for word in doc:
                    # first the total count
                    if word not in self._counts:
                        self._counts[word] = [1, 0]
                    else:
                        self._counts[word][0] += 1

                    # now the document count
                    if word not in doc_words:
                        self._counts[word][1] += 1
                        doc_words.add(word)

    def update_counts_from_trained(self, qd):
        '''
        Update the current model with the counts from another model
        qd is another Trainer instance 
        '''
        for word, count in qd._counts.items():
            try:
                self._counts[word][0] += count[0]
                self._counts[word][1] += count[1]
            except KeyError:
                self._counts[word] = count
        self._total_docs += qd._total_docs

    def prune(self, min_count, min_doc_count):
        '''
        Remove all words with count less then min_count
        or document count less then min_doc_count
        '''
        words_to_remove = []
        for word, count in self._counts.items():
            if count[0] < min_count or count[1] < min_doc_count:
                words_to_remove.append(word)

        for word in words_to_remove:
            del self._counts[word]

    @classmethod
    def load_from_file(cls, inputfile):
        ndocs, counts = load_model(inputfile)
        ret = cls()
        ret._total_docs = ndocs
        ret._counts = counts
        return ret

    def serialize_to_file(self, outputfile):
        write_model(self._total_docs, self._counts, outputfile)

