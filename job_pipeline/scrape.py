import os
import random
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from serpapi import GoogleSearch

# load the dot env and get the serp api key
load_dotenv()
API_KEY = os.getenv("SERP_API_KEY")

# Create a session with the given proxies and ca_cert

def create_session(proxies=None, ca_cert=None):
    session = requests.Session()
    if proxies:
        session.proxies.update(proxies)
    if ca_cert:
        session.verify = ca_cert
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session

# Fetch job description from the job page
def get_job_description(session, job_url):
    # Get job description from the job page(separate page for desc extraction)
    try:
        response = session.get(job_url, timeout=10)
        if response.status_code != 200:
            return "N/A"
    except Exception:
        return "N/A"

    soup = BeautifulSoup(response.text, "html.parser")
    desc_tag = soup.find("div", class_="show-more-less-html__markup")
    return desc_tag.text.strip() if desc_tag else "N/A"

# Used to fetch the jobs from linkedin
# For sample purpose we are fetching only 10 jobs and also using some hardcoded values
def fetch_linkedin_jobs(position = "Data Engineer", location = "worldwide", results_wanted=10, is_remote=False, job_type=None, easy_apply=False):
    base_url = "https://www.linkedin.com"
    delay = 3
    band_delay = 4
    session = create_session()
    job_list = []
    seen_ids = set()
    start = 0

    while len(job_list) < results_wanted and start < 1000:
        params = {
            "keywords": position,
            "location": location,
            "f_WT": 2 if is_remote else None,
            "f_JT": job_type,
            "start": start,
            "f_AL": "true" if easy_apply else None,
        }
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = session.get(f"{base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search?", params=params, timeout=10)
            if response.status_code != 200:
                return job_list
        except Exception:
            return job_list

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("div", class_="base-search-card")

        if not job_cards:
            return job_list

        for job_card in job_cards:
            href_tag = job_card.find("a", class_="base-card__full-link")
            if not href_tag or "href" not in href_tag.attrs:
                continue
            
            job_url = href_tag.attrs["href"].split("?")[0]
            job_id = job_url.split("-")[-1]
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)

            # Extract Job Title
            title_tag = job_card.find("h3", class_="base-search-card__title")
            job_title = title_tag.text.strip() if title_tag else None

            # Extract Company Name
            company_tag = job_card.find("h4", class_="base-search-card__subtitle")
            company_name = company_tag.text.strip() if company_tag else None

            # Extract Location
            location_tag = job_card.find("span", class_="job-search-card__location")
            job_location = location_tag.text.strip() if location_tag else None

            # Extract Job Posting Time
            time_tag = job_card.find("time", class_="job-search-card__listdate")
            job_posting_time = time_tag.text.strip() if time_tag else None

            # Fetch Job Description (requires opening the job page)
            job_description = get_job_description(session, job_url)

            job_list.append({
                "job_title": job_title,
                "company": company_name,
                "location": job_location,
                "job_description": job_description,
                "job_url": job_url,
                "job_posting_time": job_posting_time
            })

            if len(job_list) >= results_wanted:
                return job_list
        
        time.sleep(random.uniform(delay, delay + band_delay))
        start += len(job_list)

    return job_list

# Fetch job postings from serpapi
def fetch_serpapi_jobs(query = "Data Engineer", location = "India", num_jobs = 10):
    # by default serapi has 10 jobs per page, for sample purpose we will be using only 10 pages if we want more 
    # we can increase the number of pages by pagination
    params = {
      "engine": "google_jobs",
      "q": query,
      "location": location,
      "hl": "en",
      "api_key": API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_results = results.get("jobs_results",[])
    jobs_data = []
    for i in jobs_results[:num_jobs]:
        job_data = {
            "job_title":i["title"],
            "company":i["company_name"],
            "location":i["location"],
            "job_description": " ".join(i["description"].split("\n")),
            "job_url": i["share_link"],
            "job_posting_time" : i["detected_extensions"].get("posted_at")
        }
        jobs_data.append(job_data)
    return jobs_data