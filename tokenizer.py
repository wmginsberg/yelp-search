from porter_stemmer import PorterStemmer
import re



class Tokenizer(object):
	def __init__(self):
		self.stemmer = PorterStemmer()
		self.stopwords = set();

		stopwords_file = open("/home/jadenijs/course/cs1951a/final/stencil/code/yelp-search/stopwords.txt")
		for stopword in stopwords_file:
			stopword = stopword.strip('\n')
			self.stopwords.add(stopword)

	def tokenize(self, review, positions=False):
		# This function takes the text of a yelp review and returns a dictionary
		# of words to lists of the positions in which they occur in the review

		raw_words = review.split(" ")

		URL_regex = re.compile('www\.|http\:\/\/|https\:\/\/')
		alphabet_regex = re.compile('[a-z]')

		invalid_chars_regex = re.compile('[^a-z0-9]+')
		sequential_chars_regex = re.compile('(.)\\1+')


		clean_words = {} if positions else [];

		for pos, word in enumerate(raw_words):
			# Lowercase word first
			word = word.lower()

			if not alphabet_regex.match(word):
				# Word does not begin with alphabet
				continue
			elif word in self.stopwords:
				# Word is a stopword
				continue
			elif URL_regex.match(word):
				# Word is a URL
				word = "URL"
			else:
				# Strip all chars that are not alphabets or numbers
				word = invalid_chars_regex.sub('', word)
				# Find repeated characters and replace them with single occurrence
				repeated_chars = sequential_chars_regex.findall(word)
				for c in repeated_chars:
					word = re.sub(c + '+', c, word)
				# Apply Porter stemmer
				word = self.stemmer.stem(word, 0,len(word)-1)

			if len(word) > 1:
				if positions:
					value = clean_words.get(word)
					if value:
						value.append(pos)
					else:
						clean_words[word] = []
						clean_words[word].append(pos)
				else:
					clean_words.append(word)

		return clean_words
