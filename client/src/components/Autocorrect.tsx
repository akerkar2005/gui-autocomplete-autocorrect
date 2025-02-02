import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Autocorrect.css';

const Autocorrect: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [caretPosition, setCaretPosition] = useState({ x: 0, y: 0 });
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [backendData, setBackendData] = useState([{}]);
  const [currIndex, setCurrIndex] = useState(0);
  const [auto, setAuto] = useState(0);
  const [prevWord, setPrevWord] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const API_BASE_URL = 'http://100.80.0.51:3000';


  const MAX_SUGGESTIONS = 3; // Maximum number of suggestions

  // Define the response type
  interface SuggestionResponse {
    suggestions: string[];
  }

  // Create a Map to act like an OrderedDict for caching
  const cache = useRef<Map<string, string[]>>(new Map());

  // Load cache from localStorage
  const loadCache = () => {
    const storedCache = localStorage.getItem('autocorrectCache');
    if (storedCache) {
      //console.log("cache");
      const parsedCache = JSON.parse(storedCache);
      cache.current = new Map(Object.entries(parsedCache));
      console.log('Loaded cache: ', cache.current);
    }
    else {
      console.log('no cache found in localStorage');
    }
  };

  // Save cache to localStorage
  const saveCache = () => {
    const cacheObject = Object.fromEntries(cache.current);
    localStorage.setItem('autocorrectCache', JSON.stringify(cacheObject));
    console.log('Saved cache: ', cacheObject);
  };

  useEffect(() => {
    loadCache(); // Load cache on component mount
    return () => {
      saveCache(); // Save cache when the component unmounts (e.g., when user closes the tab)
    };
  }, []);

  const fetchSuggestions = async (word: string) => {
    if (word.length <= 1 || word.length > 22)
      return;
    if (cache.current.has(word)) {
        console.log(`Cache hit for word: ${word}`);
        console.log(`size of cache: ${cache.current.get(word).length}`);
        const cacheHit = cache.current.get(word);
        if (cacheHit.length == 1 && cacheHit[0] === word)
            setSuggestions([]);
        else
            setSuggestions(cache.current.get(word) || []);
        return;
    }

    console.log(`Trying to fetch suggestions for word: ${word}`);

    try {
      const response = await fetch(`${API_BASE_URL}/api/autocorrect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input_word: word })
      });
      console.log("Response from server: ", response);

      if (!response.ok) 
        throw new Error(`HTTP Error! Status: ${response.status}`);

      const data = await response.json();
      console.log("Response JSON", data);
      const fetchedSuggestions = data.suggestions.data || [];
      if (fetchedSuggestions.length == 1 && fetchedSuggestions[0] === word) 
          setSuggestions([]);
      else {
          setSuggestions(fetchedSuggestions);
      }

      // Cache the suggestions in case the word gets misspelled again
      if (fetchedSuggestions.length > 0) {
        cache.current.set(word, fetchedSuggestions.slice(0, MAX_SUGGESTIONS)); // Keep only top 3 suggestions
        saveCache();
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

  const debouncedFetchSuggestions = debounce(fetchSuggestions, 20);


  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    setAuto(0);
    setInputText(text);
    const textarea = textareaRef.current;

    const { selectionStart } = textarea;

    const textBeforeCaret = textarea.value.substring(0, selectionStart);
    const entireText = textarea.value;
    
    const words = textBeforeCaret.split(/\s+/);
    const entireWords = entireText.split(/\s+/);
    const lastWord = entireWords[words.length - 1];


    if (lastWord && lastWord.length < 20) {
      debouncedFetchSuggestions(lastWord);
    } else {
      setSuggestions([]);
    }
  };

  const calculateCaretPositionAndLine = () => {
      if (textareaRef.current) {
          const textarea = textareaRef.current;
          const { selectionStart } = textarea;
          /* get the current text in the input textarea */
          const textBeforeCaret = textarea.value.substring(0, selectionStart);
          const entireText = textarea.value;
          
          const words = textBeforeCaret.split(/\s+/);
          const entireWords = entireText.split(/\s+/);
          const lastWord = entireWords[words.length - 1];
          

          if (lastWord && lastWord.length < 20) {
            console.log("Caret Position Fetch Suggest", lastWord);
            debouncedFetchSuggestions(lastWord);
          } else {
            setSuggestions([]);
          }
      }
  }

  const handleCaretPosition = () => {
    calculateCaretPositionAndLine();
  };

  const handleSuggestionClick = (suggestion: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const { selectionStart } = textarea;

    /* get the current text in the input textarea */
    const textBeforeCaret = textarea.value.substring(0, selectionStart);
    const words = textBeforeCaret.split(/\s+/);
    const entireWords = textarea.value.split(/\s+/);
    if (words[words.length - 1] != entireWords[words.length - 1])
      return;
    const lastWord = entireWords[words.length - 1];
    setPrevWord(lastWord);
    setAuto(1);

    const newText = inputText.replace(new RegExp(`\\b${lastWord}\\b`), suggestion);

    setInputText(newText);

    const newCaretPos = selectionStart - lastWord.length + suggestion.length;
    textarea.setSelectionRange(newCaretPos, newCaretPos);

    setSuggestions([]);
  };

  const handleInvert = () => {
      handleSuggestionClick(prevWord);
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if ((e.altKey || e.metaKey || e.ctrlKey) && e.key === '1' && suggestions.length >= 1 && suggestions[0]) {
      handleSuggestionClick(suggestions[0]);
    } else if ((e.altKey || e.metaKey || e.ctrlKey) && e.key === '2' && suggestions.length >= 2 && suggestions[1]) {
      handleSuggestionClick(suggestions[1]);
    } else if ((e.altKey || e.metaKey || e.ctrlKey) && e.key === '3' && suggestions.length >= 2 && suggestions[2]) {
      handleSuggestionClick(suggestions[2]);
    } else if (e.key === ' ' && suggestions.length > 0) {
      handleSuggestionClick(suggestions[0]);
    } else if (e.key === 'Backspace') {
      if (auto == 1 && prevWord) {
        handleInvert();
        e.preventDefault();
        setPrevWord("");
        setAuto(0);
      }
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [suggestions]);

  return (
    <div
      style={{
        display: 'grid',
        gridRows: 'auto auto' 
      }}
    >
      <h 
        className="header"
      >
        Autocorrect & Autocomplete
      </h>
      <textarea
        className="text-area-wrapper"
        ref={textareaRef}
        value={inputText}
        onChange={handleInputChange}
        onClick={handleInputChange}
        onKeyUp={handleInputChange} 
        placeholder="Type here..."
      />
      <div 
        className="suggestions-wrapper"
      >
        {suggestions.length > 0 && (
          <div
            className={`suggestions ${suggestions.length > 0 ? 'show' : ''}`}
            style={{
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
    </div>
  );
};

export default Autocorrect;
