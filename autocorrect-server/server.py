from flask import Flask, request, jsonify
from flask_cors import CORS
import ctypes
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Path to the shared library
lib_path = os.path.join(os.getcwd(), "MinDist.so")
c_lib = ctypes.CDLL(lib_path)

# Example Python function for autocorrect
def autocorrect_or_autocomplete(input_word):
    # Placeholder logic: Call your MinDist and Trie functions here
    # Return top 3 suggestions for autocorrect/autocomplete
    # This is simplified; integrate your real logic here
    return {
        "autocomplete": ["suggestion1", "suggestion2", "suggestion3"],
        "autocorrect": ["correction1", "correction2", "correction3"],
        "status": "success"
    }

# Define API endpoint
@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.json
    input_word = data.get("word", "")
    if not input_word:
        return jsonify({"error": "No input word provided"}), 400
    
    result = autocorrect_or_autocomplete(input_word)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5173, debug=True) 
