import sys
import json
import asyncio
from typing import List, Dict, Set
import aiohttp
import re
from pathlib import Path
from dataclasses import dataclass
import TrieModule
import MinDist
from bs4 import BeautifulSoup

@dataclass
class ProcessorConfig:
    max_word_length: int = 44
    max_suggestions: int = 3
    cache_file: str = "words.txt"

class WordProcessor:
    def __init__(self, config: ProcessorConfig = ProcessorConfig()):
        self.trie: TrieModule.Trie = TrieModule.Trie()
        self.words: List[str] = []
        self.word_map_first: Dict[int, int] = {}
        self.word_map_last: Dict[int, int] = {}
        self.config = config
        self.responses: List[str] = []

    async def fetch_words(self) -> Set[str]:
        """Fetch words asynchronously from sources."""
        async def fetch(url, session):
            try:
                async with session.get(url, timeout=10) as response:
                    return await response.text()
            except Exception as e:
                return ""

        urls = []

        req_upper_bounds = [40, 48, 77, 52, 31, 35, 28, 31, 33, 8, 9, 25, 37, 17, 18, 56, 5, 47, 88, 37, 23, 11, 22, 1, 4, 3, 1]
        all_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0']

        for i in range(len(all_letters)):
            for j in range(1, req_upper_bounds[i]):
                urls.append('https://www.merriam-webster.com/browse/thesaurus/' + str(all_letters[i]) + '/' + str(j))

        urls.append('https://www.knowyourproduce.com/fruits-and-vegetables-a-z/')
        urls.append('https://www.vegetables.co.nz/vegetable-a-z/vegetables-a-z/')
        urls.append('https://simple.wikipedia.org/wiki/List_of_fruits')
        urls.append('https://simple.wikipedia.org/wiki/List_of_vegetables')
        urls.append('https://www.boldtuesday.com/pages/alphabetical-list-of-all-countries-and-capitals-shown-on-list-of-countries-poster?srsltid=AfmBOoqRuzPIeHdHqZWc7jQT7gBKHTtr9ncYJpDAVCr_Us8aKl47Ca3e')
        urls.append('https://www.thefreedictionary.com/A-very-long-list-of-adverbs,-not-all-of-which-end-in--ly.htm')
        urls.append('https://byjus.com/english/list-of-adverbs/')


        unique_words = set()


        async with aiohttp.ClientSession() as session:
            responses = await asyncio.gather(*[fetch(url, session) for url in urls])

        for response in responses:
            # Parse the HTML content
            soup = BeautifulSoup(response, 'html.parser')
            # Extract text from the parsed HTML
            text = soup.get_text()
            # Find all words using regex
            words = re.findall(r"\b[a-zA-Z']+\b", text.lower())
            unique_words.update(words)

            #for response in responses:
            #    unique_words.update(word_pattern.findall(response.lower()))

        return unique_words

    def _build_trie_and_maps(self) -> None:
        """Build trie and word maps."""
        current_length = 1
        for i, word in enumerate(self.words):
            self.trie.insert(word)
            if len(word) > current_length:
                self.word_map_last[current_length] = i
                current_length = len(word)
                self.word_map_first[current_length] = i

    async def initialize(self):
        """Initialize processor and load words."""
        cache_path = Path(self.config.cache_file)

        if cache_path.exists():
            with open(cache_path, "r") as file:
                self.words = [line.strip() for line in file]
        else:
            self.words = sorted(await self.fetch_words())
            with open(self.config.cache_file, "w") as file:
                file.writelines(f"{word}\n" for word in self.words)

        self.words = sorted([word.lower() for word in self.words], key=len)
        self._build_trie_and_maps()

    def process_word(self, input_word: str) -> List[str]:
        """Process input word and return suggestions."""
        try:
            if not input_word or len(input_word) >= self.config.max_word_length:
                return []

            # Try autocomplete first
            output = self.trie.search(input_word)
            
            # If no autocomplete results, try autocorrect
            if not output and input_word not in self.words:
                lower = len(input_word)
                if (len(input_word) > 5):
                    lower -= 2
                lower_bound = self.word_map_first.get(lower, 0)
                upper_bound = self.word_map_last.get(len(input_word) + 4, 0)
                shorter_words = self.words[lower_bound:upper_bound + 1]
                
                # Fix: MinDist.compareWords should return [(word, distance, etc)]
                output = MinDist.compareWords(input_word, shorter_words)
                
                # Ensure output is sorted and sliced correctly
                if output:
                    output.sort(key=lambda x: (x[1], x[2]))  # Sort by distance or other metric
                    output = output[:self.config.max_suggestions]

                if output and output[0][1] > 5.0:
                    return []  # If all suggestions are bad, return empty list

                return [word for word, _, _ in output]  # Ensure we are just returning words

            return output[:self.config.max_suggestions]  # Ensure we return limited suggestions

        except Exception as e:
            print(f"Error processing word: {e}")
            return []

async def main():
    processor = WordProcessor()
    await processor.initialize()

    while True:
        data = sys.stdin.readline()
        if not data:
            break

        try:
            request = json.loads(data)
            word = request.get("word", "")
            response = processor.process_word(word)
            print(json.dumps({"data": response}))
        except Exception as e:
            print(f"Error handling request: {e}")
        
        sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())

