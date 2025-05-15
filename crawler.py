import csv
import os
import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

INDEX_FILE = 'index.csv'
BASE_URL = 'https://quotes.toscrape.com/'

#Each crawl takes around 22 mins
def crawl_site(url=BASE_URL):
    index = {}
    visited = set()
    queue = [url]
    count = 0
    
    while queue:
        current_url = queue.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)
        count += 1
        
        time.sleep(6) #6 seconds politeness window
        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {current_url}: {e}")
            continue
        
        #parse the page and extract text
        text = BeautifulSoup(response.text, 'html.parser').get_text()
        index_page(text, current_url, index)
        #add a number to log the progress of the crawl
        print(f"[{count}] Crawled: {current_url}")
        
        #now crawl the links on the page
        for link in BeautifulSoup(response.text, 'html.parser').find_all('a', href=True):
            href = link['href']
            if href.startswith('/'):
                next_url = urljoin(current_url, href)
                if next_url not in visited:
                    queue.append(next_url)
                    
    return index                
      
def index_page(text, url, index): #tokenises the text and creates an inverted index
       words = re.findall(r"\w+", text.lower())
       for position, word in enumerate(words):
           if len(word) < 3: #ignore words with less than 3 characters
               continue     
           if word not in index:
               index[word] = {}
           if url not in index[word]:
                index[word][url] = {
                    'frequency': 0,
                    'positions': []
                }          
           index[word][url]['frequency'] += 1
           index[word][url]['positions'].append(position)   
           
def save_index(index, filename=INDEX_FILE): #save the index to a CSV file
    with open (filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'URL', 'Frequecny', 'Positions'])
        for words, urls in index.items():
            for url, data in urls.items():
                pos = ','.join(map(str, data['positions'])) #convert list of positions to a string
                writer.writerow([words, url, data['frequency'], pos]) 
                
def load_index(filename=INDEX_FILE): #load the index from a CSV file
    index = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                word = row['Word']
                url = row['URL']
                freq = int(row['Frequecny'])
                postions = list(map(int, row['Positions'].split(','))) #convert string of positions to a list of integers
                if word not in index:
                    index[word] = {}
                index[word][url] = {
                    'frequency': freq,
                    'positions': postions
                }
        print("Index loaded")        
    except FileNotFoundError:
        print("Error: Index file not found. Run build first.")
    return index

def print_word(word, index):
    if word not in index:
        print(f"Word {word} not found in index.")
        return
    print(f"\nInverted index for word '{word}':")
    print(f'Number of counts : {len(index[word])}')
    
    sorted_rank = sorted(index[word].items(), key=lambda x: x[1]['frequency'], reverse=True)
    
    for url, data in sorted_rank:
        print(f' URL       : {url}')
        print(f' Frequency : {data["frequency"]}')
        print(f' Positions : {data["positions"]}\n')
        
def find_word(phrase, index):
    words = phrase.lower().split()
    if not any (word in index for word in words):
        print(f"None of the words found in index.")
        return
    
    urls = [set(index[word].keys()) for word in words if word in index] #get the URLs for all words in the phrase    
    all_urls = set.union(*urls) #find the union of all URLs for the words in the phrase
    
    common_urls = set.intersection(*urls) if urls else set() #find the common URLs for all words in the phrase
    
    phrase_scores = {}
    match_scores = {}

    for url in all_urls:
        position_list = [index[word][url]['positions'] for word in words if url in index[word]]
        phrase_found = False
        if len(position_list) == len(words):
            count = 0
            for i in position_list[0]:
                if all((i+j) in position_list[j] for j in range(1, len(words))):
                    count += 1
            if count > 0:
                phrase_scores[url] = count 

        if not phrase_found:
            total_frequency = sum(index[word][url]['frequency'] for word in words if url in index[word])
            match_scores[url] = total_frequency
            
    ranked_phrases = sorted(phrase_scores.items(), key=lambda x:x[1], reverse=True)
    ranked_individual_words = sorted(match_scores.items(), key=lambda x:x[1], reverse=True)
    
    print('\nURLs for the exact phrase:')
    print(f"Number of counts : {len(ranked_phrases)}")
    if ranked_phrases:
        for url, score in ranked_phrases:
            print(f"{url} (Score: {score})")
    else:
        print("No URLs found for the exact phrase.")
    
    print('\nRanked URLs for individual words:')
    print(f"Number of counts : {len(ranked_individual_words)}")
    if ranked_individual_words:
        for url, score in ranked_individual_words:
            words_in_url = [word for word in words if url in index.get(word, {})]
            print(f"{url} (Score: {score}) (Words: {', '.join(words_in_url)})")
    else:
        print("No URLs found for individual words.")
    
test = {}
loaded = False

while True:   
    user_input = input("Enter command: ")
    
    if user_input == 'build':
        test = crawl_site()
        save_index(test)
        loaded = True
        print("Index built and saved.")  
        
    elif user_input == 'load':
        if not os.path.exists(INDEX_FILE):
            print("Error: Index file not found. Run build first.")
        else:
            test = load_index()
            loaded = bool(test)
    
    elif user_input.startswith('print'):
        parts = user_input.split()
        if len(parts) == 2:
            if not loaded:
                print("Error: Index not loaded. Run load first.")
            else:
                word = parts[1].lower()    
                print_word(word, test)
        else:
            print("Usage: print <word>")
             
    elif user_input.startswith('find'):
        if not loaded:
            print("Error: Index not loaded. Run load first.")
            continue
        parts = user_input.split()
        if len(parts) >= 2:
            phrase = ' '.join(parts[1:])
            find_word(phrase, test)
        else:
            print("Usage: find <phrase>")     
        
    elif user_input == 'exit':
        print('Exitted')
        break          