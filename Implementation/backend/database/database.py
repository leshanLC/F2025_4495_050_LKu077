import sqlite3
import pandas as pd
import os

class PathfinderDatabase:
    def __init__(self, db_path="pathfinder_db.sqlite"):
        self.db_path = "./database/"+db_path
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self._create_tables()
            print(f"Connected to DB: {self.db_path}")
            return True
        except Exception as e:
            print(f"DB connection error: {e}")
            return False

    def _create_tables(self):
        cursor = self.connection.cursor()

        # Jobs Table
        create_jobs_table = """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Courses Table
        create_courses_table = """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_title TEXT NOT NULL,
            organization TEXT,
            skills TEXT,
            url TEXT,
            rating REAL,
            course_students_enrolled INTEGER
        );
        """

        cursor.execute(create_jobs_table)
        cursor.execute(create_courses_table)
        self.connection.commit()
        cursor.close()
        print("Tables ready")

    # Save Jobs
    def save_jobs(self, jobs):
        if not jobs:
            print("No jobs to save.")
            return 0

        cursor = self.connection.cursor()
        insert_sql = """
            INSERT INTO jobs (job_title, company, description)
            VALUES (?, ?, ?)
        """
        saved_count = 0

        for job in jobs:
            try:
                cursor.execute(insert_sql, (
                    job.get('title'),
                    job.get('company'),
                    job.get('description')
                ))
                saved_count += 1
            except Exception as e:
                print(f"Insert error: {e}")

        self.connection.commit()
        cursor.close()
        return saved_count

    # Save Courses
    def save_courses(self, courses):
        if not courses:
            print("No courses to save.")
            return 0

        cursor = self.connection.cursor()
        insert_sql = """
            INSERT INTO courses (course_title, organization, skills, url, rating)
            VALUES (?, ?, ?, ?, ?)
        """
        saved_count = 0

        for course in courses:
            try:
                cursor.execute(insert_sql, (
                    course.get('course_title'),
                    course.get('organization'),
                    course.get('skills'),
                    course.get('url'),
                    course.get('rating')
                ))
                saved_count += 1
            except Exception as e:
                print(f"Insert error: {e}")

        self.connection.commit()
        cursor.close()
        return saved_count

    # Backup Entire DB
    def backup_to_csv(self, filename="jobs_backup.csv"):
        if not os.path.exists(self.db_path):
            print("DB not found.")
            return False

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM jobs", conn)
        df.to_csv(filename, index=False)
        conn.close()

        print(f"Backup saved: {filename}")
        return True
    
        # Fetch jobs for model training
    def fetch_jobs(self):
        cursor = self.connection.cursor()

        query = """
            SELECT 
                job_title,
                description
            FROM jobs
            WHERE description IS NOT NULL 
              AND job_title IS NOT NULL
        """

        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            print(f"Error loading jobs for training: {e}")
            return pd.DataFrame()
        
        # Fetch courses for model training or recommendation
    def fetch_courses(self):
        cursor = self.connection.cursor()

        query = """
            SELECT 
                course_title,
                organization,
                skills,
                url,
                rating,
                course_students_enrolled
            FROM courses
            WHERE course_title IS NOT NULL
        """

        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            print(f"Error loading courses for training: {e}")
            return pd.DataFrame()


