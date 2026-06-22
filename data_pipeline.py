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