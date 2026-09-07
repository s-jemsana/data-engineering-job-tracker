import sqlite3
import requests
import os
from dotenv import load_dotenv

# Loads the .env contents into memory
load_dotenv()

# Get hidden keys from memory and assign to variables
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
    raise ValueError("Missing Adzuna credentials. Set ADZUNA_APP_ID and ADZUNA_APP_KEY in the Airflow environment.")


def extract_data(search_term="software developer", results_per_page=10):
    """Extracts raw job data from the Adzuna SA API with dynamic search parameters."""
    # Target country "za" (South Africa) for search page 1
    url = "https://api.adzuna.com/v1/api/jobs/za/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": search_term,
        "results_per_page": results_per_page
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        # Raise an exception if the server returns a bad status code (like 404 or 500)
        response.raise_for_status()

        raw_data = response.json()
        print(f"Data extraction for '{search_term}': successful")
        return raw_data
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during extraction: {e}")
        return {}
    

def transform_data(raw_api_data):
    """Cleans and standardizes raw job data."""
    clean_jobs_list = []

    # Adzuna packages its list of jobs inside the "results" key
    raw_jobs = raw_api_data.get("results", [])

    for job in raw_jobs:
        # Clean strings using whitespace stripping
        title = job.get("title", "").strip()
        url = job.get("redirect_url", "").strip()

        # Defensive parsing for nested company dictionary
        company_info = job.get("company", {})
        company = company_info.get("display_name", "Not Specified").strip()

        # Defensive parsing for nested locatio list
        location_info = job.get("location", {})
        location_list = location_info.get("area", [])
        location = ", ".join(location_list) if location_list else "South Africa"

        # Handle salary data (Adzuna provides max values as numbers)
        salary_max = job.get("salary_max")
        salary_min = job.get("salary_min")

        if salary_max:
            salary = f"Up to R{int(salary_max):,}"
        elif salary_min:
            salary = f"From R{int(salary_min):,}"
        else:
            salary = "Not Specified"


        # Only add the job if it has a valid application link
        clean_job = {
            "title": title,
            "company": company,
            "location": location,
            "salary": salary,
            "url": url
        }

        clean_jobs_list.append(clean_job)

    print(f"Successfully transformed and cleaned {len(clean_jobs_list)} records")
    return clean_jobs_list

def load_data(clean_jobs_list, db_name="job_tracker.db"):
    """Loads cleaned job data into a local SQLite relational database."""
    # Connect to SQLite (will create the file if it doesn't exist)
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()


    # Create the jobs table with strict constraints
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS jobs (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   company TEXT NOT NULL,
                   location TEXT NOT NULL,
                   salary TEXT,
                   url TEXT NOT NULL UNIQUE,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )
                   """)
    inserted_count = 0

    # Loop through the list of dictionaries and insert data safely
    for job in clean_jobs_list:
        try:
            cursor.execute("""
                           INSERT INTO jobs (title, company, location, salary, url)
                           VALUES (?, ?, ?, ?, ?)
                           """, (
                               job["title"],
                               job["company"],
                               job["location"],
                               job["salary"],
                               job["url"]
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