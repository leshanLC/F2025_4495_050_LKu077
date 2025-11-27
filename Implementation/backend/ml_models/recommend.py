import os
import pandas as pd
import re
from database.database import PathfinderDatabase

db = PathfinderDatabase()
db.connect()

jobs_df = db.fetch_jobs()
courses_df = db.fetch_courses()


def extract_skills(text):
    if pd.isna(text):
        return set()

    # split by comma
    skills = [s.strip().lower() for s in text.split(",")]
    return set(skills)

# Preprocess course skills
courses_df["skills_set"] = courses_df["skills"].apply(extract_skills)

# --- Build a global dictionary of all known skills (from courses) ---
all_course_skills = set().union(*courses_df["skills_set"])


def extract_job_skills_from_text(text):
    if pd.isna(text):
        return set()

    text = text.lower()

    found = set()
    for skill in all_course_skills:
        # fuzzy match → word boundaries
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text):
            found.add(skill)
    return found

def safe_int(value):
    try:
        if value is None:
            return 0
        value = str(value).replace(",", "").strip()
        if value == "" or value.lower() == "nan":
            return 0
        return int(float(value))   # float() can parse "3.0", "3", "3000", but NOT "nan"
    except:
        return 0


def recommend_courses_for_job(job_title, user_skills):
    user_skills = {s.lower() for s in user_skills}

    # Find job row
    job_row = jobs_df[jobs_df["job_title"].str.contains(job_title, case=False, na=False)]
    if job_row.empty:
        return {"error": "Job not found"}

    job_row = job_row.iloc[0]

    # Extract job-required skills
    job_text = job_row["description"]
    job_required_skills = extract_job_skills_from_text(job_text)

    # Compute missing skills
    missing_skills = job_required_skills - user_skills

    if not missing_skills:
        return {"message": "User already has all job-required skills!"}

    # Score each course
    course_recommendations = []

    for _, row in courses_df.iterrows():
        course_skills = row["skills_set"]

        matched = missing_skills.intersection(course_skills)
        if matched:
            match_score = len(matched) / len(missing_skills)

            course_recommendations.append({
                "course_title": row["course_title"],
                "organization": row["organization"],
                "url": row["url"],
                "rating": row["rating"],
                "coverage_score": match_score
            })

    # Rank courses: highest coverage → highest rating → highest enrollments
    ranked = sorted(
                    course_recommendations,
                    key=lambda x: (
                        x["coverage_score"],
                        x["rating"]
                    ),
                    reverse=True
                )

    return {
        "job_title": job_title,
        "missing_skills": list(missing_skills),
        "recommended_courses": ranked[:5]
    }