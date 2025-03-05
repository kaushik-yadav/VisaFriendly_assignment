from scrape import fetch_serpapi_jobs, fetch_linkedin_jobs
from utils import clean_jobs, save_to_csv
from db import SQLiteDB

POSITION = "Data Engineer"
LOCATION = "worldwide"
RESULTS_WANTED = 10


def main():
    # Fetching jobs from serpapi and linkedin
    print("Fetching jobs from serpapi and linkedin")
    serpapi_jobs = fetch_serpapi_jobs(POSITION, LOCATION, RESULTS_WANTED)
    linkedin_jobs = fetch_linkedin_jobs(POSITION, LOCATION, RESULTS_WANTED)
    print("Jobs have been fetched from serpapi and linkedin")

    # Combining all jobs and cleaning them
    print("Cleaning and removing dupicate values from the jobs")
    all_jobs = serpapi_jobs + linkedin_jobs
    cleaned_jobs = clean_jobs(all_jobs)
    print("Jobs have been cleaned and duplicates have been removed")

    print("Storing the cleaned jobs to a sqlite database")
    db = SQLiteDB("job_postings.db")
    print("Storing data in db")
    db.store_data(cleaned_jobs)
    print("data stored in db")
    db.close_conn()
    print("Closed connection")
    print("Data stored successfully!")

    ## if csv is needed use this
    # Saving the cleaned jobs to a csv file
    # print("Saving the cleaned jobs to a csv file")
    # save_to_csv(cleaned_jobs)


if __name__ == "__main__":
    main()
