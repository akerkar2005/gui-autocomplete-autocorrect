import os
import ctypes
import numba
import requests
import re

import tkinter as tk
from queue import Queue
import threading

import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

import json
from collections import deque
from collections import Counter
import time
from collections import OrderedDict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import platform

import MinDist
import TrieModule


# Define a request model for JSON input
class InputWordRequest(BaseModel):
    input_word: str

class SuggestionResponse(BaseModel):
    suggestions: List[str]


'''

Initializing the C functions and defining their return types
int minDistance(char *word1, char *word2)

'''

#lib_path = ""
#if platform.system() == "Darwin":
#    lib_path = os.path.join(os.getcwd(), "MinDist.dylib")
#elif platform.system() == "Linux":
#    lib_path = os.path.join(os.getcwd(), "MinDist.so") 
#c_lib = ctypes.CDLL(lib_path)
#c_lib.minDistance.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
#c_lib.minDistance.restype = ctypes.c_int
#c_lib.keyboardDist.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
#c_lib.keyboardDist.restype = ctypes.c_double


"""

This is the Trie data structure I created in Python. I used this at first, but switched to 
C++ since I observed it was a lot faster. The python code just ran too slowly and I needed 
the server to have faster responses, like 0.07 seconds, instead of waiting 0.28 seconds.

"""

"""
class Trie:

    '''

    This is a Trie data structure used for the autocomplete functionality of the program.
    Each node represents a Hash Map, where each entry has a character key and a Hash Map
    value. Essentially, this Trie data structure is a Hash Map that maps characters to new
    Hash Maps that also map characters to Hash Maps. A recursive Hash Map!

    Each node is a character of a larger word, and if we go down the Trie, we will eventually
    reach a "None" node. This represents the end of a word (this also represents that the
    current path you took is a complete and valid word that was entered into the Trie).

    '''

    def __init__(self):
        self.Trie = {}
    
    def insert(self, word: str):
        node = self.Trie
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node["EOW"] = None

    def search(self, prefix: str):
        node = self.Trie

        # Adjust node to be the Hash Map (since this Trie implementation is essentially a 
        # recursive Hash Map) that aligns with the end of the input word we wish to 
        # potentially complete. If, for any given letter, the recursive Hash Map entry 
        # does not exist, then we may conclude that the word cannot be completed given
        # our database because that given path does not exist in our Trie. For example,
        # if the input word was sppl, it could never be valid since no valid word has 
        # such an unusual prefix.

        for char in prefix:
            if char not in node:
                return []
            node = node[char]

        # If all goes well and we have adjusted node to be at the node where 
        # we start from the end letter entry in the Trie (given the input word), 
        # we may find every prefix, searching every node adjacent to the given
        # node and return 3 prefixes. We prioritize prefixes completions that are 
        # smaller since it is more likely that is how the user meant to complete 
        # the word. If you type app, for example, you probably meant apple or apply
        # and not apparent.

        return self._find_words_with_prefix(node, prefix, [], prefix)
    
    def _find_words_with_prefix(self, node: dict, prefix: str, words, orig: str):
        for char in node:
            if char == 'EOW':

                # Only 3 suggestions for autocomplete. If the length is less
                # than 3, then safely append this potential prefix to the result.

                if len(words) < 3:
                    words.append(prefix)
                else:
                    for i in range(len(words)):

                        # Prioritize smaller prefixes 

                        if len(words[i]) > len(prefix):
                            words[i] = prefix
                            break
                continue
            
            # Recursively traverse down the Trie, updating the new prefix by
            # appending the character we just processed to prefix and maintaining
            # the original prefix (strictly for debugging) in orig. This is
            # Depth First Search since we go down a path recursively until we
            # reach the end of a word and backtrack when needed to explore other
            # nodes with smaller prefixes.

            child_node = node[char]
            self._find_words_with_prefix(child_node, prefix + char, words, orig)

        # Once every relevant node has been explored, we can return the resulting list

        return words
"""

trie = TrieModule.Trie()
word_dict = {}
word_map_first = dict()
word_map_last = dict()
words = []
responses = []


