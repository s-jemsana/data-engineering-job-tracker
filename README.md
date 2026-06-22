# 📊 Data Engineering Job Tracker


## 1. Problem Statement & Motivation

Job hunting as a software engineer is overwhelming. Internships and junior roles open and close rapidly across multiple platforms, making it difficult to keep track of deadlines, requirements, salary transparency, and application links. This automated data pipeline aggregates software engineering roles into a centralized database. Instead of manually scrolling through websites, the system extracts, structures, and logs the data programmatically, mirroring a standard production ETL (Extract, Transform, Load) architecture used in data engineering teams worldwide.


## 2. System Design & Architectural Overview

To keep the project lightweight, scalable, and independent of external database servers, the application utilizes a modular Python engine combined with an embedded SQLite database.

```
[ EXTRACT ]   --> Fetch raw JSON payloads from public Job APIs using HTTP GET.
     │
[ TRANSFORM ] --> Clean strings via whitespace stripping; map missing values to defaults.
     │
[   LOAD    ] --> Securely persist structured records into a relational SQLite database.
```


## 3. Database Schema Design

A relational database layout ensures data integrity and structural reliability. The jobs table uses strict text types and handles unique entries gracefully through an autoincrementing primary key.

|Column Name|Data Type|Constraints|Description|
| :---| :---| :---| :---|
| id| INTEGER| PRIMARY KEY AUTOINCREMENT| A unique identifier generated automatically for each job listing.
|job_title| TEXT| NOT NULL| The designation of the role (e.g., "Junior Python Developer").
|company| TEXT| NOT NULL| The name of the hiring organization.
|location| TEXT| -| Target location or if the role is remote/hybrid.
|salary| TEXT| -| Financial range or compensation metrics (defaults to "Not Specified").
|job_url| TEXT| NOT NULL| Direct hyperlink to the application page.


## 4. Getting Started & Installation

### Prerequisites

- Python 3.x Installed
- requests library installed

### Installation & Execution

1. Clone the repository:
```
Bash

git clone git@github.com:your_username/job-tracker.git
cd job-tracker
```
2. Install dependencies:
```
Bash
pip install requests
```

3. Run the pipeline:
```
Bash

python data_pipeline.py
```
*(Note: Running this will automatically generate a local job_tracker.db file in your root folder).*


## 5. Implementation Details (The Code Lifecycle)

The Python pipeline is divided into three isolated, single-responsibility functions to ensure clean modularity:
- **Extraction** (```extract_data```): Uses the ```requests``` library to fetch JSON payloads. Network operations are wrapped in a ```try-except``` block to capture errors (like HTTP failure codes or server downtime) without crashing the pipeline.
- **Transformation** (```transform_data```): Utilizes Python’s ```.strip()``` method to remove accidental leading or trailing whitespaces from strings, and safely replaces empty salary strings (```""```) with a standard ```"Not Specified"``` fallback string.
- **Loading** (```load_data```): Opens a connection to ```job_tracker.db```. Data is mapped to the schema using SQL placeholders (```?```) to prevent SQL injection or formatting bugs. It calls ```connection.commit()``` to execute a clean database transaction.


## 6. Personal Reflection & Growth

Key Takeaway: Building this project highlighted the importance of transaction atomicity (.commit()) and why data cleaning is the most critical step in any data engineering lifecycle.