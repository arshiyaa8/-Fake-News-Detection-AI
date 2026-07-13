chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "verifyText",
    title: "Verify Text with Dual-AI Guard",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "verifyText" && info.selectionText) {
    const selectedText = info.selectionText;

    // Direct connection to your exact local Python Flask server port
    fetch('http://127.0.0.1:5050/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: selectedText })
    })
    .then(response => response.json())
    .then(data => {
      let title = "Verification Result";
      let message = "";

      if (data.subject === "Finance") {
        title = "💰 Finance Scan Complete";
        message = `Classification: ${data.prediction}\nConfidence: ${(data.probability * 100).toFixed(1)}%`;
      } else if (data.subject === "Health") {
        title = "🩺 Health Scan Complete";
        message = `Classification: ${data.prediction}\nConfidence: ${(data.probability * 100).toFixed(1)}%`;
      } else {
        message = `${data.prediction} (${(data.probability * 100).toFixed(1)}%)`;
      }

      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png',
        title: title,
        message: message,
        priority: 2
      });
    })
    .catch(error => {
      console.error('Error:', error);
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png',
        title: 'Server Unreachable',
        message: 'Ensure app.py is actively running in your terminal on port 5050.',
        priority: 2
      });
    });
  }
});