"""

This is the autocomplete function that exploits the Trie data structure, looking
for 3 valid words which the input word could be a prefix of.

"""

def autocomplete(input_word: str):
    global trie
    suggestions = trie.search(input_word)
    # Sort by length first, then alphabetically
    suggestions.sort(key=lambda x: (len(x), x))
    if not suggestions:
        return []
    return suggestions

"""

This is the autocorrect function employing Levenshtein Edit Distance (Dynamic
Programming) and Keyboard Distance (Euclidean Distance between letters from 
the input word and any given word in words) to find the best suggestions for 
autocorrecting a word.

All of the edit distance algorithm is done in C. Although this is unsafe since
C is a generally unsafe language, it is extremely fast. Note that I may change
to C++ in the near future since I do not trust C as much as C++, but switching
from Python to C for the edit distance algorithm yielded much faster times for
obvious reasons.

Each letter comparison and the letter pair's Euclidean Distance on a generic en-US
keyboard is done in C as well. The keyboard itself is just a 2D array in C. I hope to
discover a better way to implement this for any keyboard, but for now, this program
implements this for English keyboards only. No special characters are given any consideration
and add nothing to the Keyboard Distance.


Args:

- words (list): the full database of words for the current program run.
- input_word (str): the word that the user has potentially misspelled.

Returns:

- res (list): List of suggestions to correct the input_word cut off to the top 3, 
              minimizing both Edit Distance and Keyboard Distance.

""" 

def autocorrect(words, input_word: str):

    res = []

    """ The code written in python below is now done in cpp """

    """for word in words:
        edit_score = MinDist.minDistance(input_word, word);
        kb_score = MinDist.keyboardDist(input_word, word);
                
        # Add word to results
        res.append((word, edit_score, kb_score))"""

    res = MinDist.compareWords(input_word, words)

    # Sort by edit distance, then keyboard distance
    res.sort(key=lambda x: (x[1], x[2]))

    # Take the top 3 results 
    res = res[:3]
    print(res)

    # Check if the smallest edit score is too large 
    if res and res[0][1] > 5.0:
        return []

    return [word for word, _, _, in res]



async def fetch_text(url, session):
    async with session.get(url) as response:
        return await response.text()


async def fetch_and_process_responses(urls):
    unique_words = set()
    word_pattern = re.compile(r'\b[a-z]+\b')
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_text(url, session) for url in urls]
        responses = await asyncio.gather(*tasks)

    for text in responses:
        for word in word_pattern.findall(text.lower()):
            unique_words.add(word)
    return unique_words 


async def do_responses():
    global responses, words
    
    words = await fetch_and_process_responses(responses)

    # Save the work to a file
    words = sorted(words, key=lambda word: (word[0], len(word)))
    with open("words.txt", "w") as f:
        f.write(f"{len(responses)}\n")
        for word in words:
            f.write(word + '\n')


async def initialize_words(word_file="words.txt"):
    global responses, words

    req_upper_bounds = [16, 20, 25, 16, 11, 14, 12, 11, 14, 3, 3, 11, 17, 7, 8, 22, 2, 13, 31, 16, 9, 4, 9, 1, 1, 1, 1]
    all_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0']

    # Can add more URLS if necessary
    for i in range(len(all_letters)):
        for j in range(1, req_upper_bounds[i]):
            responses.append('https://www.thesaurus.com/list/' + str(all_letters[i]) + '/' + str(j))

    #req_upper_bounds = [30, 32, 46, 26, 18, 22, 18, 22, 17, 5, 7, 18, 27, 12, 14, 40, 4, 21, 54, 27, 10, 8, 15, 2, 3, 3]
    #
    #for i in range(len(req_upper_bounds)):
    #    for j in range(1, req_upper_bounds[i]):
    #        responses.append('https://www.dictionary.com/list/' + str(all_letters[i])) if j == 1 else responses.append('https://www.dictionary.com/list/' + str(all_letters[i]) + '/' + str(j))
    
    # celebrities
    responses.append('https://www.instyle.com/celebrity-a-z-7481982')

    num_responses_done = 0

    try:
        with open(word_file, "r") as file:
            num_responses_done = int(open('words.txt').readline().strip())
        if num_responses_done != len(responses):
            await do_responses()
            num_responses_done = len(responses)
        else:
            with open("words.txt", "r") as file:
                file.readline()
                words = [line.strip() for line in file]
    except FileNotFoundError:
        await do_responses()



