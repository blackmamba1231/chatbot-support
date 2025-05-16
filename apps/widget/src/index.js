import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Create a container div for our chat widget if it doesn't exist
const widgetContainer = document.getElementById('vogo-chat-widget-root') || (() => {
  const div = document.createElement('div');
  div.id = 'vogo-chat-widget-root';
  document.body.appendChild(div);
  return div;
})();

// Create React root and render app
const root = ReactDOM.createRoot(widgetContainer);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
