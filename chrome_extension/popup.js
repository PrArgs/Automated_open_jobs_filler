document.addEventListener("DOMContentLoaded", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const jobUrlInput = document.getElementById("jobUrl");
  const status = document.getElementById("status");

  jobUrlInput.value = tab.url;

  document.getElementById("submitBtn").addEventListener("click", async () => {
    const jobUrl = jobUrlInput.value;

    try {
      const response = await fetch("http://localhost:5000/submit-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: jobUrl })
      });

      const data = await response.json();
      status.textContent = data.message || "Saved!";
    } catch (err) {
      status.textContent = "Error: " + err.message;
    }
  });
});
