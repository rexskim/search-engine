import os
import json
import nltk
import pickle
import math
from bs4 import BeautifulSoup

# Define the directory containing the web pages to index
directory = "DEV"

# Create a list of all subdirectories in the directory
dev_directories = [os.path.join(directory, sub_directories) for sub_directories in os.listdir(directory)]

# Initialize the index, word count, and total page count
index = {}
word_count = {}
total_pages = 0

# Initialize the Porter stemmer
portStem = nltk.stem.PorterStemmer()

# number of pages to go through before creating new partial index
create_new_partial_index_every_THIS_pages = 10000

# Counter to keep track of the number of partial indicies created
partial_index_count = 0

# Loop through each subdirectory
for sub_directories in dev_directories:
    print("Indexing pages in", sub_directories)

    # Loop through each file in the subdirectory
    for filename in os.listdir(sub_directories):
        # Open the JSON file containing the page data
        with open(os.path.join(sub_directories, filename), "r") as f:
            page_data = json.load(f)

        # Extract the URL and HTML content from the page data
        url = page_data["url"]
        html_content = page_data["content"]

        # Use BeautifulSoup to parse the HTML content and extract the text
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(" ", strip=True)

        # Tokenize the text using NLTK
        tokens = nltk.word_tokenize(text)

        # Update the word count for the current page
        word_count[url] = len(tokens)

        # Loop through each token and add it to the index
        for token in tokens:
            # Stem the token using the Porter stemmer
            stemmed_token = portStem.stem(token)

            # Update the index for the current token and URL\
            # d in d
            if stemmed_token in index:
                if url in index[stemmed_token]:
                    index[stemmed_token][url] += 1
                else:
                    index[stemmed_token][url] = 1
            else:
                index[stemmed_token] = {url: 1}

        # Increment the page count and print progress
        total_pages += 1
        print("Indexed", url)

        # Check if it's time to offload the index to a partial index on disk
        if total_pages % (create_new_partial_index_every_THIS_pages) == 0:
            partial_index_filename = f"partial_index_{partial_index_count}.pickle"
            with open(partial_index_filename, "wb") as f:
                partial_index = {token: index[token] for token in index}
                pickle.dump(partial_index, f)
            partial_index_count += 1
            index = {}  # Reset the index in memory

# Save the remaining index to a partial index on disk
partial_index_filename = f"partial_index_{partial_index_count}.pickle"
with open(partial_index_filename, "wb") as f:
    partial_index = {token: index[token] for token in index}
    pickle.dump(partial_index, f)
    partial_index_count += 1

# Merge the partial indexes into a single index
merged_index = {}
for partial_index_num in range(partial_index_count):
    partial_index_filename = f"partial_index_{partial_index_num}.pickle"
    with open(partial_index_filename, "rb") as f:
        partial_index = pickle.load(f)
        for token in partial_index:
            if token in merged_index:
                merged_index[token].update(partial_index[token])
            else:
                merged_index[token] = partial_index[token]

# Calculate the inverse document frequency for each token in the merged index
for token in merged_index:
    docs_containing_token = len(merged_index[token])
    idf = math.log(total_pages / docs_containing_token)

    for url in merged_index[token]:    
        tf = merged_index[token][url] / word_count[url]
        merged_index[token][url] = tf * idf

# rewrite term counts to tf_idf in partial indicies
num_partial_indexes = 6
for partial_index_num in range(num_partial_indexes):
    # open partial index with term counts
    partial_index_filename = f"partial_index_{partial_index_num}.pickle"
    with open(partial_index_filename, "rb") as f:
        partial_index = pickle.load(f)

    # update term counts to tf_idf
    for token in partial_index:
        for url in partial_index[token]:
            if token in merged_index and url in merged_index[token]:
                partial_index[token][url] = merged_index[token][url]
            else:
                partial_index[token][url] = 0

    # overwrite partial index with tf_idf
    with open(partial_index_filename, "wb") as f:
        pickle.dump(partial_index, f)
    
# Save the merged index to a file using pickle
with open("index.pickle", "wb") as f:
    pickle.dump(merged_index, f)

# Print some statistics about the index
print("Number of pages indexed:", total_pages)
print("Number of unique tokens:", len(merged_index))
print("Size of index on disk:", os.path.getsize("index.pickle") // 1000, "KB")

