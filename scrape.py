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
            return None
    except Exception:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    desc_tag = soup.find("div", class_="show-more-less-html__markup")
    return desc_tag.text.strip() if desc_tag else None


# Extract job information from the job card
def extract_job_info(job_card):
    # Extract the job url using href tag
    href_tag = job_card.find("a", class_="base-card__full-link")
    job_url = None
    if href_tag and "href" in href_tag.attrs:
        job_url = href_tag.attrs["href"].split("?")[0]
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

    apply_tag = job_card.find("a", class_="apply-button")  # External ATS link
    ats_link = apply_tag["href"] if apply_tag else None
    return {
        "job_title": job_title,
        "company": company_name,
        "location": job_location,
        "job_url": ats_link if ats_link else job_url,
        "job_posting_time": job_posting_time,
    }


# Fetch job details by extracting job card details
def fetch_job_details(job_cards, seen_ids, results_wanted, session):
    job_list = []
    for job_card in job_cards:
        job_info = extract_job_info(job_card)
        job_url = job_info.get("job_url")
        job_id = job_url.split("/")[-1] if job_url else None

        if not job_id or job_id in seen_ids:
            continue

        seen_ids.add(job_id)

        job_info["job_description"] = get_job_description(session, job_url)
        job_list.append(job_info)

        if len(job_list) >= results_wanted:
            break
    return job_list


# Used to fetch the jobs from linkedin
# For sample purpose we are fetching only 10 jobs and also using some hardcoded values
def fetch_linkedin_jobs(
    position,
    location,
    results_wanted,
    is_remote=False,
    job_type=None,
    easy_apply=False,
):
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
            # It filters the jobs for the past 24 hours where "r86400" refers to last 24 hours( since 24 hours = 86400 seconds)
            "f_TPR": "r86400",
        }
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = session.get(
                f"{base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search?",
                params=params,
                timeout=10,
            )
            if response.status_code != 200:
                print(
                    f"Failed to fetch linkedin jobs, Status code: {response.status_code}"
                )
                return None
        except Exception as e:
            print(f"Exception occured while fetching linkedin jobs :{e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("div", class_="base-search-card")

        if not job_cards:
            print("No more jobs found")
            break

        job_detail = fetch_job_details(job_cards, seen_ids, results_wanted, session)
        if job_detail:
            job_list.extend(job_detail)
        time.sleep(random.uniform(delay, delay + band_delay))
        start += len(job_list)

    if job_list:
        return job_list
    return None


# Fetch job postings from serpapi
def fetch_serpapi_jobs(postion, location, results_wanted):
    # by default serapi has 10 jobs per page, for sample purpose we will be using only 10 pages if we want more
    # we can increase the number of pages by pagination
    params = {
        "engine": "google_jobs",
        "q": postion,
        "location": location,
        "hl": "en",
        # Retrives job from the last 24 hours
        "tbs": "qdr:d",
        "api_key": API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_results = results.get("jobs_results", [])
    jobs_data = []
    for i in jobs_results[:results_wanted]:
        job_data = {
            "job_title": i["title"],
            "company": i["company_name"],
            "location": i["location"],
            "job_description": " ".join(i["description"].split("\n")),
            # If the ATS link is available then we take it else we take the share link (google search link)
            "job_url": (
                i.get("apply_options", [{}])[0].get("link")
                if i.get("apply_options")
                else i.get("share_link")
            ),
            "job_posting_time": i["detected_extensions"].get("posted_at"),
        }
        jobs_data.append(job_data)
    return jobs_data
