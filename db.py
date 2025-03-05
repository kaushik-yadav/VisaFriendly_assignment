import sqlite3
class SQLiteDB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    # Used to store data in sqlite database from the dataframe
    def store_data(self, df, mode = "append"):
        # Store DataFrame in SQL Table
        df.to_sql("jobs_data", self.conn, if_exists=mode, index=False)
    
    # Close the connection
    def close_conn(self):
        self.conn.close()

    def execute_query(self, query):
        ...

