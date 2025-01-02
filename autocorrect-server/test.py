import subprocess
import time
import re
import pyperclip

# Dictionary for word replacements
replacement_map = {
    "hello": "hi",
    "world": "planet",
    "spple": "apple"
}

# Monitor the cursor position and avoid interference
def get_cursor_position():
    result = subprocess.run(['xdotool', 'getmouselocation'], capture_output=True, text=True)
    # Extract the position (x and y coordinates)
    position = result.stdout.split()
    x_pos = int(position[0].split(':')[1])
    y_pos = int(position[1].split(':')[1])
    return x_pos, y_pos

def get_word_under_cursor():
    # This function captures the word under the cursor using a more passive method
    # Get the position of the cursor
    x, y = get_cursor_position()
    
    # Capture the word under the cursor by using `xdotool`'s window-based approach
    subprocess.run(['xdotool', 'mousemove', str(x), str(y)])  # Move the mouse to where the cursor is
    subprocess.run(['xdotool', 'click', '1'])  # Click to focus on the text editor (this doesn't interfere)
    
    # Simulate selecting the word under the cursor (no interference)
    subprocess.run(['xdotool', 'key', 'ctrl+shift+Left'], check=True)
    time.sleep(0.1)  # Wait a moment for the word to be selected
    subprocess.run(['xdotool', 'key', 'ctrl+c'], check=True)  # Copy the selected word
    
    # Retrieve the clipboard content (the word selected)
    clipboard_content = pyperclip.paste()
    return clipboard_content.strip()

def clean_word(word):
    # Remove unwanted symbols (!, comma, or any other punctuation) at the end of the word
    cleaned_word = re.sub(r'[!.,;?]+$', '', word)
    
    # Remove spaces at the end of the word
    cleaned_word = cleaned_word.rstrip()
    
    return cleaned_word

def replace_word(word):
    # Clean the word by removing unwanted symbols and spaces
    cleaned_word = clean_word(word)
    
    # Check if the word exists in the replacement map
    if cleaned_word in replacement_map:
        # Perform replacement
        subprocess.run(['xdotool', 'key', 'BackSpace'], check=True)  # Remove the original word
        time.sleep(0.1)
        subprocess.run(['xdotool', 'type', replacement_map[cleaned_word]], check=True)
        subprocess.run(['xdotool', 'key', 'space'], check=True)  # Add space after replacement

def main():
    last_position = None
    pause_duration = 1  # Time in seconds to wait before processing
    last_time = time.time()
    
    while True:
        # Get current cursor position
        current_position = get_cursor_position()
        
        # If the position has changed, update the last position
        if current_position != last_position:
            last_position = current_position
            last_time = time.time()  # Reset the timer when the cursor moves
        
        # Check if there's a pause in typing
        if time.time() - last_time >= pause_duration:
            # Get the word under the cursor and process it
            word = get_word_under_cursor()
            if word:
                replace_word(word)
            last_time = time.time()  # Reset the timer after processing
        
        time.sleep(0.1)  # Monitor cursor with a small delay

if __name__ == "__main__":
    main()

