# Personal Autocorrect & Autocomplete Program

## Beginnings Of This Project
  This project was originally made to experiment with the Trie data structure and learning python.
I started off with a simple python script, where I took in a word as input. The program, before
taking input, would read a massive file of words that represented the entire data set
of words the program would work with, exploiting the Trie data structure to instantly
provide the top 3 recommendations to "complete" the word. \
However, I was not satisfied with just autocompleting words and I realized 
my "database" of words was very limited and, sometimes, incorrect (random words were present 
that no sane human would use in real life, like appled). I migrated from using a file of words 
I found from the internet to BeautifulSoup webscraping and started working on a way to implement
autocorrections. \
  Even though the project itself is not exciting or unique, I learned many things from expanding 
the project from a simple input output python program to optimizing it by writing the code 
in a lower-level language and developing a full-stack application that exploits API calls 
to deliver a robust application, taking in live input and providing autocorrections and 
autocompletions in real time. 


## Miscellaneous Notes
  I am still new to Full-Stack Development, so I am still learning more 
about ways to develop a more secure program while making sure not to sacrifice performance.
I am not confident in my application's security, but for future projects, I hope to 
be more mindful during development. I tried to maintain some level of security by preventing 
obvious DDoS attacks, limiting the number of requests per user. \
I just want it to be known that this application was mostly fueled by my curiosity of 
how autocorrections and autocompletions could be handled in a real world setting. Instead of a 
project, you can say it is more like a "research" application. A couple of algorithms I 
used for this project, such as the Levenshtein Edit Distance algorithm, were not developed 
by me, so it is unfair to call this a project from my perspective.\
  From the Front-End perspective, I learned a few things about React + Vite. However, I thought 
the differences between React TSX and React JSX ranged from slim to none. I like TypeScript, 
but I did not see major differences. You can let me know if I am wrong.

## Autocorrect Notes
    Autocorrect was the most frustrating part about this project. While it is easy to find the 
minimum distance between any two words via the Levenshtein Edit Distance Dynamic Programming
algorithm, the problem arises when we are literally trying to read the user's mind and figure 
out, by brute force and comparing every possible word in our database, what possible word 
they may be misspelling. I realized I needed more than just the Levenshtein Edit Distance 
Algorithm to figure out how to find out what the user may be mispelling. I thought of two 
major ideas:

- Maintain a user-side cache for commonly misspelled words (reduce API calls)
- Implement an algorithm that calculates the Euclidean Keyboard Distance 
  between each letter given any two words.

    For the second bullet point, the idea came to me when I tested the word "auren". The expected 
output is "queen, siren" for the top two recommendations. My program opted for other words 
instead, like "pure". I started to note the pattern where, on a phone, we tend to "mistype" 
incorrect letters, and the incorrect letters tend to be adjacent or close to the letters we 
wanted to actually type for the correct word we were thinking of. Thus, I thought of a pretty 
terrible solution, but it got the job done. \ 

    I made a 2D array documenting the common letters and symbols that
we use in a regular English keyboard and, whenever the Edit Distance Algorithm was called, I also 
calculated the total Euclidean Distance between all keys given two words, putting a sizeable 
penalty if the words were of different length. I simply calculated the Euclidean Distance of 
each bi-letter comparison in linear time and added up all of the results, representing how 
close the letters are in proximity on a US keyboard given the input word and any word on the 
database (the database is limited to words of length [length(input_word) - 2, 
length(input_word) + 4] whenever a lookup is done). \
    The solution has very obvious drawbacks. I do not like the solution of making a 2D array. I might 
look in to finding a better way to figuring out where a specific key's "coordinate value" may 
be on the US keyboard. There is no point in acccomodating for other languages as that is far 
beyond the scope of what I want this "research" project to entail. I will stick to English for 
now. 
