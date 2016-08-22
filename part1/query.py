import sys
import math
import operator
import csv
import json
from collections import defaultdict
from tokenizer import TokenizerA

csv.field_size_limit(sys.maxsize)

TOTAL_REVIEWS = 335022

HEURISTIC = False

class SearchEngine:

	def __init__(self, args):
		print "Initializing..."
		self.tokenizer = TokenizerA()
		self.biz = {}
		self.initialize_business(args[1])
		print "Businesses initialized..."
		self.index = {}
		self.initialize_index(args[2])
		print "Query...\n"

	def initialize_business(self, business_path):
		with open(business_path, 'rt') as f:
			for line in f:
				b = json.loads(line)
				self.biz[b['business_id']] = b

	def initialize_index(self, index_path):
		# The index is of the form business_id, review_id, list of positions of word
		with open(index_path, 'rt') as f:
			reader = csv.reader(f,delimiter=',')
			for row in reader:
				# Parse the review list and store it keyed to the word
				word = row[0]
 				reviews = []
 				bids = set()
 				review_count = 0
 				for r in row[1].split(":"):
					review_count += 1

 					review = r.split(";")

 					biz_id = review[0]
 					review[2] = [int(x) for x in review[2].split(",")]

 					reviews.append(review)					
				
				self.index[word] = {}
				self.index[word]['reviews'] = reviews

				# Calculate tf-idf
				self.tf_idf(word, reviews, review_count)

	def tf_idf(self, word, reviews, word_review_count):
		# Our tf is the number of occurrences of a word in all of a business's
		# reviews

		# Our idf is given by the log of total number of reviews overall divided by
		# the total number of reviews in which the word occurs.

		idf = math.log(float(TOTAL_REVIEWS)/word_review_count)

		tfs = {} # Map of business ID to tf-idf for the given word


 		for review in reviews:
 			if tfs.has_key(review[0]):
 				tfs[review[0]] += len(review[2])
 			else:
 				tfs[review[0]] = len(review[2])
 
 		for biz_id in tfs:
			tfs[biz_id] *= idf


		self.index[word]['tf_idf'] = tfs


	def run(self):
		for line in sys.stdin:
			results = self.parse_query(line)
			self.rank_and_display_results(results)

	def parse_query(self, line):
		if line[0] == '"' and line[len(line)-2] == '"':
			tokenized = self.tokenizer.process_review(line[1:-2])
			if len(tokenized) == 0:
				return []
			if len(tokenized) > 1:
				return self.phrase_query(tokenized)
			else:
				return self.free_text_query(tokenized)
		else:
			tokenized = self.tokenizer.process_review(line)
			if len(tokenized) == 0:
				return []
			return self.free_text_query(tokenized)

	def rank_and_display_results(self, results):
		results = sorted(results, key=lambda score_pair: score_pair[1])
		length = len(results)

		if length == 0:
			print "No results found.\n"
		else:
			print " "
			for i in range(min(length, 10)):
				bid = results[i][0]
				biz = self.biz.get(bid)
				print "%d) %s  (%s)" % ((i+1), biz['name'], biz['business_id'])
				print str(biz['stars']) + " stars, " + str(biz['review_count']) + " reviews"
				print biz['full_address']
				print ",".join(biz['categories'])
				print "\n------------------------------------------\n"

	def score_results(self, bids, value_objs):
		scores = {};
		# Gather TD-IDFs for each business
		for bid in bids:
			if not scores.has_key(bid):
				scores[bid] = 0

			for obj in value_objs:
				scores[bid] += obj['tf_idf'][bid]

			if HEURISTIC:
				biz = self.biz[bid]
				scores[bid] *= math.log(float(biz['review_count'])) * float(biz['stars'])

		return scores

	def free_text_query(self, words):
		value_objs = []

		obj1 = self.index.get(words[0])
		if not obj1:
			return []

		value_objs.append(obj1)

		inter = set(obj1['tf_idf'].keys())

		# Find the set of all reviews which contain the entire query, in order
		for i in range(1,len(words)):
			obj2 = self.index.get(words[i])
			if not obj2:
				return []
			value_objs.append(obj2)

			temp = set(obj2['tf_idf'].keys())
			inter = inter.intersection(temp)

		scores = self.score_results(inter, value_objs)

		# Return tuples of (business ID, score)
		return scores.items();

	def phrase_query(self, words):
		value_objs = []

		obj1 = self.index.get(words[0])
		if not obj1:
			return []
		value_objs.append(obj1)

		reviews1 = obj1['reviews']

		# Find the set of all reviews which contain the entire query, in order
		for i in range(1,len(words)):
			obj2 = self.index.get(words[i])
			if not obj2:
				return []
			value_objs.append(obj2)

			reviews2 = obj2['reviews']

			common = self.review_list_intersection(reviews1, reviews2)

			reviews1 = self.consecutive_occurence(common)
			if len(reviews1) == 0:
				return []

		# Filter reviews into businesses
		bids = set()
		for review in reviews1:
			bids.add(review[0])

		scores = self.score_results(bids, value_objs)

		# Return tuples of (score, business ID)
		return scores.items();

	def review_list_intersection(self, list1, list2):
		result = []

		len1 = len(list1)
		len2 = len(list2)

		i = 0
		j = 0

  		while (i < len1 and j < len2):
  			if list1[i][1] < list2[j][1]:
  				i += 1
  			elif list1[i][1] > list2[j][1]:
  				j += 1
  			else:
  				result.append((list1[i], list2[j]))
  				i += 1
  				j += 1

		return result

	def helper1(self, pos_i, elt2, result):
		for pos_j in elt2[2]:
			if pos_i == pos_j - 1:
				result.append(elt2)
				return 1

		return 0

	def consecutive_occurence(self, common):
		result = []
		for pair in common:
			elt1 = pair[0]
			elt2 = pair[1]

			for pos_i in elt1[2]:
				if self.helper1(pos_i, elt2, result) == 1:
					break
			

		return result


if __name__ == '__main__':
	SearchEngine(sys.argv).run()












