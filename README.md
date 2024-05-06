# Scrape Letterboxd Profile Ratings Chrome Extension (Using Flask and Selenium)
<u>Version</u>: <b>1.0</b> (_This will never be updated haha_)<br>
<u>Author</u>: <b>Timan Zheng</b><br>
<u>Date</u>: <b>5/6/2024</b> (_Date of publication, the project was finished incrementally over the duration of the prior week_)<br>
<u>Description</u>: <b>A Google Chrome extension for scraping film ratings from any given Letterboxd profile and downloading them as a CSV file.</b>

## Overview
This Chrome extension leverages the Flask web framework for Python, as well as the automated-testing tool Selenium, to scrape film ratings from a given Letterboxd profile. Upon clicking the extension icon while on a valid Letterboxd profile, the extension fetches the profile ratings data, converts it into a CSV file, and downloads it in the user's browser. This CSV file is formatted according to Letterboxd's official formatting standards (see https://letterboxd.com/about/importing-data/). (**Note**: in order to run this extension, Flask and Selenium must be downloaded and configured on the user's system; the Flask server must be active prior to running the extension).

This extension demonstrates a range of technical skills, namely Chrome extension development, web scraping, and server-client architecture. Its purpose is oddly specific (_the reason for its existence will be expanded on in a later section_), but this extension offers a simple and streamlined mechanism for collecting public ratings data from Letterboxd profiles, storing them in CSV files. It is an effortless way to download personalized film ratings from online cinephiles for further analysis or archival purposes. 

### How It Works:
1. **Profile URL Validation**: This extension will only run if the tab on which it was triggered corresponds to a valid Letterboxd profile page. That is, ensuring a match syntactically (of form _http(s)://letterboxd.com/*_) but confirming that the URL refers to a legitimate account with data attached to it. The extension uses a content script (**check_profile.js**) to first verify the URL structure and then inspect the page's DOM for specific elements that indicate the profile's existence.

2. **Loading Animation**: Upon URL validation, a custom CSS and HTML animation is injected into the current tab page (by way of content script **animation.js** and the contents of **/animation**). It is little more than a circle that spins in a loop while the profile-scraping process occurs, and terminates the instant the process terminates (regardless of if the scraping completed or resulted in error). This addition is mainly to serve as a visual cue for the user, informing them that the extension functionality is working and its results are underway.

3. **Server Communication**: The Chrome extension (through its background script **check_profile.js**) communicates with a locally hosted Flask server that listens for scraping requests. (Said server must be initiated and active prior to running the extension; otherwise, the loading animation will run briefly but terminate once the fetch request yields an absent response). A GET request is sent to the Flask server with the profile URL; if successful, the backend logic is triggered.

4. **Backend Logic & Selenium Web Scraping**: The Flask server uses the browser-automation tool Selenium to navigate the given Letterboxd profile's ratings page(s), perform pagination, and scrape all rated films (their titles, release years, and 0.5-5 numerical ratings). (The logic for this web scraping is discernible and concentrated in **pull_ratings_script.py**, seen in the **/python** directory).

5. **CSV File Generation and Download**: Once the data is collected, the Flask server compiles the information into a CSV file (titled **<_profile_username_>_ratings.csv**). The background script then triggers an automatic download of the file through the current browser tab. (The CSV file is retrieved from the Flask server through a GET request from a '**/get_csv/<file_name>**' route defined in **pull_ratings_flask.py**). 

## Project Structure

```plaintext
Scrape-Profile-Ratings/
│
├── icons/
│   ├── lbs-icon-16.png
│   ├── lbs-icon-32.png
│   ├── lbs-icon-48.png
│   └── lbs-icon-128.png
│
├── python/
│   ├── __pycache__/
│   ├── original_script/
│   │   └── pull_ratings.py
│   ├── pull_ratings_flask.py
│   └── pull_ratings_script.py
│
├── scripts/
│   ├── animation/
│   │   ├── anim.css
│   │   └── loading_spinner.html
│   ├── animation.js
│   ├── verify_url.js
│   └── check_profile.js
│
├── manifest.json
└── README.md
```

## Getting Started

### Prerequisites

Ensure you have the following installed:
- **Python 3.x**
- **Flask**
- **Selenium**
- **Chrome WebDriver** (_ensure you download the required **webdriver_manager** Python package and set this up prior_)
- **Chrome browser**

### Setting Up the Flask Server

1. Navigate to the `python` directory:
   ```bash
   cd python
   ```
2. Start the Flask server:
   ```bash
   python pull_ratings_flask.py
   ```
   Read the terminal to determine what your local-host Flask server URL is (`http://***.*.*.*:****` is simply a placeholder; replace all occurrences with your respective URL).

### Loading the Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer Mode**.
3. Click on **Load unpacked** and select the root directory of this project.

## Usage

1. Visit a valid Letterboxd profile in Chrome. (_Also ensure the Flask server is running_).
2. Click on the extension icon. (_If it does not work on an initial click, you may need to double-click_).
3. If the profile URL is valid, the ratings data will be fetched, and a loading animation will be displayed.
4. Upon completion, a CSV file containing the profile's ratings data will automatically download.
<br>**NOTE**: I recommend having the Chrome service worker (for the extension) open in case any issues occur. If the Flask server is active and the service worker console indicates that a connection could not be established, I reccomend refreshing the extension and Letterboxd page.

## Python Scripts

**pull_ratings_flask.py:** Sets up a Flask server that handles requests to trigger the Selenium-based web scraping process.

**pull_ratings_script.py:** Contains the core scraping logic that uses Selenium to navigate the Letterboxd profile and extract ratings data, which is then written to a CSV file.

**pull_ratings.py:** A standalone script version of the above that can be run directly from the terminal to scrape ratings from a profile URL.

### JavaScript Scripts

**check_profile.js:** The extension's background service worker. Listens for clicks on the extension icon, checks the current URL's validity, and initiates the scraping process.

**verify_url.js:** A content script that checks the DOM for specific elements to verify if the profile URL is valid.

**animation.js:** Contains functions to show and hide the loading spinner during the scraping process.

## Some Background Information

This Chrome extension was developed mostly for fun. I initially only had the **pull_ratings.py** file which I had written myself for the purposes of analyzing differences between two archival accounts on the site. I had thought of writing a Chrome extension to integrate that logic into an extension, but the process of translating my Python code to functionally-equivalent JavaScript code seemed overly tedious, and thus I opted to incorporate Flask into the project.

Given that its functionality is rather _specific_, and the Flask aspect is somewhat of a hassle to manage for what is meant to be a convenient extension, this project is simply just a fun side project for experience purposes. And so, it will not be published on the Chrome store. (Additionally, many of the functions involved in the process are contingent on certain keys in the Letterboxd page DOM; if the team behind the site decided to restructure and overhaul their website, this extension may be immediately rendered useless).

## Technologies and Skills Demonstrated

- **Chrome Extensions Development:** Managing background service workers, content scripts, and interactions between them.
- **Web Scraping:** Using Selenium to navigate a website, locate elements, and extract data.
- **Python Flask:** Setting up a simple server to handle web requests and serve files.
- **JavaScript and CSS:** Managing asynchronous events, manipulating the DOM, and controlling styles for loading animations.
- **Regular Expressions:** Extracting structured data from URLs using regex patterns.

---