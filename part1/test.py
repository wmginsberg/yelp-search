import csv

def longest_common_substring(s1, s2):
	m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
	longest, x_longest = 0, 0
	for x in xrange(1, 1 + len(s1)):
		for y in xrange(1, 1 + len(s2)):
			if s1[x - 1] == s2[y - 1]:
				m[x][y] = m[x - 1][y - 1] + 1
				if m[x][y] > longest:
					longest = m[x][y]
					x_longest = x
			else:
				m[x][y] = 0
	
	return longest

f = open('inverted_index_final.csv')

csv = csv.reader(f)

words = []

for row in csv:
	words.append(row[0])

for word in words:
	for word2 in words:
		if word != word2 and longest_common_substring(word, word2) > 4:
			print word + " " + word2
