import pandas as pd

def save_to_csv(df, filename="job_postings.csv"):

    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Job postings have been saved to {filename}")