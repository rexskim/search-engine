import os
import re
import json
import nltk
import pickle
import math
import time
from bs4 import BeautifulSoup

portStem = nltk.stem.PorterStemmer()

query = input("Enter Query: ")
query_tokens = nltk.word_tokenize(query)
stemmed_query = [portStem.stem(token) for token in query_tokens]

with open("index.pickle", "rb") as f:
    index = pickle.load(f)

url_scores = {}

for token in stemmed_query:
    if token in index:
        # for each url and its tf value add tf to total score
        for url, token_frequency in index[token].items():
            if url in url_scores:
                url_scores[url] += token_frequency
            else:
                url_scores[url] = token_frequency

ranked_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)


top_5_urls = ranked_urls[:5]

for url, score in top_5_urls:
    print(url)
    print("TF-IDF Score:", score)
    print()

# ranked_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)
#
#
# top_5_urls = ranked_urls[:5]

# for url, score in top_5_urls:
#    print(url)
#    print("TF-IDF Score:", score)
#    print()
