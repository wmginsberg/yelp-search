from __future__ import division
import sys
import csv
from collections import defaultdict
import argparse
import json
import re
import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

features = []


def createTree(my_dict,file_name):
	global features

	biz = {}

	# business_path = "/course/cs1951a/pub/final/data/extracted/yelp_academic_dataset_business.json"
	business_path = "data/yelp_academic_dataset_business.json"

	with open(business_path, 'rt') as f:
			for line in f:
				b = json.loads(line)
				biz[b['business_id'].encode('utf-8')] = b
				my_dict[b['name'].encode('utf-8')] = b['business_id'].encode('utf-8')

	
	b_id = []

	pattern = re.compile('\(\\d+, 0\.\\d+\)')
	with open(file_name) as f:
		reader = csv.reader(f)
		for row in reader:
			buckets = [0] * 100
			r = pattern.findall(row[1])

			for elt in r:
				elt = elt[1:-1].split(", ")
				buckets[int(elt[0])] = float(elt[1])
			

			features.append(buckets)
			b_id.append(row[0])
	X = np.array(features)
	nbrs = NearestNeighbors(n_neighbors=11, algorithm='ball_tree').fit(X)
	return nbrs, b_id, biz

def query(business_id,nbrs,b_id,biz):
	global features

	queryobj = biz[business_id]
	categories = set(queryobj['categories'])
	numcategories = len(categories)
	numattributes = len(queryobj['attributes'])

	index = b_id.index(business_id)
	q = features[index]

	distances , indices = nbrs.kneighbors(q)
	results = []
	bids = []
	for x in indices[0]:

		resultobj = biz[b_id[x]]
		attrscore = 0
		stardiff = float(queryobj['stars']) - float(resultobj['stars'])
		for a in resultobj['attributes']:
			if resultobj['attributes'].get(a) == queryobj['attributes'].get(a):
				attrscore += 1

		attrscore /= numattributes
		catscore = len(categories.intersection(set(resultobj['categories'])))/numcategories
		#biz[b_id[x]]['categories'], biz[b_id[x]]['stars'], biz[b_id[x]]['attributes'],
		results.append((biz[b_id[x]]['name'].encode('utf-8') ,  (attrscore, catscore, stardiff)))
		bids.append('"' + b_id[x] + '"')
	for x in range(len(results)):
		print str(x) + ") " + str(results[x])

		


	print ",".join(bids)
		




def file_to_dict(my_file,my_dict):
    for line in my_file:
        # Load information, tokenize review
        data = json.loads(line)
        


if __name__ == '__main__':
    
    id_dict = {}
    features_file = 'probabilites.csv'
    res = createTree(id_dict,features_file)
    print "Ready for queries"
    for line in sys.stdin:
        name = line.strip('\n')
        if (id_dict.has_key(name)):
        	print "Recommendations for " + name
        	query(id_dict[name],res[0],res[1],res[2])
        else: 
            print "Cannot find business, " + name