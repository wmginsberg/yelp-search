from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol

class UserGroupedReviews(MRJob):
	INPUT_PROTOCOL = JSONValueProtocol

	def __init__(self, args):
		super(UserGroupedReviews, self).__init__(args)
		self.sents = {}
		with open('AFINN-111.txt', 'r') as f:
			for line in f:
				term, score  = line.split("\t")
				self.sents[term] = float(score)


	bids = ["QweOrPB4d80XnWtESAl1kQ","ZRrIwqIUMII1b2keMI8QRw","UH-fhgy-_NvPyZRE3-Mthg","sBxd1tZZtGJ8jDZZxHZiwg","czOxS1z2MGzPXNP3W1d0Yw","xS7LCOcJbqh_Y5cIKxqWfQ","AZq_SBJsqsleJkQCksYsjg","FgyBmc-XS_ViFAf8Wy25yA","VgtEm_L23SNZEsyNMKwhog","Avg7PU8_DBm0KfJ2t2lTzw","KNIFSqzQADOZWDO_7T-KzA"]
	def mapper(self, _, review):
		text = review['text'].encode('UTF-8')
		bid = review['business_id'].encode('UTF-8')
		user_id = review['user_id'].encode('UTF-8')

		if bid in self.bids:
			yield (user_id, [bid, text])

	def reducer(self, key, values):
		l = []
		contains_original = False
		for value in values:
			if value[0] == self.bids[0]:
				contains_original = True

			score = 0
			words = value[1].split(" ")
			for word in words:
				word = word.lower()
				word_score = self.sents.get(word)
				if word_score:
					score += word_score
			l.append([value[0],score])

		if len(l) > 1 and contains_original:
			yield (key, l)

if __name__ == '__main__':
	UserGroupedReviews.run()