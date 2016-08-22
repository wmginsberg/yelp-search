from mrjob.job import MRJob
from tokenizer import Tokenizer
from mrjob.protocol import JSONValueProtocol

class ReviewCSVProtocol(object):
	def read(self,line):
		pass
	def write(self,key,value):
		return '"%s","%s"' % (key, value)



class ConcatReviews(MRJob):
	INPUT_PROTOCOL = JSONValueProtocol
	OUTPUT_PROTOCOL = ReviewCSVProtocol

	def __init__(self, args):
		super(ConcatReviews, self).__init__(args)
		self.tokenizer = Tokenizer()

	def mapper(self, _, review):
		# INPUT : A line from the reviews JSON file
		# OUTPUT:
		# 	key: word
		#	value: dictionary of review
		text = review['text'].encode('UTF-8')
		tokenized_review = self.tokenizer.tokenize(text)
		yield (review['business_id'], " ".join(tokenized_review))

	def reducer(self, key, values):
		str = ""
		for value in values:
			str += value

		yield (key, str)

if __name__ == '__main__':
	ConcatReviews.run()
