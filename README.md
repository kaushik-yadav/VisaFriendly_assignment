# Visa Friendly Job Scraper

## 📌 Overview
This project scrapes job postings from LinkedIn and SerpAPI, storing visa-friendly job listings in an SQLite database. It helps users find jobs that support visa sponsorship.

## Tech Stack
- **Python** (Scraping & Data Processing)
- **Selenium** (Web Scraping)
- **BeautifulSoup** (HTML Parsing)
- **Pandas** (Data Handling)
- **SQLite** (Database Storage)
- **SerpAPI** (Google Job Search API)
- **CSV Storage** (Job listings are saved as CSV files)

## Features
- Fetches job postings from **LinkedIn** & **SerpAPI**
- Stores job data in **SQLite database** and exports results in **CSV format**
- Removes **duplicate job listings** based on job URLs
- **Error handling** for missing fields & database integrity
- Structured as a **modular Python application**

## Setup Instructions
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/VisaFriendly_assignment.git
cd VisaFriendly_assignment
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate  # On Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Get your SerpAPI key from [here](https://serpapi.com/).<br>
Create a `.env` file in the project directory and add your **SerpAPI key**:
```bash
SERPAPI_KEY=your_api_key_here
```

### 5️⃣ Run the Scraper
```bash
python main.py
```

## Approach
1. **Data Scraping**: Extracts job details from LinkedIn & Google Jobs.
2. **Data Cleaning**: Removes duplicates, handles missing fields.
3. **Database Storage & CSV Output**: Saves jobs to SQLite, ensuring uniqueness using `job_url`, and exports results in CSV format.
4. **Logging & Debugging**: Identifies skipped jobs and errors.

## Known Issues & Alternative Solutions
### ❌ Why ATS Links Are Not Working for LinkedIn Jobs?
Unlike Google Jobs, LinkedIn does not always expose direct ATS links in the job listing HTML.

- **Reason**: Many LinkedIn job postings redirect to an internal LinkedIn apply page instead of linking directly to an external ATS.
- **Issue**: The HTML structure of job postings lacks a consistent class or attribute containing the ATS link.

### 🔄 Possible Alternatives
- **Scrape the job details page** – This would require visiting each job URL and extracting an external link if available. However, LinkedIn often restricts scraping at scale.
- **LinkedIn API (Premium Only)** – The API provides richer job details, but it's restricted and requires approval.
- **Use a Browser Automation Tool (e.g., Selenium)** – This can dynamically load job pages but is slower and requires handling LinkedIn’s anti-bot measures.

For now, the script prioritizes the available job URL when the ATS link is missing. Let me know if we should explore an alternative approach!

## Scheduling
We can use two approaches for Scheduling:
1. **AWS hosted**: We can use AWS Lambda with EventBridge or an EC2 cron job to run the script, with AWS RDS for storage.
2. **locally hosted**: We can use a cron job on Linux/macOS or Task Scheduler on Windows to run the script at set intervals.

## License
This project is licensed under the MIT License.
