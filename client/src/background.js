chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "FETCH_INPUT") {
    const { inputText, x, y } = message;

    fetch("http://127.0.0.1:8000/autocorrect", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ input_word: inputText }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Suggestions received from API: ", data);
        sendResponse({ suggestions: data.suggestions || [], x, y });
      })
      .catch((error) => {
        console.error("Error fetching suggestions:", error);
        sendResponse({ suggestions: [], x, y, error: error.message });
      });

    return true; // Indicates sendResponse is asynchronous
  }
});

