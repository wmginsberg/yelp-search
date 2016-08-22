import sys
import math
import operator
import csv
import json
import numpy
from collections import defaultdict
import util
from tokenizer import TokenizerA



csv.field_size_limit(sys.maxsize)


def query(file_name, line):
	tokenizer = TokenizerA()
	PQ = 0
	if line[0] == '"' and line[len(line)-2] == '"':
		PQ = 1
		line = line[1:-2]
		

	words = tokenizer.process_review(line)
	b_ids = set() #eventual list of b_ids for the query
	
	#words = line.split(" ")
	info = {} #info for each word, formatted as a list of ["b_id,r_id,pos",etc..]
	values = {} #business id for each term
	tf = {} #term frequency
	idf = {} #inverse document freq
	total = 15585
	for w in words:
		tf[w] = {}
		with open(file_name, 'rt') as f:
			reader = csv.reader(f,delimiter=',')
			for row in reader:
				if w == row[0]:
					info[w] = row[1].split(';')
	
	if len(info) == 0:
		print "There are no results for : " + str(words)
	else:
		if PQ == 0:
			for key in info:
				values[key] = set()
				document_count = set()
				if '' in values[key]:
					values[key].remove('')
				if '' in document_count:
					document_count.remove('')
				

				#review_info = info[key].split(';')
				for r in info[key]:

					r_info = r.split(',')
					if r_info[0] in tf[key]:
						tf[key][r_info[0]] += 1
					if r_info[0] not in tf[key]:
						tf[key][r_info[0]] = 1
					if r_info[0] not in values[key]:
						values[key].add(r_info[0])
						b_ids.add(r_info[0])
						document_count.add(r_info[0])
				idf[key] = len(document_count)
		if PQ == 1:

			if words[0] != '':
				for x in range(len(words)):
					#review_info = info[words[x]].split(';')
					values[words[x]] = set()
					document_count = set()
					if '' in values[words[x]]:
						values[words[x]].remove('')
					if '' in document_count:
						document_count.remove('')

					for r in info[words[x]]:

						r_info = r.split(',')
						
						if '' != r:
							
							if r_info[0] in tf[words[x]]:
								tf[words[x]][r_info[0]] += 1
							if r_info[0] not in tf[words[x]]:
								tf[words[x]][r_info[0]] = 1
							values[words[x]].add((r_info[0],r_info[1],int(r_info[2])-x))
							b_ids.add((r_info[0],r_info[1],int(r_info[2])-x))
							document_count.add(r_info[0])
					idf[words[x]] = len(document_count)





		for key in values:
			b_ids = b_ids.intersection(values[key])
			
		if PQ == 1:
			
			b = set()
			if '' in b:
				b.remove('')
			for s in b_ids:
				b.add(s[0])
			b_ids = b

		if '' in b_ids:
			b_ids.remove('')
		data = open("../../../data/yelp_academic_dataset_business.json")
		bus_info = {} #dictionary that stores the tuple (reviewcount, stars)
		for line in data:
			bus = json.loads(line)
			b_id = bus['business_id'].encode('utf-8')
			bus_info[b_id] = (float(bus['review_count']),float(bus['stars']),bus['name'].encode('utf-8'))

		tf_idf = {}
		if len(b_ids) == 0:
			print "There are no results for : " + str(words)
		for business in b_ids:
			tf_idf[business] = 0
			for w in words:
				tf_idf[business] += tf[w][business] * math.log((total/float(idf[w])))
			
			tf_idf[business] = (tf_idf[business] * math.log(bus_info[business][0]) * bus_info[business][1],bus_info[business][2])

		#TODO  could do cosine similarity for tf-idf
		



		sorted_results = sorted(tf_idf.iteritems(), key=operator.itemgetter(1), reverse= True)[:10]
		counter = 1
		for key in sorted_results:
			print str(counter) +" :", key[1][1]
			counter += 1



def main():
	# first read in the inverted index file
	file_name = sys.argv[1]
	# a = set()
	# a.add("a")
	# a.add("b")
	# b = set()
	# b.add("b")
	# b.add("c")
	# b = b.intersection(a)
	# print b


	for line in sys.stdin:
		# answer each query
		
		
		query(file_name, line)
		

if __name__ == '__main__':
	main()