"""

This function initializes the autocorrect and autocomplete data structures,
doing all requests to load valid words when necessary (and saving work to
the file words.txt). This will be called when the client side opens the app
for the first time.


Args: None

Returns: None

"""

async def lifespan(app: FastAPI):

    # The following happens on startup of the API

    global words
    global word_map_first
    global word_map_last
    global trie
    global responses

    await initialize_words()

    words = [x.lower() for x in words]
    words = sorted(words, key=len)
    f_len = 1

    for i in range(len(words)):
        curr_word = words[i]
        trie.insert(curr_word)
        if len(curr_word) > f_len:
            word_map_last[f_len] = i
            f_len = len(curr_word)
            word_map_first[f_len] = i

    # The server runs

    yield 
    
    # What happens on shutdown 

    words = sorted(words, key=lambda word: (word[0], len(word)))
    
    with open("words.txt", "w") as f:
        f.write(f"{len(responses)}\n")
        for word in words:
            f.write(word + '\n')


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with the exact URL of your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)


"""

Every time the user types a word, the client sends an input_word to the server
backend side, and the server calls autocorrect_and_autocomplete_req to get a single
array of suggestions for the frontend to display depending on what the user input is.

When given a choice between autocomplete and autocorrect, this function always prioritizes
autocomplete since there is a bigger chance the user just isn't finished typing a word.

If the word cannot be completed and it was simply misspelled, the output to autocorrect will
be returned. Before calling autocorrect, the function will check the cache to see if users
have misspelled this specific word before, making returns easier.


Args:

- input_word (str): This represents the word the user has currently typed, and the word we will
                    try to correct or complete.

Returns:

- output (list): This represents either the autocomplete or autocorrect suggestions depending on
                 what the user input was.

"""

@app.post("/autocorrect")
def autocorrect_and_autocomplete_req(request: InputWordRequest) -> SuggestionResponse:
    global words
    global word_map_first
    global word_map_last
    global trie
    global responses

    input_word = request.input_word
    #print(f"Received Word: {input_word}")
    num_responses_done = len(responses)
    shorter_words = []
    output = []
    
    if input_word in words and len(input_word) < 44:

        # This occurs when the word is spelled correctly and we need to
        # suggests ways to complete potentially unfinished text.

        output = autocomplete(input_word)
    elif len(input_word) < 44:
        
        output = autocomplete(input_word)

        if not output:
            lower_bound = word_map_first.get(len(input_word), 0)
            upper_bound = word_map_last.get(len(input_word) + 4, 0)
            shorter_words = words[lower_bound:upper_bound + 1]
            corrected_suggestions = autocorrect(shorter_words, input_word)
            output = corrected_suggestions
    else:

        # The word is too long to be considered valid for any operations.

        output = []

    
    return SuggestionResponse(suggestions=output)



#@app.on_event("shutdown")
#def save_words_on_shutdown():
#    global words, responses
#    words = sorted(words, key=lambda word: (word[0], len(word)))
#    
#    with open("words.txt", "w") as f:
#        f.write(f"{len(responses)}\n")
#        for word in words:
#            f.write(word + '\n')





def autocorrect_and_autocomplete_req_test(input_word: str) -> List[str]:
    global words, word_map_first, word_map_last, trie, responses

    #print(f"Received Word: {input_word}")
    num_responses_done = len(responses)
    shorter_words = []
    output = []
    
    if input_word in words and len(input_word) < 44:

        # This occurs when the word is spelled correctly and we need to
        # suggests ways to complete potentially unfinished text.

        output = autocomplete(input_word)
    elif len(input_word) < 44:
        
        output = autocomplete(input_word)

        if not output:
            lower_bound = word_map_first.get(len(input_word), 0)
            upper_bound = word_map_last.get(len(input_word) + 4, 0)
            shorter_words = words[lower_bound:upper_bound + 1]
            corrected_suggestions = autocorrect(shorter_words, input_word)
            output = corrected_suggestions
    else:

        # The word is too long to be considered valid for any operations.

        output = []

    words = sorted(words, key=lambda word: (word[0], len(word)))
    
    return output






