/**
 * Vogo.Family Chat Widget Embed Script
 * 
 * Add this script to your WooCommerce website to embed the chat widget:
 * <script src="https://your-widget-host.com/embed.js" id="vogo-chat-widget"></script>
 */

(function() {
  // Configuration - change this to your deployed widget URL
  const WIDGET_URL = 'http://localhost:3000'; // Change to your production URL when deployed
  
  function loadScript(src, callback) {
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = src;
    script.async = true;
    
    if (callback) {
      script.onload = callback;
    }
    
    document.head.appendChild(script);
  }
  
  function loadStyles(href) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = href;
    document.head.appendChild(link);
  }
  
  function initializeWidget() {
    // Create container for the widget
    const container = document.createElement('div');
    container.id = 'vogo-chat-widget-root';
    document.body.appendChild(container);
    
    // Load widget scripts and styles
    loadStyles(`${WIDGET_URL}/static/css/main.css`);
    loadScript(`${WIDGET_URL}/static/js/main.js`);
  }
  
  // Check if document is already loaded
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(initializeWidget, 1);
  } else {
    document.addEventListener('DOMContentLoaded', initializeWidget);
  }
})();
