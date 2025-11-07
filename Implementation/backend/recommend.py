import os
import pandas as pd
import re

# Base directory for app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(BASE_DIR, "data")

# File paths
job_skills_path = os.path.join(data_dir, "job_skills.csv")
course_path = os.path.join(data_dir, "course.csv")

# Load data
job_skills = pd.read_csv(job_skills_path)
courses = pd.read_csv(course_path) if os.path.exists(course_path) else pd.DataFrame()

# Normalize column names
job_skills.columns = job_skills.columns.str.strip().str.lower()
if not courses.empty:
    courses.columns = courses.columns.str.strip().str.lower()

def extract_skills(text):
    """
    Extract likely skill phrases from qualification text
    """
    if pd.isna(text):
        return []
    text = text.lower()
    # Split by comma, semicolon, newline, or 'and'
    parts = re.split(r'[,\n;/]| and ', text)
    return [p.strip() for p in parts if len(p.strip()) > 2]

def find_relevant_courses(missing_skills):
    """
    Match missing skills with course dataset
    """
    if courses.empty or "skills" not in courses.columns:
        return [f"Online course to improve {s} skills" for s in missing_skills[:5]]

    course_suggestions = []
    for skill in missing_skills[:5]:
        matched = courses[courses["skills"].str.contains(skill, case=False, na=False)]
        if not matched.empty:
            for _, row in matched.head(1).iterrows():
                course_suggestions.append(
                    f"{row.get('course name', 'Course')} — covers {skill.title()}"
                )
        else:
            course_suggestions.append(f"Online course to improve {skill} skills")
    return course_suggestions

def recommend_courses(job_category, user_skills):
    """
    Recommend missing skills and related courses for a job category
    """
    if "category" not in job_skills.columns:
        return {
            "missing_skills": [],
            "course_suggestions": ["Job skills file missing 'Category' column"]
        }

    # Filter job category
    job_req = job_skills[job_skills["category"].str.lower() == job_category.lower()]

    if job_req.empty:
        return {
            "missing_skills": [],
            "course_suggestions": ["No matching job category found"]
        }

    # Combine qualification columns
    job_req["combined_skills"] = (
        job_req.get("minimum qualifications", "").fillna('') + " " +
        job_req.get("preferred qualifications", "").fillna('')
    )

    # Extract skill words/phrases
    all_skills = []
    for txt in job_req["combined_skills"]:
        all_skills.extend(extract_skills(txt))

    required_skills = sorted(set([s for s in all_skills if len(s) > 2]))

    # Normalize user skills
    user_skills = [s.lower() for s in user_skills]

    # Find missing ones
    missing_skills = [s for s in required_skills if not any(s in u for u in user_skills)]

    # Recommend matching courses
    course_suggestions = find_relevant_courses(missing_skills)

    return {
        "missing_skills": missing_skills,
        "course_suggestions": course_suggestions or ["No missing skills detected! 🎉"]
    }
