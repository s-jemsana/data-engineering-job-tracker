import sqlite3
import requests
import os
from dotenv import load_dotenv

# Loads the .env contents into memory
load_dotenv()

# Get hidden keys from memory and assign to variables
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


def extract_data():
    """Extracts raw software developer job data from the Adzuna SA API."""
    # Target country "za" (South Africa) for search page 1
    url = "https://api.adzuna.com/v1/api/jobs/za/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": "developer",
        "results_per_page": 5   # Keeping it small for easy testing 
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        # Raise an exception if the server returns a bad status code (like 404 or 500)
        response.raise_for_status()

        raw_data = response.json()
        print("Data extraction successful")
        return raw_data
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during extraction: {e}")
        return {}
    

def transform_data(raw_jobs):
    """Cleans and standardizes raw job data."""
    cleaned_jobs = []

    for job in raw_jobs:
        # Clean strings using whitespace stripping
        title = job.get("title", "Unknown Title").strip()
        company = job.get("company", "Unknown Company").strip()
        location = job.get("location", "Remote").strip()

        # Check for missing or empty salary info and apply a default fallback value
        raw_salary = job.get("salary", "")
        if not raw_salary or raw_salary.strip() == "":
            salary = "Not Specified"
        else:
            salary = raw_salary.strip()

        url = job.get("url", "").strip()

        # Only add the job if it has a valid application link
        if url:
            cleaned_jobs.append({
                "job_title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "job_url": url
            })

    print(f"Data transformation successful. Cleaned {len(cleaned_jobs)} records")
    return cleaned_jobs

def load_data(cleaned_jobs, db_name="job_tracker.dp"):
    """Loads cleaned job data into a local SQLite relational database."""
    # Connect to SQLite (will create the file if it doesn't exist)
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()


    # Create the jobs table with strict constraints
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS jobs (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   job_title TEXT NOT NULL,
                   company TEXT NOT NULL,
                   location TEXTX NOT NULL,
                   salary TEXT,
                   job_url TEXT NOT NULL UNIQUE
                   )
                   """)
    inserted_count = 0

    # Loop through the list of dictionaries and insert data safely
    for job in cleaned_jobs:
        try:
            cursor.execute("""
                           INSERT INTO jobs (job_title, company, location, salary, job_url)
                           VALUES (?, ?, ?, ?, ?)
                           """, (
                               job["job_title"],
                               job["company"],
                               job["location"],
                               job["salary"],
                               job["job_url"]
                           ))
            inserted_count += 1
        except sqlite3.IntegrityError:
            # Catch duplicates based on the UNIQUE job_url constraint
            continue
    
    # Commit the transaction to save changes permanently
    connection.commit()
    connection.close()

    print(f"Data loading successful. Saved {inserted_count} new records to {db_name}.")





if __name__ == "__main__":
    print("Starting Job Tracker Data Pipeline")

    # Extraction layer
    raw_data = extract_data()

    
    if raw_data:
        # Transformation layer
        cleaned_data = transform_data(raw_data)

        # Loading layer
        load_data(cleaned_data)

    print("Pipeline Execution Finished")