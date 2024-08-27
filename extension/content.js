console.log('Content script loaded');

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  console.log('Message received in content script:', request);
  if (request.action === "getYouTubeUrl") {
    if (window.location.hostname === "www.youtube.com" && window.location.pathname.startsWith("/watch")) {
      console.log('Sending YouTube URL:', window.location.href);
      sendResponse({url: window.location.href});
    } else {
      console.log('Not a valid YouTube video page');
      sendResponse({error: "No es una página de video de YouTube válida"});
    }
  }
  return true;  // Keeps the message channel open for asynchronous response
});