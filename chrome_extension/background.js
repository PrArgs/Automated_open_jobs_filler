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
      body: JSON.stringify({
        token: await getAuthToken()
      })
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

// Get OAuth token
async function getAuthToken() {
  try {
    const token = await chrome.identity.getAuthToken({ interactive: true });
    return token;
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
}

// Initialize extension
async function initialize() {
  let spreadsheetId = await checkUserSpreadsheet();
  if (!spreadsheetId) {
    spreadsheetId = await createUserSpreadsheet();
  }
  
  // Start local server if not running
  fetch('http://localhost:5000/health')
    .catch(() => {
      // Server not running, start it
      chrome.runtime.sendNativeMessage('com.jobtracker.server', 
        { command: 'start_server' },
        (response) => {
          console.log('Server start response:', response);
        }
      );
    });
}

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  initialize();
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'submitJob') {
    submitJob(request.data)
      .then(response => sendResponse(response))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Will respond asynchronously
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
      body: JSON.stringify({
        ...jobData,
        token: await getAuthToken()
      })
    });
    return await response.json();
  } catch (error) {
    console.error('Error submitting job:', error);
    throw error;
  }
}
