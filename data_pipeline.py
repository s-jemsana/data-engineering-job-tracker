import sqlite3
import requests

def extract_data():
    """Extracts raw job data from the target public API."""
    url = "https://demo-api.wethinkcode.co.za/jobs" # Simulated target endpoint

    try:
        response = requests.get(url, timeout=10)
        # Raise an exception if the server returns a bad status code (like 404 or 500)
        response.raise_for_status()

        print("Data extraction successful")
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Extraction failed due to network error: {e}")
        return []