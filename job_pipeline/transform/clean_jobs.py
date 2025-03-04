import pandas as pd

def clean_jobs(jobs_list):

    jobs_df = pd.DataFrame(jobs_list)

    # Normalize the fields(same case and remove leading/trailing whitespaces)
    jobs_df["job_title"] = jobs_df["job_title"].str.lower().str.strip()
    jobs_df["company"] = jobs_df["company"].str.lower().str.strip()
    jobs_df["location"] = jobs_df["location"].str.lower().str.strip()

    # Creatting a unique hash for each job posting
    # This job hash will be further used to identify duplicates
    jobs_df["job_hash"] = jobs_df["job_title"] + "_" + jobs_df["company"] + "_" + jobs_df["location"]

    # Dropping the duplicates
    jobs_df = jobs_df.drop_duplicates(subset=["job_hash"]).drop(columns=["job_hash"])

    return jobs_df
