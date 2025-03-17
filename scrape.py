import os
import random
import time
import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from serpapi import GoogleSearch

# load the dot env and get the serp api key
load_dotenv()
API_KEY = os.getenv("SERP_API_KEY")


def create_session(proxies=None, ca_cert=None):
    session = requests.Session()
    if proxies:
        session.proxies.update(proxies)
    if ca_cert:
        session.verify = ca_cert
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def parse_posting_time(posted_time):
    if not posted_time:
        return None
    try:
        current_time = datetime.datetime.utcnow()
        hours_ago = int(posted_time.split()[0])
        posted_datetime = current_time - datetime.timedelta(hours=hours_ago)
        return posted_datetime.strftime("%H:%M:%S")
    except:
        return None


def get_job_description(session, job_url):
    try:
        response = session.get(job_url, timeout=10)
        if response.status_code != 200:
            return None
    except Exception:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    desc_tag = soup.find("div", class_="show-more-less-html__markup")
    return desc_tag.text.strip() if desc_tag else None


def extract_job_info(job_card):
    href_tag = job_card.find("a", class_="base-card__full-link")
    job_url = (
        href_tag.attrs["href"].split("?")[0]
        if href_tag and "href" in href_tag.attrs
        else None
    )
    title_tag = job_card.find("h3", class_="base-search-card__title")
    job_title = title_tag.text.strip() if title_tag else None
    company_tag = job_card.find("h4", class_="base-search-card__subtitle")
    company_name = company_tag.text.strip() if company_tag else None
    location_tag = job_card.find("span", class_="job-search-card__location")
    job_location = location_tag.text.strip() if location_tag else None
    time_tag = job_card.find("time", class_="job-search-card__listdate")
    job_posting_time = parse_posting_time(time_tag.text.strip()) if time_tag else None
    apply_tag = job_card.find("a", class_="apply-button")
    ats_link = apply_tag["href"] if apply_tag else None
    return {
        "job_title": job_title,
        "company": company_name,
        "location": job_location,
        "job_url": ats_link if ats_link else job_url,
        "job_posting_time": job_posting_time,
    }


def fetch_job_details(job_cards, seen_ids, results_wanted, session):
    job_list = []
    for job_card in job_cards:
        job_info = extract_job_info(job_card)
        if not job_info.get("job_posting_time"):
            continue
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


def fetch_linkedin_jobs(
    position, location, results_wanted, is_remote=False, job_type=None, easy_apply=False
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
                    f"Failed to fetch LinkedIn jobs, Status code: {response.status_code}"
                )
                return None
        except Exception as e:
            print(f"Exception occurred while fetching LinkedIn jobs: {e}")
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
    return job_list if job_list else None


def fetch_serpapi_jobs(position, location, results_wanted):
    params = {
        "engine": "google_jobs",
        "q": position,
        "location": location,
        "hl": "en",
        "api_key": API_KEY,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_results = results.get("jobs_results", [])
    jobs_data = []
    for i in jobs_results[:results_wanted]:
        posted_time = i["detected_extensions"].get("posted_at")
        formatted_time = parse_posting_time(posted_time)
        if not formatted_time:
            continue
        job_data = {
            "job_title": i["title"],
            "company": i["company_name"],
            "location": i["location"],
            "job_description": " ".join(i["description"].split("\n")),
            "job_url": (
                i.get("apply_options", [{}])[0].get("link")
                if i.get("apply_options")
                else i.get("share_link")
            ),
            "job_posting_time": formatted_time,
        }
        jobs_data.append(job_data)
    return jobs_data
