import sys
import csv
import json
from tokenizer import TokenizerA


def main(data):
	tokenizer = TokenizerA()
	review_dict = {}
	review_id = 0
	
	for line in data:

		# Load information, tokenize review
		review = json.loads(line)
		tokenized_review = tokenizer.process_review(review['text'].encode('utf-8'), positions=True)
	
		# position = 0
		# Word by word, insert into dictionary
		for word in tokenized_review:

			positions = tokenized_review[word]

			# If the word is already there, append it
			if review_dict.has_key(word):
				# word_data = review_dict[word]
				# word_data += (review['business_id'].encode('utf-8') + ";" + str(review_id) + ";" + ",".join([str(x) for x in positions]) + ":")
				word_data = [ review['business_id'].encode('utf-8') , str(review_id) , ",".join([str(x) for x in positions ]) ]
				review_dict[word].append(word_data)

			# If it is not there, insert it
			else:
				review_dict[word] = [ [ review['business_id'].encode('utf-8') , str(review_id), ",".join([str(x) for x in positions ])] ]
		
			# position += 1

		review_id += 1 

	write_to_file(review_dict)       
		

def write_to_file(r_dict):
	csv_writer = csv.writer(open('inverted_index_final.csv','w'), quoting=csv.QUOTE_ALL) 
	for word in r_dict.keys():
		data = sorted(r_dict[word], key=lambda review: int(review[1]))
		data = ":".join([";".join(d) for d in data])
		csv_writer.writerow([word,data]) 

	


if __name__ == '__main__':
	# data = open("/course/cs1951a/pub/final/data/extracted/yelp_academic_dataset_review.json")
	# data = open("/Users/mirajshah/Documents/CS1951A/yelp-search/data/yelp_academic_dataset_review.json")
	data = open("/Users/mirajshah/Documents/CS1951A/yelp-search/data/review_small.json")
	main(data)
