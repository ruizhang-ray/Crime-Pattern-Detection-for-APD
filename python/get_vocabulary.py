from gensim import corpora
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from collections import defaultdict
from six import iteritems
import string
import arrow
import nltk
import sys
import re

class Documents(object):

	def __init__(self, fname):
		self.fname    = fname
		self.fhandler = open(self.fname)
		self.index    = 0

	def __iter__(self):
		for line in self.fhandler:
			if self.index > 0 and self.index % 1000 == 0:
				print >> sys.stderr, '[%s] [Documents] %s docs have been processed.' % (arrow.now(), self.index)
			yield self.tokenize(line)
			self.index += 1

	def tokenize(self, text):
		tokens = []
		# Remarks for each of the crimes are delimited by '\2'
		for remarks in text.strip('\n').split('\2'):
			# Free text part for each of the records are delimited by '\1'
			for remark in remarks.strip().split('\1'):
				# For every sentences in each of the free text part
				for sent in sent_tokenize(remark.decode("utf8")):
					# For every token
					for token in nltk.word_tokenize(sent.lower()):
						# Replace '-' with '_'
						tokens.append('_'.join(token.split('-')))
		return tokens

print >> sys.stderr, '[%s] Init document object.' % arrow.now()
docs = Documents('../tmp/woodie.validate_24_cases/corpus.txt')

print >> sys.stderr, '[%s] Creating dictionary.' % arrow.now()
dictionary = corpora.Dictionary([ doc for doc in docs ])
dictionary.save('./universe.dict')

print >> sys.stderr, '[%s] Removing stopwords, words that appear only once, and other non-words' % arrow.now()
non_ids  = [ tokenid for token, tokenid in iteritems(dictionary.token2id) if token in string.punctuation ]
once_ids = [ tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1 ]
stop_ids = [
	dictionary.token2id[stopword] 
	for stopword in stopwords.words('english')
	if stopword in dictionary.token2id
]
dictionary.filter_tokens(stop_ids + once_ids + non_ids)

print dictionary
print dictionary.token2id
