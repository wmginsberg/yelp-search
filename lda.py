import sys
import csv
import json
import numpy
from collections import defaultdict
import util

from gensim import corpora, models, similarities
import gensim



def main(data):
    
    review_dict = {}
    review_id = 0
    reviews = []
    b_id = []
    prob_vector = {}
    
    for line in data:
        
    	# Load information, tokenize review
        info = line.split(',')
        split_line = info[1].split(' ')
        reviews.append(split_line)
        b_id.append(info[0])
        
    print "here1"
    dictionary = corpora.Dictionary(reviews)
    print "here2"
    dictionary.save('reviews.dict')
    corpus = [dictionary.doc2bow(text) for text in reviews]
    print "here3"
    gensim.corpora.MmCorpus.serialize('example.mm', corpus)
    print "here4"
    mm = corpora.MmCorpus('example.mm')
    print "here5"
    lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics = 100)
    print "here6"
    data = open('new_output.csv')
    for line in data:
        info = line.split(',')
        prob_vector[info[0]] = lda[dictionary.doc2bow(info[1].split(' '))]
        
    write_to_file(prob_vector)
     
        

def write_to_file(r_dict):
    print "in write file"
    csv_writer = csv.writer(open('probabilites.csv','w')) 
    for word in r_dict.keys():
        
        data = r_dict[word]
        csv_writer.writerow([word,data]) 
	


if __name__ == '__main__':
	data = open('new_output.csv') # csv of businessid, string concatenation of every review
	main(data)