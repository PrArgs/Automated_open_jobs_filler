document.addEventListener("DOMContentLoaded", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const jobUrlInput = document.getElementById("jobUrl");
  const status = document.getElementById("status");
  const submitBtn = document.getElementById("submitBtn");

  jobUrlInput.value = tab.url;

  // Check if server is running when popup opens
  try {
    const response = await fetch('http://localhost:5000/health');
    if (response.ok) {
      console.log('Server is already running');
    }
  } catch (error) {
    console.log('Server not running, will start when needed');
  }

  document.getElementById("submitBtn").addEventListener("click", async () => {
    const jobUrl = jobUrlInput.value;
    
    // Disable button and show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";
    status.textContent = "Starting server and processing...";

    try {
      // Try to start server if not running
      try {
        const startResponse = await fetch('http://localhost:5000/start-server', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        
        if (startResponse.ok) {
          status.textContent = "Server starting up...";
          // Wait for server to be ready
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      } catch (error) {
        console.log('Server start failed, continuing anyway');
      }
      
      // Submit the job URL
      const response = await fetch("http://localhost:5000/submit-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: jobUrl })
      });

      const data = await response.json();
      status.textContent = data.message || "Job URL saved successfully!";
      status.style.color = "green";
    } catch (err) {
      status.textContent = "Error: " + err.message;
      status.style.color = "red";
    } finally {
      // Re-enable button
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit Job URL";
    }
  });
});
