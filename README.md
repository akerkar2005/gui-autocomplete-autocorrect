# Personal Autocorrect & Autocomplete Program

## How To Run Locally
I am not hosting this project because I don't see the point in doing so, but I did make it easy 
to run it locally as long as you have conda and node package manager. I recommend micromamba 
since it's lightweight and that is what I used, but as long as you have an environment, you should be good.
This should also be simple if you have node package manager. If you don't, follow these steps
`https://nodejs.org/en/download`.

### Setup script
I made a setup script that does everything written in Backend and Frontend sections of this README file. 
If you want, you can try running it but I won't guarantee that it will work. Don't forget to follow the 
instructions at the end (I can't automate activating the conda environment within a subshell without running 
conda init which is overkill; just do the last step yourself hehe).

### Backend
Since I am using an Express framework
```
npm install
```
while on the server directory to install the required packages.

Set up a Python environment with Python version 3.12. For conda, you can go to the server directory 
and make an env with the environment.yml file:
```
conda env create --file environment.yml
```
and it should download the required packages automatically. You must cd into the server/python directory and run 
`pip install .`, which will run setup.py. It is possible pybind11 didn't install. Do that with conda:
```
conda install -c conda-forge pybind11
```
After running this, you can do `pip install .` on the `server/python` directory and you finished setting up 
the server locally.
### Frontend
```
npm install
```
in the frontend directory. This should download everything you will need (don't worry, 
it's not a lot).
### Launch the App
Once you are done setting up frontend and backend, to launch the app, go to the client directory and 
run the bash command `run_application.sh` (after giving it executable permissions) to run the frontend 
and backend concurrently. This will launch the app locally.

## Beginnings Of Autocorrect & Autocomplete
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This project was originally made to experiment with the Trie data structure and to learn python. 
I started off with a simple python script, where I took in a word as input. The program, before 
taking input, would read a massive file of words that represented the entire data set 
of words the program would work with, exploiting the Trie data structure to instantly 
provide the top 3 recommendations to "complete" the word.

 However, I was not satisfied with just autocompleting words and I realized 
my "database" of words was very limited and, sometimes, incorrect (random words were present 
that no sane human would use in real life, like appled). I migrated from using a file of words 
I found from the internet to BeautifulSoup webscraping and started working on a way to implement 
autocorrections.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Even though the project itself is not exciting or unique, I learned many things from expanding 
the project from a simple input output python program to optimizing it by writing the code 
in a lower-level language and developing a full-stack application that exploits API calls 
to deliver a robust application, taking in live input and providing autocorrections and 
autocompletions in real time.

## Miscellaneous Notes
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;I am still new to Full-Stack Development, so I am still learning more 
about ways to develop a more secure program while making sure not to sacrifice performance. 
I am not confident in my application's security, but for future projects, I hope to 
be more mindful during development. I tried to maintain some level of security by preventing 
obvious DDoS attacks, limiting the number of requests per user. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;I just want it to be known that this application was mostly fueled by my curiosity of 
how autocorrections and autocompletions could be handled in a real world setting. Instead of a 
project, you can say it is more like a "research" application. A couple of algorithms I 
used for this project, such as the Levenshtein Edit Distance algorithm, were not developed 
by me, so it is unfair to call this a project from my perspective.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From the Front-End perspective, I learned a few things about React + Vite. However, I thought 
the differences between React TSX and React JSX ranged from slim to none. I like TypeScript, 
but I did not see major differences from a bird's eye POV. You can let me know if I am wrong.

## Autocorrect Notes
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Autocorrect was the most frustrating part about this project. While it is easy to find the 
minimum distance between any two words via the Levenshtein Edit Distance Dynamic Programming 
algorithm, the problem arises when we are literally trying to read the user's mind and figure 
out via brute force, comparing every possible word in our database, what possible word 
they may be misspelling. I realized I needed more than just the Levenshtein Edit Distance 
Algorithm to figure out how to find out what the user may be mispelling. I thought of two 
major ideas:

- Maintain a user-side cache for commonly misspelled words (reduce API calls)
- Implement an algorithm that calculates the Euclidean Keyboard Distance 
  between each letter given any two words.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For the second bullet point, the idea came to me when I 
tested the word "auren". The expected output is "queen, siren" for the top two recommendations. 
My program opted for other words instead, like "pure". I started to note the pattern where, 
on a phone, we tend to "mistype" incorrect letters, and the incorrect letters tend to be 
adjacent or close to the letters we wanted to actually type for the correct word we were 
thinking of. Thus, I thought of a pretty terrible solution, but it got the job done. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;I made a 2D array documenting the common letters and symbols that
we use on a common English keyboard and, whenever the Edit Distance Algorithm was called, 
the program would now calculate the total Euclidean Distance between all keys given two words, 
imposing a sizeable 
penalty if the words were of different length. I simply calculated the Euclidean Distance of 
each bi-letter comparison in linear time and added up all of the results, representing how 
close the letters are in proximity on a US keyboard given the input word and any word on the 
database (the database is limited to words of length [length(input_word) - 2, 
length(input_word) + 4] whenever a lookup is done).

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This solution has some drawbacks. I do not like the 
solution of making a 2D array in C++. I might look into a better way to derive a specific key's 
"coordinate value" on the US keyboard. There is no point in acccomodating for other languages 
as that is far beyond the scope of what I want this "research" application to entail. I will 
stick to English for now.

## Autocomplete Notes
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Autocomplete was very easy to figure out in contrast. Since 
we are working with prefixes and deriving the "closest" words given a specific prefix, the 
obvious solution is to use the Trie data structure. All we do is take in an input, for example 
appl, and then search the Trie. Assuming all words in the database have been inserted into the 
Trie, we may begin recursively searching for our best suggestions by readjusting the Trie's 
starting node to the prefix, which would be the input we typed "appl", and then go down the 
Trie. While we are going down the Trie, we will keep track of the valid words in the Trie 
with the shortest length. When you type appl, you probably wish to complete it like apple, and 
you are less likely to complete appl with application. This explains why we keep track of the 
smallest words while assuming we always start at the input prefix "appl". 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;And that's it! I never had to think about this part of 
the program again since it worked reliably. I implemented my own Hash Table and Trie Data 
Structure in C++ to make the lookups faster, and imported the Dynamic Library in the main 
Python processor program. Other than that, there were no real issues developing this part of 
the project. If only autocorrect were this simple...

## Autocorrect & Autocomplete Notes
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Now that we established what was done for each part of this 
project, how exactly were they implemented to work with each other? Autocomplete is always given 
precedence. Yes, "appl" is a mispelling, but the user wasn't done typing! If a Trie lookup 
yields an actual result, then we do NOT call the autocorrect subroutine. However, if a Trie 
lookup yields an empty result, it means that we need to check if the input word can be 
autocorrected. There is a cap for the edit distance calculation. If 5 changes had to be 
made at minimum, we do not display any results (this may change with further testing). If 
the word already exists in the database, we do not display results (done on the Front-End).

## Final Notes
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Thank you for reading my documentation on this research 
application! While the final product is not that interesting, I believed the journey to be 
better than the destination. Tries are just way too cool for me to NOT implement them, and 
the Edit Distance algorithm is also quite incredible.
