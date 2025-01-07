import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Autocorrect.css';

const Autocorrect: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [caretPosition, setCaretPosition] = useState({ x: 0, y: 0 });
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [originalWord, setOriginalWord] = useState('');
  const [currentLine, setCurrentLine] = useState(0);
  const [currentHeight, setCurrentHeight] = useState(500);
  const [currentWidth, setCurrentWidth] = useState(1000);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

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
    if (cache.current.has(word)) {
        console.log(`Cache hit for word: ${word}`);
        setSuggestions(cache.current.get(word) || []);
        return;
    }

    console.log(`Trying to fetch suggestions for word: ${word}`);

    try {
      const response = await axios.post<SuggestionResponse>(
                          'http://127.0.0.1:8000/autocorrect',
                          { input_word: word }
                       );
      const fetchedSuggestions = response.data.suggestions || [];
      setSuggestions(fetchedSuggestions);

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

  const debouncedFetchSuggestions = debounce(fetchSuggestions, 100);


  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    setInputText(text);
    const textarea = textareaRef.current;

    const { selectionStart } = textarea;

    const textBeforeCaret = textarea.value.substring(0, selectionStart)
    
    const words = textBeforeCaret.split(/\s+/);
    const lastWord = words[words.length - 1];

    console.log("input has changed")

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
          
          const words = textBeforeCaret.split(/\s+/);
          const lastWord = words[words.length - 1];
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
    const { selectionStart } = textarea;
    const selectionStartPos = textarea.selectionStart;
    const selectionEndPos = textarea.selectionEnd;

    /* get the current text in the input textarea */
    const textBeforeCaret = textarea.value.substring(0, selectionStart);
    const words = textBeforeCaret.split(/\s+/);
    const lastWord = words[words.length - 1];
    const newText = inputText.replace(lastWord, suggestion);
    
    setInputText(newText);

    if (textarea) {
        const newCaretPos = selectionStartPos - lastWord.length + suggestion.length;
        textarea.setSelectionRange(newCaretPos, newCaretPos);
    }

    setSuggestions([]);
    setOriginalWord('');
  };




  return (
    <div
      style={{
        display: 'grid',
        gridRows: 'auto auto' 
      }}
    >
      <h 
        style={{
          fontSize: '50px',
          padding: '7px 8px'
        }}
      >
        Hello Gays
      </h>
      <textarea
        ref={textareaRef}
        value={inputText}
        onChange={handleInputChange}
        onClick={handleInputChange}
        onKeyUp={handleInputChange}
        style={{ 
          width: `${currentWidth}px`,
          height: `${currentHeight}px`,
          padding: '7px 8px',
          fontSize: '16px',
          resize: 'none',
          transition: '0.5s ease-in-out'
        }}
        placeholder="Type here..."
      />
      <div 
        className="suggestion-wrapper"
        style={{
          width: `${currentWidth}px`,
          height: '50px',
          padding: '7px 8px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center'
        }}
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