async def initialize_data_test():
    global words, word_map_first, word_map_last, trie, responses

    try:
        num_responses_done = int(open('words.txt').readline().strip())
    except:
        num_responses_done = 0

    req_upper_bounds = [40, 48, 77, 52, 31, 35, 28, 31, 33, 8, 9, 25, 37, 17, 18, 56, 5, 47, 88, 37, 23, 11, 22, 1, 4, 3, 1]
    all_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0']
        
    for i in range(len(all_letters)):
        for j in range(1, req_upper_bounds[i]):
            responses.append('https://www.merriam-webster.com/browse/thesaurus/' + str(all_letters[i]) + '/' + str(j))

    #req_upper_bounds = [30, 32, 46, 26, 18, 22, 18, 22, 17, 5, 7, 18, 27, 12, 14, 40, 4, 21, 54, 27, 10, 8, 15, 2, 3, 3]
    #
    #for i in range(len(req_upper_bounds)):
    #    for j in range(1, req_upper_bounds[i]):
    #        responses.append('https://www.dictionary.com/list/' + str(all_letters[i])) if j == 1 else responses.append('https://www.dictionary.com/list/' + str(all_letters[i]) + '/' + str(j))
    responses.append('https://www.knowyourproduce.com/fruits-and-vegetables-a-z/')
    responses.append('https://www.vegetables.co.nz/vegetable-a-z/vegetables-a-z/')
    responses.append('https://simple.wikipedia.org/wiki/List_of_fruits')
    responses.append('https://simple.wikipedia.org/wiki/List_of_vegetables')
    responses.append('https://www.boldtuesday.com/pages/alphabetical-list-of-all-countries-and-capitals-shown-on-list-of-countries-poster?srsltid=AfmBOoqRuzPIeHdHqZWc7jQT7gBKHTtr9ncYJpDAVCr_Us8aKl47Ca3e')

    def process_words(text, unique_words):
        """Process the words in the response and add unique words to the set."""
        text = text.lower()
        for word in word_pattern.findall(text):
            if word not in unique_words:
                unique_words.add(word)

    async def fetch_text(url, session):
        """Fetch text from a URL asynchronously."""
        async with session.get(url) as response:
            return await response.text()

    async def process_responses():
        """Fetch and process all URLs asynchronously."""
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_text(url, session) for url in responses]
            texts = await asyncio.gather(*tasks)

            unique_words = set()

            for text in texts:
                process_words(text, unique_words)

            return unique_words

    if num_responses_done != len(responses):
        word_pattern = re.compile(r'\b[a-z]+\b')
        words = await process_responses()  # Use 'await' properly inside the async function
        num_responses_done = len(responses)

        # Save the work to a file
        words = sorted(words, key=lambda word: (word[0], len(word)))
        with open("words.txt", "w") as f:
            f.write(f"{num_responses_done}\n")
            for word in words:
                f.write(word + '\n')
    else:
        with open("words.txt", "r") as file:
            file.readline()
            words = [line.strip() for line in file]

    words = [x.lower() for x in words]
    words = sorted(words, key=len)
    f_len = 1

    for i in range(len(words)):
        curr_word = words[i]
        trie.insert(curr_word)
        if len(curr_word) > f_len:
            word_map_last[f_len] = i
            f_len = len(curr_word)
            word_map_first[f_len] = i
    pass




# testing purposes only


asyncio.run(initialize_data_test())


print(len(words))
input_word = input("Enter word: ")

start = time.time()
print(autocorrect_and_autocomplete_req_test(input_word))
end = time.time()
dur = end - start
print("Time it took: ", dur)
