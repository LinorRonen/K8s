import requests
from multiprocessing import Process
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app


def start_flask_app():
    """
    Function to start the Flask app in a separate process.
    """
    app.run(port=5002)

def test_website_is_reachable():
    """
    Test to check if the website is reachable.
    """
    print("Starting the test...")
    url = 'http://127.0.0.1:5002'
    try:
        print(f"Attempting to reach: {url}")
        response = requests.get(url)
        print(f"Received response with status code: {response.status_code}")
        if response.status_code == 200:
            print("Test passed: Website is reachable.")
        else:
            print(f"Test failed: Expected status code 200, but got {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Test failed: Unable to reach the website. Error: {e}")

if __name__ == "__main__":
    flask_process = Process(target=start_flask_app)
    flask_process.start()

    time.sleep(5)

    test_website_is_reachable()

    flask_process.terminate()
    flask_process.join()
