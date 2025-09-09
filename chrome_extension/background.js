// Background service worker for Job Application Tracker

// Check if user has a spreadsheet set up
async function checkUserSpreadsheet() {
  const result = await chrome.storage.local.get(['spreadsheetId']);
  return result.spreadsheetId;
}

// Create new spreadsheet for user
async function createUserSpreadsheet() {
  try {
    const response = await fetch('http://localhost:5000/create-spreadsheet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({})
    });
    const data = await response.json();
    if (data.spreadsheetId) {
      await chrome.storage.local.set({ spreadsheetId: data.spreadsheetId });
      return data.spreadsheetId;
    }
  } catch (error) {
    console.error('Error creating spreadsheet:', error);
  }
  return null;
}

// Start Flask server automatically using a different approach
async function startFlaskServer() {
  try {
    // Try to start server by opening a new tab with a special URL
    // This will trigger the server to start
    const response = await fetch('http://localhost:5000/start-server', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (response.ok) {
      console.log('Flask server started successfully');
      return true;
    } else {
      console.error('Failed to start server');
      return false;
    }
  } catch (error) {
    console.error('Server start error:', error);
    return false;
  }
}

// Check if server is running and start if needed
async function ensureServerRunning() {
  try {
    const response = await fetch('http://localhost:5000/health', { 
      method: 'GET',
      mode: 'no-cors' // Avoid CORS issues
    });
    return true; // Server is running
  } catch (error) {
    console.log('Server not running, attempting to start...');
    return await startFlaskServer();
  }
}

// Wait for server to be ready
async function waitForServer(maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await fetch('http://localhost:5000/health');
      if (response.ok) {
        console.log('Server is ready!');
        return true;
      }
    } catch (error) {
      // Server not ready yet
    }
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
  }
  return false;
}

// Initialize extension
async function initialize() {
  // Ensure server is running first
  const serverStarted = await ensureServerRunning();
  
  if (serverStarted) {
    // Wait for server to be ready
    const serverReady = await waitForServer();
    if (!serverReady) {
      console.error('Server failed to start within timeout');
      return;
    }
  }
  
  let spreadsheetId = await checkUserSpreadsheet();
  if (!spreadsheetId) {
    spreadsheetId = await createUserSpreadsheet();
  }
}

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  initialize();
});

// Listen for extension startup
chrome.runtime.onStartup.addListener(() => {
  initialize();
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'submitJob') {
    // Ensure server is running before submitting
    ensureServerRunning().then(() => {
      submitJob(request.data)
        .then(response => sendResponse(response))
        .catch(error => sendResponse({ error: error.message }));
    });
    return true;
  }
  
  if (request.action === 'ensureServer') {
    ensureServerRunning().then(success => {
      sendResponse({ success });
    });
    return true;
  }
});

// Submit job data to server
async function submitJob(jobData) {
  try {
    const response = await fetch('http://localhost:5000/submit-job', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jobData)
    });
    return await response.json();
  } catch (error) {
    console.error('Error submitting job:', error);
    throw error;
  }
}
