chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "verifyText",
    title: "Verify Text with Dual-AI Guard",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "verifyText" && info.selectionText) {
    const selectedText = info.selectionText;

    // Make sure content.js is actually present on this tab before messaging it
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });
    } catch (e) {
      console.error('Could not inject content script (restricted page?):', e);
      return;
    }

    chrome.tabs.sendMessage(tab.id, { type: 'SHOW_LOADING' }, () => {
      if (chrome.runtime.lastError) console.error(chrome.runtime.lastError.message);
    });

    fetch('http://127.0.0.1:5050/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: selectedText })
    })
    .then(response => response.json())
    .then(data => {
      chrome.tabs.sendMessage(tab.id, { type: 'SHOW_RESULT', data }, () => {
        if (chrome.runtime.lastError) console.error(chrome.runtime.lastError.message);
      });
    })
    .catch(error => {
      console.error('Error:', error);
      chrome.tabs.sendMessage(tab.id, {
        type: 'SHOW_ERROR',
        error: 'Ensure app.py is actively running on port 5050.'
      }, () => {
        if (chrome.runtime.lastError) console.error(chrome.runtime.lastError.message);
      });
    });
  }
});