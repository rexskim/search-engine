import os
import re
import json
import nltk
import pickle
import math
from bs4 import BeautifulSoup
import concurrent.futures
import time


query = input("Enter Query: ")
start = time.time()
portStem = nltk.stem.PorterStemmer()

query_tokens = nltk.word_tokenize(query)
stemmed_query = [portStem.stem(token) for token in query_tokens]

# Load partial indexes
num_partial_indexes = 5
partial_indexes = []
for partial_index_num in range(num_partial_indexes):
    partial_index_filename = f"partial_index_{partial_index_num}.pickle"
    with open(partial_index_filename, "rb") as f:
        partial_index = pickle.load(f)
        partial_indexes.append(partial_index)


# Perform search in partial indexes
url_scores = {}
for token in stemmed_query:
    for partial_index in partial_indexes:
        if token in partial_index:
            for url, token_frequency in partial_index[token].items():
                if url in url_scores:
                    url_scores[url] += token_frequency
                else:
                    url_scores[url] = token_frequency


# Sort and display top results
ranked_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)
top_5_urls = ranked_urls[:5]

for url, score in top_5_urls:
    print(url)
    print("TF-IDF Score:", score)
    print()

end = time.time()
elapsed_time = end - start
final_res = elapsed_time * 1000
print("Execution Time:", final_res, "milliseconds")


