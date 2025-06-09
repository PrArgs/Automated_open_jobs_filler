chrome.action.onClicked.addListener((tab) => {
  const jobUrl = tab.url;

  // Make a request to your local server (e.g., Flask)
  fetch("http://localhost:5000/submit-url", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ url: jobUrl })
  })
  .then(response => response.text())
  .then(data => {
    console.log("Server response:", data);
  })
  .catch(error => {
    console.error("Error sending URL:", error);
  });
});
