from extract.serpapi_jobs import fetch_serpapi_jobs
from extract.linkedin_jobs import fetch_linkedin_jobs
from transform.clean_jobs import clean_jobs
from load.save_to_csv import save_to_csv

def main():
    # Fetching jobs from serpapi and linkedin
    print("Fetching jobs from serpapi and linkedin")
    serpapi_jobs = fetch_serpapi_jobs()
    linkedin_jobs = fetch_linkedin_jobs()
    print("Jobs have been fetched from serpapi and linkedin")

    # Combining all jobs and cleaning them
    print("Cleaning and removing dupicate values from the jobs")
    all_jobs = serpapi_jobs + linkedin_jobs
    cleaned_jobs = clean_jobs(all_jobs)

    # Saving the cleaned jobs to a csv file
    print("Saving the cleaned jobs to a csv file")
    save_to_csv(cleaned_jobs)

if __name__ == "__main__":
    main()
