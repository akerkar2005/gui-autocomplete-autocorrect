
// server/types/index.ts
export interface AutocorrectRequest {
  input_word: string;
}

export interface AutocorrectResponse {
  suggestions: string[];
}

export interface PythonResponse {
  error?: string;
  data?: string[];
}
