from porter_stemmer import PorterStemmer
import re

class TokenizerA(object):
	def __init__(self):
		self.stemmer = PorterStemmer()
		self.stops = self.initialize_stops()
		self.sequential_chars_regex = re.compile('(.)\\1+')
		# URL regex courtesy of John Gruber
		self.URL_regex = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')


	def process_review(self, review, positions=False):
		#TODO: pre-process review
		# this is a helper function for __call__
		new_review  = ""
		review = self.URL_regex.sub('URL', review)
		review = self.strip_punctuation(review)        
		review = review.split(" ")

		clean_words = {}

		pos = 0
		for word in review: 
			word = word.strip()

			if (len(word) > 0):
				# lowercase words
				word = word.lower()

				# Ignore stopwords
				if self.stops.get(word):
					continue

				# Turn words that start with non ascii into nothing
				if (ord(word[0]) < 48 or ord(word[0]) > 127):
					continue

				# Remove doubles
				# shortened_word = ""         
				# for i in range(len(word)-2):
				# 	shortened_word += word[i]
				# 	if (word[i] == word[i+1] == word[i+2]):                        
				# 		shortened_word = shortened_word[0:-1]  

				# shortened_word+=word[len(word)-2:]        
				# word = shortened_word

				repeated_chars = self.sequential_chars_regex.findall(word)
				for c in repeated_chars:
					word = re.sub(c + '+', c, word)

				# Porter Stemmer        
				word = self.stemmer.stem(word, 0,len(word)-1)

				# Add to review
				if positions:
					value = clean_words.get(word)
					if value:
						value.append(pos)
					else:
						clean_words[word] = []
						clean_words[word].append(pos)
				else:
					word += " "
					new_review += word

				pos += 1
		
		if positions:
			return clean_words
		else:
			new_review = ' '.join(new_review.split())
			review = new_review.split()
			return review

	def __call__(self, doc):
		# this function will tokenize the given document and return a list of extracted features (tokens)
		processed_doc = self.process_review(doc)
		#TODO: return a list of features extracted from processed_doc
		return processed_doc

	def strip_punctuation(self,words):   
		# Replace punctuation with whitespace
		# p = ['"',':', '[', ']', '\\', '~', '@', '#', '$', '%', '^', '&', '=' ',','.','\n', '/', '-', '?','!',';',')','(','=','*','0','1','2','3','4','5','6','7','8','9']
		pattern = re.compile('[^a-zA-Z\' ]+')
		# for punc in p:
		# 	words = words.replace(punc,' ')

		words = pattern.sub(' ', words)

		words = re.sub(r'\'[^ ]*', '', words)

		return words

	def initialize_stops(self):
		# stop_file = open('../../../data/stopwords.txt', 'r')
		stop_file = open('stopwords.txt', 'r')
		stop_words = stop_file.readlines()
		stops = {}
		for stop_word in stop_words:
			stops[stop_word[:-1]] = 1

		return stops     

