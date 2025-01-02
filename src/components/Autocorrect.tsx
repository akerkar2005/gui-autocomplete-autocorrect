import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Autocorrect.css';

const Autocorrect: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [caretPosition, setCaretPosition] = useState({ x: 0, y: 0 });
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [originalWord, setOriginalWord] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const MAX_SUGGESTIONS = 3; // Maximum number of suggestions

  // Define the response type
  interface SuggestionResponse {
    suggestions: string[];
  }

  // Create a Map to act like an OrderedDict for caching
  const cache = new Map<string, string[]>();

  // Load cache from localStorage
  const loadCache = () => {
    const storedCache = localStorage.getItem('autocorrectCache');
    if (storedCache) {
      console.log("cache");
      const parsedCache = JSON.parse(storedCache);
      Object.entries(parsedCache).forEach(([key, value]) => {
        cache.set(key, value);
      });
      console.log(cache);
    }
    else {
      console.log("no cache");
    }
  };

  // Save cache to localStorage
  const saveCache = () => {
    const cacheObject = Object.fromEntries(cache);
    localStorage.setItem('autocorrectCache', JSON.stringify(cacheObject));
  };

  useEffect(() => {
    loadCache(); // Load cache on component mount
    return () => {
      saveCache(); // Save cache when the component unmounts (e.g., when user closes the tab)
    };
  }, []);

  const fetchSuggestions = async (word: string) => {
    try {
      const response = await axios.post<SuggestionResponse>('http://127.0.0.1:8000/autocorrect', { input_word: word });
      setSuggestions(response.data.suggestions || []);
      // Cache the suggestions in case the word gets misspelled again
      if (response.data.suggestions.length > 0) {
        cache.set(word, response.data.suggestions.slice(0, MAX_SUGGESTIONS)); // Keep only top 3 suggestions
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([]);
    }
  };


  const debounce = (func: Function, delay: number) => {
    let timer: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timer);
      timer = setTimeout(() => func(...args), delay);
    };
  };

  const debouncedFetchSuggestions = debounce(fetchSuggestions, 300);


  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    setInputText(text);

    const words = text.split(/\s+/);
    const lastWord = words[words.length - 1];
    if (lastWord && lastWord.length < 20) {
      debouncedFetchSuggestions(lastWord);
    } else {
      setSuggestions([]);
    }
  };

  const handleCaretPosition = () => {
    if (inputRef.current) {
      const input = inputRef.current;
      const { selectionStart } = input;
      if (selectionStart !== null) {
        const rect = input.getBoundingClientRect();
        const span = document.createElement('span');
        span.style.visibility = 'hidden';
        span.style.position = 'absolute';
        span.style.whiteSpace = 'pre';
        span.textContent = input.value.substring(0, selectionStart);
        document.body.appendChild(span);

        const caretX = rect.left + span.offsetWidth;
        const caretY = rect.top + rect.height;
        setCaretPosition({ x: caretX, y: caretY });

        document.body.removeChild(span);
      }
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    const words = inputText.split(/\s+/);
    const lastWord = words[words.length - 1];
    if (lastWord !== suggestion) {
      words[words.length - 1] = suggestion;
      setInputText(words.join(' '));
      setOriginalWord(lastWord); // Store the original misspelled word
    }
    setSuggestions([]);
  };


  useEffect(() => {
    handleCaretPosition();
  }, [inputText]);

  return (
    <div>
      <input
        ref={inputRef}
        type="text"
        value={inputText}
        onChange={handleInputChange}
        style={{ width: '100%', padding: '8px', fontSize: '16px' }}
        placeholder="Type here..."
      />
      {suggestions.length > 0 && (
        <div
          className={`suggestions ${suggestions.length > 0 ? 'show' : ''}`}
          style={{
            left: Math.min(caretPosition.x, 1000),
            top: caretPosition.y,
            padding: '8px',
            borderRadius: '4px',
            zIndex: 1000,
            boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
          }}
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              value={suggestion}
              onClick={() => handleSuggestionClick(suggestion)}
            >
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default Autocorrect;

