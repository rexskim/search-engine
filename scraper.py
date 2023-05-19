import re
import pickle
import nltk
# nltk.download('stopwords')

from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import parse_qs
from urllib.parse import urldefrag

from collections import Counter
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from simhash import Simhash, SimhashIndex

visited_links = set()
simhash_index = SimhashIndex([], k=3)


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    global visited_links, simhash_index, longest_page_link
    global visited_links, simhash_index
    
    links = []
    if resp.status == 200:
        content = resp.raw_response.content
        # if page is empty return empty list (no links to extract)
        if not content:
            return links
        
        soup = BeautifulSoup(content, 'html.parser')
        # remove html tags and extracts text
        page_text = soup.get_text()
        page_text = soup.get_text()  
        
        
        simhash = Simhash(page_text)
        # check if page is similar to previously visited pages
        if simhash_index.get_near_dups(simhash):
            return links
        simhash_index.add(url, simhash)
        
        for link in soup.find_all('a'):
            link = link.get('href')
            # check if link is valid and has not been visted yet
            if link and is_valid(link) and link not in visited_links:
                links.append(link)
                if urljoin(url, link) != resp.url:
                    print("Detected redirect from {} to {}".format(urljoin(url,link),resp.url))
                visited_links.add(link) 

    # calls longest_page and assigns longest page link to the global variable
    # longest_page_link = longest_page()
                
    return links


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not any(parsed.netloc.endswith(domain) for domain in [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]):
            return False
        # if url contains unwanted paths (pages with no info)
        if re.search(r".*(/calendar|/mailto:http|/files/|/publications/|/papers/)", parsed.path.lower()):
            return False
        # checks if first 9 characters of url path matches /wp-json/
        if re.match(r"/wp-json/", parsed.path.lower()[0:9]):
            return False
        
        # will parse for action parameter, if paramteter is action to download is found, rejects URL
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if "action" in params and "download" in params["action"]:
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise

# finds longest page based on number of words
def longest_page():
    numWords = 0
    longestPage = None
    
    # parse through pages
    for link in visited_links:
        soup = BeautifulSoup(link, 'html.parser')
        text = soup.get_text()
        pageCount = 0
        # count how many words on page
        for word in re.split('[^a-zA-Z0-9]', text):
            word = word.lower()
            pageCount += 1
        if pageCount > numWords:
            numWords = pageCount
            longestPage = link
    
    return longestPage


# finds the 50 most common words
def common_words():
    stopwords_list = set(stopwords.words('english'))
    word_count = Counter()

    for link in visited_links:
        soup = BeautifulSoup(link, 'html.parser')
        text = soup.get_text()
        words = re.findall(r'\b\w+\b', text.lower())
        # if word is is not in stopwords list, add to word_count
        word_count.update(word for word in words if word not in stopwords_list)
        
    return [word for word, count in word_count.most_common(50)]

# find all unique urls
def unique_urls():
    # for each url, find the first like url part, and if its unique add it to count.
    unique_urls = set()
    for link in visited_links:
        parsed = urlparse(link)
        # remove fragment
        url_without_fragment = urldefrag(link).link
        unique_urls.add(url_without_fragment)

    return len(unique_urls)

# finds subdomains in ics.uci.edu domain
def count_subdomains():
    subdomains = {}
    subdomain_count = []
    for link in visited_links:
        parsed_url = urlparse(link)
        # split domain into different parts
        domain_parts = parsed_url.netloc.split('.')
        # check if domain is in ics.uci.edu
        if parsed_url.netloc.endswith('.ics.uci.edu'):
            # extract first part of domain
            subdomain = domain_parts[-4]
        # add to set
        if subdomain not in subdomains:
            subdomains[subdomain] = set()
        
        subdomains[subdomain].add(link)
        
        # loop through each subdomain and count how many there are
        for subdomain, links in subdomain.items():
            pages_count = len(links)
            subdomain_count.append(('http://{}.ics.uci.edu'.format(subdomain), pages_count))
            
    return sorted(subdomain_count)
    
    
def main():
    get_unique_urls = unique_urls()
    print("Unique pages: ", get_unique_urls)
    
    get_longest_page = longest_page()
    print("Longest page: ", get_longest_page)
    
    get_common_words = common_words()
    print("50 most common words: ", get_common_words)
    
    get_subdomains = count_subdomains()
    print("Subdomains found: ", get_subdomains)
    
    
if __name__ == '__main__':
    main()