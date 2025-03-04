import os

from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()
API_KEY = os.getenv("SERP_API_KEY")
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