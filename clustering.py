from __future__ import division
import sys
import csv
import argparse
import json
import re
import numpy as np
from sklearn.cluster import KMeans

N_CLUSTERS = 30

class Clustering:
	def __init__(self, args):
		print "Initializing..."
		self.biz = {}
		self.features = []
		self.labels = []

		self.initialize(args[1])

		self.kmeans = KMeans(n_clusters=N_CLUSTERS)

	def initialize(self,file_name):
		global features

		biz = {}

		business_path = "data/yelp_academic_dataset_business.json"
		with open(business_path, 'rt') as f:
				for line in f:
					b = json.loads(line)
					self.biz[b['business_id'].encode('utf-8')] = b

		
		pattern = re.compile('\(\\d+, 0\.\\d+\)')

		self.N = 0

		with open(file_name) as f:
			reader = csv.reader(f)
			for row in reader:
				self.N += 1

				biz_entry = self.biz[row[0]]

				buckets = [0] * 100
				r = pattern.findall(row[1])

				for elt in r:
					elt = elt[1:-1].split(", ")
					buckets[int(elt[0])] = float(elt[1])
				

				self.features.append(buckets)
				self.labels.append(( biz_entry['business_id'].encode('UTF-8'), biz_entry['name'].encode('UTF-8') , ) )

		self.features = np.array(self.features)

	def cluster(self):
		print "Clustering..."

		Y = self.kmeans.fit_transform(self.features)

		Y_tups = []

		for col in xrange(N_CLUSTERS):
			Y_tups.append([])
			for row in xrange(self.N):
				tup = self.labels[row] + (Y[row][col], )
				Y_tups[col].append(tup)

		for col in xrange(N_CLUSTERS):
			Y_tups[col] = sorted(Y_tups[col], key = lambda entry: entry[2])

		self.top10 = []

		for col in xrange(N_CLUSTERS):
			self.top10.append(Y_tups[col][:11])

	def build_json(self):
		print "Building JSON..."
		f = open('graph.json', 'w')

		nodes = []
		links = []

		for col in xrange(N_CLUSTERS):
			entry = self.top10[col][0]
			nodes.append({'biz_id': entry[0], 'name': entry[1], 'group': col, 'size':15})

		ind = len(nodes)

		for j in xrange(N_CLUSTERS):
			for i in xrange(1,10):
				entry = self.top10[j][i]
				nodes.append({'biz_id': entry[0], 'name': entry[1], 'group': j, 'size':5})
				links.append({'source': j, 'target': ind})
				ind += 1

		result = {'nodes': nodes, 'links': links}

		f.write(json.dumps(result)) 
		f.close()

	def run(self):
		self.cluster()
		self.build_json()

if __name__ == '__main__':
	Clustering(sys.argv).run()





