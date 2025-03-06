import pandas as pd
import hashlib


# Generate a hash for the job description
def generate_description_hash(description):
    if description is None:
        description = ""
    # Normalize the description (remove extra spaces, convert to lowercase, etc.)
    normalized_description = " ".join(description.lower().strip().split())
    # generate an MD5 hash for the normalized description to remove duplicates
    return hashlib.md5(normalized_description.encode("utf-8")).hexdigest()


# Clean the job postings
def clean_jobs(jobs_list):
    jobs_df = pd.DataFrame(jobs_list)

    # Drop rows with None job descriptions
    jobs_df = jobs_df.dropna(subset=["job_description"])

    # Normalize the fields (same case and remove leading/trailing whitespaces)
    jobs_df["job_title"] = jobs_df["job_title"].astype(str).str.lower().str.strip()
    jobs_df["company"] = jobs_df["company"].astype(str).str.lower().str.strip()
    jobs_df["location"] = jobs_df["location"].astype(str).str.lower().str.strip()

    # Generate a hash for the job description
    jobs_df["description_hash"] = jobs_df["job_description"].apply(
        generate_description_hash
    )

    # Drop duplicates based on the description hash
    jobs_df = jobs_df.drop_duplicates(subset=["description_hash"])

    return jobs_df


# Save the df to a CSV file
def save_to_csv(df, filename="job_postings.csv"):
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Job postings have been saved to {filename}")
