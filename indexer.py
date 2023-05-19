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

            # Update the index for the current token and URL
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

# Calculate the inverse document frequency for each token
for token in index:
    idf = math.log(total_pages / len(index[token]))
    for url in index[token]:
        index[token][url] = index[token][url] / word_count[url] * idf

# Save the index to a file using pickle
with open("index.pickle", "wb") as f:
    pickle.dump(index, f)

# Print some statistics about the index
print("Number of pages indexed:", total_pages)
print("Number of unique tokens:", len(index))
print("Size of index on disk:", os.path.getsize("index.pickle") // 1000, "KB")
