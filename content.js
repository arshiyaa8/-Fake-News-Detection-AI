if (!window.__dualAiGuardLoaded) {
window.__dualAiGuardLoaded = true;

let floatingWidget = null;
let lastClickX = 120;
let lastClickY = 120;

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
  const isError = data.subject === 'Error' || data.subject === '';
  const badgeColor = isError ? '#888' : (isFake ? '#e74c3c' : '#2ecc71');
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
      <span style="font-weight: 600;">${subjectIcon} Dual-AI Guard</span>
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

chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'SHOW_LOADING') {
    showLoadingWidget();
  } else if (message.type === 'SHOW_RESULT') {
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
