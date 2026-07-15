if (!window.__dualAiGuardLoaded) {
window.__dualAiGuardLoaded = true;

let floatingWidget = null;
let lastClickX = 120;
let lastClickY = 120;
let lastCheckedText = '';

// Track where the user right-clicked, so we know where to place the panel
document.addEventListener('contextmenu', (e) => {
  lastClickX = e.clientX;
  lastClickY = e.clientY;
});

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function removeFloatingWidget() {
  if (floatingWidget) {
    floatingWidget.remove();
    floatingWidget = null;
  }
  lastCheckedText = '';
}

function clampPosition(x, y, width) {
  const maxX = window.innerWidth - width - 10;
  const maxY = window.innerHeight - 60;
  return {
    x: Math.min(Math.max(10, x), Math.max(10, maxX)),
    y: Math.min(Math.max(10, y), Math.max(10, maxY))
  };
}

function makeDraggable(el, handle) {
  let offsetX = 0, offsetY = 0, isDown = false;

  handle.addEventListener('mousedown', (e) => {
    isDown = true;
    offsetX = e.clientX - el.getBoundingClientRect().left;
    offsetY = e.clientY - el.getBoundingClientRect().top;
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    el.style.left = (e.clientX - offsetX) + 'px';
    el.style.top = (e.clientY - offsetY) + 'px';
  });

  document.addEventListener('mouseup', () => { isDown = false; });
}

function showLoadingWidget() {
  removeFloatingWidget();
  const { x, y } = clampPosition(lastClickX, lastClickY, 260);

  const widget = document.createElement('div');
  widget.id = 'dual-ai-guard-widget';
  widget.style.cssText = `
    position: fixed;
    top: ${y}px;
    left: ${x}px;
    background: #1e1e2e;
    color: #ddd;
    padding: 12px 16px;
    border-radius: 10px;
    font-family: -apple-system, Segoe UI, Roboto, sans-serif;
    font-size: 13px;
    z-index: 2147483647;
    box-shadow: 0 8px 24px rgba(0,0,0,0.45);
    border: 1px solid #3a3a4a;
  `;
  widget.textContent = '🔎 Checking selected text...';
  document.body.appendChild(widget);
  floatingWidget = widget;
}

function createResultWidget(data) {
  removeFloatingWidget();
  const { x, y } = clampPosition(lastClickX, lastClickY, 320);

  const widget = document.createElement('div');
  widget.id = 'dual-ai-guard-widget';
  widget.style.cssText = `
    position: fixed;
    top: ${y}px;
    left: ${x}px;
    width: 320px;
    max-height: 400px;
    overflow-y: auto;
    background: #1e1e2e;
    color: #f0f0f0;
    border-radius: 10px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.45);
    font-family: -apple-system, Segoe UI, Roboto, sans-serif;
    font-size: 13px;
    z-index: 2147483647;
    border: 1px solid #3a3a4a;
  `;

  const isFake = data.prediction && data.prediction.toLowerCase().includes('suspicious');
  const isUncertain = data.prediction && data.prediction.toLowerCase().includes('uncertain');
  const isError = data.subject === 'Error' || data.subject === '';
  const badgeColor = isError ? '#888' : (isUncertain ? '#7f8c8d' : (isFake ? '#e74c3c' : '#2ecc71'));
  const subjectIcon = data.subject === 'Finance' ? '💰' : data.subject === 'Health' ? '🩺' : '⚠️';

  widget.innerHTML = `
    <div id="dag-header" style="
      background: #292a3a;
      padding: 10px 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: move;
      border-bottom: 1px solid #3a3a4a;
      border-radius: 10px 10px 0 0;
    ">
      <span style="font-weight: 600;">${subjectIcon} Verifi AI</span>
      <span id="dag-close" style="cursor:pointer; padding: 0 4px; font-size: 18px; line-height: 1;">&times;</span>
    </div>
    <div style="padding: 14px;">
      <div style="
        display: inline-block;
        background: ${badgeColor};
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
        margin-bottom: 8px;
      ">${escapeHtml(data.prediction || 'Unknown')}</div>
      <div style="color:#aaa; margin-bottom: 10px;">
        ${data.probability ? 'Confidence: ' + (data.probability * 100).toFixed(1) + '%' : ''} ${data.subject ? '· ' + escapeHtml(data.subject) : ''}
      </div>
      ${data.related ? `<div style="border-top:1px solid #3a3a4a; padding-top:8px; margin-top:8px; white-space: pre-line; color:#ccc; font-size:12px;">${escapeHtml(data.related)}</div>` : ''}
    </div>
  `;

  document.body.appendChild(widget);
  floatingWidget = widget;

  document.getElementById('dag-close').addEventListener('click', removeFloatingWidget);
  makeDraggable(widget, document.getElementById('dag-header'));
}

function autoCheckSelection(text) {
  lastCheckedText = text;
  showLoadingWidget();

  fetch('http://127.0.0.1:5050/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  .then(response => response.json())
  .then(data => createResultWidget(data))
  .catch(error => {
    console.error('Verifi AI auto-check error:', error);
    createResultWidget({
      prediction: 'Server Unreachable',
      probability: 0,
      subject: '',
      related: 'Ensure app.py is actively running on port 5050.'
    });
  });
}

// While the panel is open, automatically re-check whenever the user
// selects a new piece of text — no right-click needed for follow-up checks.
let selectionDebounceTimer = null;
document.addEventListener('mouseup', () => {
  if (!floatingWidget) return; // only auto-refresh while a panel is already showing

  clearTimeout(selectionDebounceTimer);
  selectionDebounceTimer = setTimeout(() => {
    const selection = window.getSelection();
    const text = selection ? selection.toString().trim() : '';

    if (!text || text === lastCheckedText) return;

    if (selection.rangeCount > 0) {
      const rect = selection.getRangeAt(0).getBoundingClientRect();
      lastClickX = rect.left;
      lastClickY = rect.bottom + 10;
    }

    autoCheckSelection(text);
  }, 400); // short debounce so it fires once the selection settles
});

chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'SHOW_LOADING') {
    showLoadingWidget();
  } else if (message.type === 'SHOW_RESULT') {
    lastCheckedText = message.originalText || lastCheckedText;
    createResultWidget(message.data);
  } else if (message.type === 'SHOW_ERROR') {
    createResultWidget({
      prediction: 'Server Unreachable',
      probability: 0,
      subject: '',
      related: message.error || 'Make sure app.py is running on port 5050.'
    });
  }
});
}