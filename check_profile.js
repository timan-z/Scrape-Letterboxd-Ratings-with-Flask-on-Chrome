
// This file, check_profile.js, is my primary "background service worker."

/* For my own self reference:
- chrome.action is the API used to manipulate the appearance of the "browser action" (the extension icon).
- The function passed to addListener automatically receives a "tab" object as its argument (contains info about the tab that was active when event triggered).
- All console.log(...); statements for the background script appear in the "service worker" console of the Chrome browser (for the respective extension).
- DEBUGGING+REMINDER: "action:{}" is included in the manifest.json file or else "onClicked" will not be recognized.
*/
chrome.action.onClicked.addListener(tab => {
    // The extension runs when the icon is clicked. Afterwards, the URL will be investigated to ensure it refers to a valid Letterboxd profile:

    /* Notes about the REGEX below (for self-learning purposes):
    - The first and last "/" character delimit the REGEX pattern.
    - The other "/" characters serve as Escape Characters (for ensuring the following character should be matched exactly instead of treated as special). 
    - The "?" character means the REGEX can end with one "/" (preceding) character or none at all. 
    */
    if(/https:\/\/letterboxd\.com\/[a-zA-Z0-9_]+\/?/.test(tab.url)) {

        console.log('The current URL ', tab.url, ' IS valid for the Letterboxd Profile Ratings extension; it WILL run here.');
        
        // Send a message to the content scripts instructing it to check if the URL is valid (by checking the DOM):
        chrome.tabs.sendMessage(tab.id, {action:"verifyProfile"}, function(response) {
            // "tab.id" specifies the target of this message being sent (the content scripts operating on said tab).
            // "action:" specifies the action to take by the content script upon receiving the message, function(response) handles the response, etc.
            if(response) {
                // verify_url.js sends back a true "profileValid" constant if the profile is valid:
                if(response.profileValid) {
                    console.log('The current URL ', tab.url, ' has been validated as a legitimate profile.');

                    // Trigger a "spinning" load animation to indicate that the ratings-scraping operation is in process (by signalling to the content scripts):
                    chrome.tabs.query({active:true, currentWindow:true}, tabs=>{
                        console.log("Initiating loading animation while the ratings-scraping operation begins.");
                        chrome.tabs.sendMessage(tabs[0].id, {action: 'showSpinner'});
                    });

                    // Extract the username section of the profile URL (will be needed for the .csv file download):
                    const username_sect = tab.url.match(/https:\/\/letterboxd\.com\/([^/]+)/)[1];
                    const csv_download = username_sect + "_ratings.csv";

                    // Send the Fetch request to the Flask server to initiate the Python-Selenium script for scraping ratings:
                    // NOTE: (to self), remember to ensure you are using backticks in the fetch below rather than single quotes.
                    fetch(`http://127.0.0.1:5000/scrape_ratings?url=${encodeURIComponent(tab.url)}`, {
                        method: 'GET',
                        mode: 'cors'
                    })
                    // The Flask server will return a .csv file if valid, an indication of error (status code 400) if not:
                    .then(response => {

                        // Turn off the "spinning" load animation (ratings-scraping operation is COMPLETE):
                        chrome.tabs.query({active: true, currentWindow:true}, tabs=> {
                            console.log("Terminating loading animation as the ratings-scraping operation is complete.");
                            chrome.tabs.sendMessage(tabs[0].id, {action: 'hideSpinner'});
                        });

                        // Check if the status code returned was non-400 or 400:
                        if(response.ok) {

                            /* The .csv file will be stored on the Flask server, which I can target through the /get_csv/<file name> route
                            and download it through the current Chrome tab (using chrome.downloads API): */
                            chrome.downloads.download({
                                url: `http://127.0.0.1:5000/get_csv/${csv_download}`,
                                filename: csv_download,
                                saveAs: false // NOTE: true/false toggles whether or not the download appears as a "Save As" pop-up or if it occurs automatically.
                            });

                        } else {
                            console.log('Failed to scrape ratings due to a server error');
                            return Promise.reject(response); // Jump straight to ".catch(error => {"
                        }
                    })
                    .catch(error => {

                        // Turn off the "spinning" load animation (ratings-scraping operation is COMPLETE):
                        chrome.tabs.query({active: true, currentWindow:true}, tabs=> {
                            console.log("Terminating loading animation as the ratings-scraping operation is complete.");
                            chrome.tabs.sendMessage(tabs[0].id, {action: 'hideSpinner'});
                        });

                        console.error('Error in fetching and scraping profile ratings: ', error);
                    });

                } else {
                    console.log('The current URL ', tab.url, ' does not refer to a legitimate profile. The extension will not run.');
                }

            } else {
                console.log('Attempt to verify the current URL for profile validity failed; no response was received.');
                console.log('Check if the Flask server is active prior to running the extension, that may be the issue.');
            }
        })

    } else {
        console.log('The current URL is NOT valid for the Letterboxd Profile Ratings extension; it will NOT run here.');
    }
});
