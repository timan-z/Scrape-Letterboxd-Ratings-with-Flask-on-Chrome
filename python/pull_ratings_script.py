
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import csv
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# The argument "profile_url" passed to this function "run_selenium_script" will be the URL of the profile that I want to scrape ratings from.
def run_selenium_script(profile_url):
    # I want this extension to be able to run wherever the browser is on, on the profile page, so I need to do some string manipulation.
    # The profile URL will be of form "https://letterboxd.com/*", "https://letterboxd.com/*/", or "https://letterboxd.com/*/*", and I want to
    # manipulate each of them so that it just becomes "https://letterboxd.com/*", and that begins with checking if it is already in that state: 
    if re.match(r'https://letterboxd\.com/[a-z0-9_]+$', profile_url):
        pass
    else:
        # Removing everything after the username part of the URL (I don't want a final "/" character):
        username_sect = re.match(r'(https://letterboxd\.com/[a-z0-9_]+)', profile_url)
        if username_sect:
            profile_url = username_sect.group(1)
        else:
            pass

    # Extract the username from the URL (I'll need this later for the .csv download file naming):
    match = re.search(r'https://letterboxd\.com/([^/]+)', profile_url)
    dl_username = match.group(1)

    # This script only scrapes RATINGS, so I'm ignoring "watched" films etc. This is manual web scraping so the 
    # specific URL I want is "URL" + "/films/rated/.5-5/by/date/" (which will be appended to the extracted URL):
    append_this = "/films/rated/.5-5/by/date/"
    profile_url = profile_url + append_this

    # Initializing the Chrome driver:
    chrome_options = Options()
    chrome_options.add_argument('--headless') # Ensures Chrome runs in headless mode (so no GUI appears during the web scraping).
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    csv_file = None # DEBUG: Just in case...

    # Scraping process:
    try:
        # Open the Letterboxd profile:
        driver.get(profile_url)
        film_data = []
        cont_iteration = True

        while cont_iteration:
            time.sleep(2) # Brief buffer to ensure the webpage loads.

            # I want to first target the <div id="content" class="site-body"> element within the HTML contents (and get to the "poster-list"-class element from there):
            content_element = driver.find_element(By.ID, "content")
            # Extract the <ul> element that contains each <li> element (each film, basically):
            poster_list = content_element.find_element(By.CLASS_NAME, "poster-list")
            # poster_list is the <ul> element (unordered list), and within it are <li> elements:
            list_items = poster_list.find_elements(By.TAG_NAME, "li")

            # Iterating through all of the <li> elements:
            for li in list_items:
                buffer = li.find_element(By.CLASS_NAME, "film-poster")
                buffer2 = li.find_element(By.CLASS_NAME, "poster-viewingdata")

                # Extracting the data I am interested for the .csv file (film name, release year, and rating)
                data_film_name = buffer.get_attribute("data-film-name")
                data_film_year = buffer.get_attribute("data-film-release-year")
                star_rating = buffer2.find_element(By.CLASS_NAME, "rating").text
                num_rating = None

                # If there are any "," characters within data-film-name, the string must be enclosed within (") quotation marks for the .csv file:
                if "," in data_film_name:
                    data_film_name = '\"' + data_film_name + '\"'

                # Convert star-symbol rating to numerical rating (0.5-5, 0.5 increments):
                if star_rating == "½":
                    num_rating = 0.5
                elif star_rating == "★":
                    num_rating = 1
                elif star_rating == "★½":
                    num_rating = 1.5
                elif star_rating == "★★":
                    num_rating = 2
                elif star_rating == "★★½":
                    num_rating = 2.5
                elif star_rating == "★★★":
                    num_rating = 3
                elif star_rating == "★★★½":
                    num_rating = 3.5
                elif star_rating == "★★★★":
                    num_rating = 4
                elif star_rating == "★★★★½":
                    num_rating = 4.5
                else:
                    num_rating = 5

                # Save that data in the film_data list (will be ported to the .csv file afterwards):
                film_data.append((data_film_name, data_film_year, num_rating))
            
            # Now I want to check to see if there is an "older" (next page) button:
            buffer = driver.find_element(By.CLASS_NAME, "pagination")
            # Within the "pagination"-class element, there are potentially two "paginate-nextprev"-class elements within it.
            buffer2 = buffer.find_elements(By.CLASS_NAME, "paginate-nextprev")

            # Inspect the, potentially two, elements that were extracted:
            for nextprev in buffer2:
                # Check to see if this is the nextprev element with the "next"-class element within it:
                try:
                    #inner_element = nextprev.find_element(By.CLASS_NAME, "next")
                    # If this is the "older" (next page) button, I want to confirm that "paginate-disabled" is not also associated with the "paginate-nextprev" element:
                    class_attributes = nextprev.get_attribute("class")

                    if "paginate-disabled" in class_attributes.split():
                        # If this is the case, I want to break the loop:
                        cont_iteration = False
                    else:
                        # If this is not the case, then I want to click the "next" button: 
                        driver.find_element(By.CLASS_NAME, "next").click()

                except NoSuchElementException:
                    # This is the nextprev element containing the "previous"-class element within it, which can be ignored: 
                    pass

        # Write scraped data to a .csv file:
        csv_file = dl_username + '_ratings.csv' # The .csv file name will be "<letterboxd_profile>_ratings.csv":
        with open(csv_file, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Year', 'Rating'])
            writer.writerows(film_data)

    finally:
        # Information of interest has been scraped, so the chrome window can be closed (or an error happened, and this is just closed here at the end):
        driver.quit()
    
    # Return the path of the generated CSV file back to pull_ratings_flask.py:
    return csv_file
    # DEBUG: ^ If an error happened in the try-block, csv_file will have None as its value (and I can use this to determine status upon return).
