import sqlite3
import pandas as pd


class SQLiteDB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    # Create the jobs table if it doesn't exist
    def _create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT,
                company TEXT,
                location TEXT,
                job_description,
                job_url TEXT,
                job_posting_time TEXT,
                description_hash TEXT UNIQUE
            )
        """
        )
        self.conn.commit()

    # Store data in the database
    def store_data(self, df):
        # Iterate over each row in the DataFrame
        for _, row in df.iterrows():
            try:
                # Check if a job with the same description hash already exists
                self.cursor.execute(
                    """
                    SELECT id FROM jobs_data WHERE description_hash = ?
                """,
                    (row["description_hash"],),
                )
                if self.cursor.fetchone() is None:
                    # Insert the job if it doesn't exist
                    self.cursor.execute(
                        """
                        INSERT INTO jobs_data (
                            job_title, company, location, job_description, job_url, job_posting_time, description_hash
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            row["job_title"],
                            row["company"],
                            row["location"],
                            row["job_description"],
                            row["job_url"],
                            row["job_posting_time"],
                            row["description_hash"],
                        ),
                    )
                    self.conn.commit()
                    print(f"Inserted job: {row['job_title']} at {row['company']}")
                else:
                    print(
                        f"Duplicate job skipped: {row['job_title']} at {row['company']}"
                    )
            except Exception as e:
                print(f"Error inserting job: {e}")

    # Close the connection
    def close_conn(self):
        self.conn.close()

    def execute_query(self, query): ...
