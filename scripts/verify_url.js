
/* This file, verify_url.js, will be my content script that verifies whether or not the Letterboxd profile URL
the script is currently running on, actually refers to a valid account (by inspecting page DOM).
When background script "check_profile.js" sends message "verifyProfile", this script will pick up on it: */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "verifyProfile") {

        // Invalid Letterboxd profile pages have an exclusive <body> element of class "error" and "message-dark".
        const searchElement = document.querySelector('body.error.message-dark');
        // If searchElement "gets" something, return a "true" value to the background script to imply **invalid** profile:
        if(searchElement) {
            const profileValid = false;
            sendResponse({profileValid: profileValid});
        } else {
            // Otherwise, send a "false" value back to imply **valid** profile (need two of these since you can't change the value of a const in .js):
            // NOTE: It's important to have an "else" branch here, otherwise, I'll get a runtime error...
            const profileValid = true;
            sendResponse({profileValid: profileValid});
        }
    }
});
