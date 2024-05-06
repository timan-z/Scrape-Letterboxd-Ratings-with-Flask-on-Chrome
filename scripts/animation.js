
/* This file, animation.js, will be the content script that defines the functions for manipulating the loading animation
and interacting with the current-tab DOM, CSS, and so on. */

// Function to show the spinner:
function showSpinner() {
    let css = document.createElement('link');
    css.href = chrome.runtime.getURL('scripts/animation/anim.css');

    css.rel = 'stylesheet';
    document.head.appendChild(css);

    fetch(chrome.runtime.getURL('scripts/animation/loading_spinner.html'))
        .then(response => response.text())
        .then(html => {
            document.body.insertAdjacentHTML('beforeend', html);
        });
}

// Function to hide the spinner:
function hideSpinner() {
    let overlay = document.getElementById("spinning-loader-id");
    if(overlay) {
        overlay.remove();
    }
}

// Listen for messages from "check_profile.js" for when to initiate and terminate the spinning animation:
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action=="showSpinner") {
        showSpinner();
    }
    if (message.action=="hideSpinner") {
        hideSpinner();
    }
});
