
from flask import Flask, send_file, request, jsonify
from pull_ratings_script import run_selenium_script
from flask_cors import CORS

# NOTE: "http://127.0.0.1:5000" is the Flask server opened on my end.

app = Flask(__name__) # Flask App Initialization (create instance of Flask App).
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Route def: Establishing the endpoint (URL pattern) that the server responds to when accessed through a web request.
# This Route maps a URL to a Python function (so server-side logic can be executed with responses returned based on the request received).
# Here, the "/scrape_ratings" route will trigger the Selenium script for ratings-scraping and .csv-creation (defined in "pull_ratings.script.py"):
@app.route('/scrape_ratings', methods=['GET', 'OPTIONS'])
def scrape_ratings():

    # "run_selenium_script" (with profile URL as argument) will return the path to the .csv file containing profile ratings, that was generated.
    # The profile URL must be sent with the GET request, as part of the URL, to the Flask server, which is retrieved like this:
    # "request.args" is a dictionary-like Flask object that contains all the query parameters from the URL, we know to use 'url' because "tab.url" is being sent in the fetch.
    the_url = request.args.get('url', default='some default value (should not be needed)')
    
    ratings_csv = run_selenium_script(the_url)

    # Now, the way I have it is that, if csv_file is not generated (what's returned is "None"), then I need to indicate that a scraping error has occurred (400 signal)
    # Otherwise, the file is just sent back (to indicate success):
    if ratings_csv:
        response = send_file(ratings_csv, as_attachment=True) 
    else:
        response = jsonify({'error': 'Failed to generate CSV'})
        response.status_code = 400

    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

@app.route('/get_csv/<file_name>', methods=['GET'])
def get_csv(file_name):
    return send_file(file_name, as_attachment=True, mimetype='text/csv', download_name=file_name)

# This bit below specifies that the Flask server starts only if the script is executed directly i.e., not when imported as a module in another script.
# (Basically makes sure that the server does not inadvertently start when the script is imported elsewhere).
if __name__ == '__main__':
    app.run(debug=True)
