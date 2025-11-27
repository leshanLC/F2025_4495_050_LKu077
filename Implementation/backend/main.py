# main.py
import schedule
import time
import threading
from database.database import PathfinderDatabase
from scraper.indeed_scraper import IndeedScraper
from scraper.coursera_scraper import CourseraScraper
from itertools import cycle
from ml_models.job_model import train_model
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
from ml_models.preprocess import preprocess_input
from ml_models.personality_model import *
from ml_models.recommend import recommend_courses_for_job
from fastapi.middleware.cors import CORSMiddleware

COMMON_JOB_TITLES = [ 
    # Technology & IT 
    "Software Engineer", "Data Scientist", "Frontend Developer", "Backend Developer", "Full Stack Developer", "DevOps Engineer", "Mobile App Developer", "Web Developer", "Cloud Engineer", "Machine Learning Engineer", "IT Support Specialist", "Network Administrator", "Database Administrator", "Cybersecurity Analyst", "Systems Analyst", "Data Analyst", "Business Intelligence Analyst", "UI UX Designer", "Game Developer", "Product Manager", 
    
    # Business, Management & Finance 
    "Project Manager", "Business Analyst", "Operations Manager", "Account Manager", "Financial Analyst", "Accountant", "Bookkeeper", "Auditor", "Payroll Specialist", "Risk Analyst", "Investment Analyst", "Budget Analyst", "Compliance Officer", "Business Development Manager", "Procurement Specialist", "Office Administrator", "Administrative Assistant", "Executive Assistant", "Human Resources Manager", "Recruiter", 
    
    # Healthcare & Medical 
    "Registered Nurse", "Licensed Practical Nurse", "Medical Assistant", "Pharmacy Technician", "Dental Assistant", "Dental Hygienist", "Physiotherapist", "Occupational Therapist", "Pharmacist", "Medical Receptionist", "Healthcare Administrator", "Medical Laboratory Technician", "Caregiver", "Personal Support Worker", "Medical Office Assistant", "Home Health Aide", "Dietitian", "Mental Health Counselor", "Psychologist", "Medical Billing Specialist", 
    
    # Skilled Trades & Construction 
    "Electrician", "Plumber", "Carpenter", "Welder", "HVAC Technician", "Construction Laborer", "Construction Manager", "Painter", "Mechanic", "Maintenance Technician", "Millwright", "Heavy Equipment Operator", "Roofer", "Sheet Metal Worker", "General Labourer", "Assembler", "Fabricator", "Forklift Operator", "Quality Inspector", "Machinist", 
    
    # Logistics, Retail & Customer Service 
    "Truck Driver", "Delivery Driver", "Warehouse Associate", "Inventory Clerk", "Forklift Driver", "Logistics Coordinator", "Dispatcher", "Supply Chain Analyst", "Customer Service Representative", "Sales Associate", "Store Manager", "Retail Supervisor", "Merchandiser", "Cashier", "Order Picker", "Package Handler", "Shipping Coordinator", "Stock Clerk", "E-commerce Specialist", "Call Center Agent", 
    
    # Education & Training 
    "Teacher", "Teaching Assistant", "Substitute Teacher", "Professor", "Tutor", "Academic Advisor", "School Administrator", "Education Coordinator", "Instructional Designer", "Librarian", 
    
    # Hospitality, Tourism & Services 
    "Chef", "Cook", "Server", "Bartender", "Barista", "Dishwasher", "Hotel Front Desk Agent", "Housekeeper", "Event Coordinator", "Travel Consultant", "Flight Attendant", "Tour Guide", "Concierge", "Host Hostess", 
    
    # Creative, Media & Marketing 
    "Marketing Specialist", "Digital Marketing Manager", "Content Writer", "Copywriter", "Graphic Designer", "Video Editor", "Photographer", "Social Media Manager", "Public Relations Specialist", "Brand Manager" ]

job_cycle = cycle(COMMON_JOB_TITLES)

# Main hourly scraping job
def run_hourly_scraper():
    db = PathfinderDatabase("pathfinder_db.sqlite")
    db.connect()

    scraper = IndeedScraper(headless=True)

    job_title = next(job_cycle)
    print(f"Running scraper for: {job_title}")

    jobs = scraper.scrape_jobs(job_title=job_title, location="Canada")

    if jobs:
        added = db.save_jobs(jobs)
        print(f"Added {added} new jobs to database.")
    else:
        print("No jobs scraped.")

    scraper.driver.quit()

    course_scraper = CourseraScraper(headless=True)

    courses = course_scraper.scrape_courses(query=job_title)

    if courses:
        added = db.save_courses(courses)
        print(f"Added {added} new courses to database.")
    else:
        print("No courses scraped.")

    course_scraper.driver.quit()

model = None
tfidf = None
label_encoder = None

def run_monthly_training():
    global model, tfidf, label_encoder
    print("Starting monthly model training...")
    train_model()
    print("model training completed successfully.")
    model = joblib.load("./ml_models/saved_model.pkl")
    tfidf = joblib.load("./ml_models/tfidf.pkl")
    label_encoder = joblib.load("./ml_models/label_encoder.pkl")


def start_scheduler():
    import schedule
    # schedule jobs

    print("scheduler started")
    schedule.every(1).hours.do(run_hourly_scraper)
    schedule.every(30).days.do(run_monthly_training)

    # optionally, run once immediately
    run_hourly_scraper()
    run_monthly_training()

    while True:
        schedule.run_pending()
        time.sleep(10)


app = FastAPI(title="Career Path Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

class UserProfile(BaseModel):
    education: str
    gpa: float
    interests: list[str]
    skills: list[str]

# pydantic schemas(personality)
class OceanInput(BaseModel):
    """
    Request body schema for when the frontend already sends
    O, C, E, A, N average scores.
    """
    O: float = Field(..., ge=1.0, le=5.0, description="Openness (1–5)")
    C: float = Field(..., ge=1.0, le=5.0, description="Conscientiousness (1–5)")
    E: float = Field(..., ge=1.0, le=5.0, description="Extraversion (1–5)")
    A: float = Field(..., ge=1.0, le=5.0, description="Agreeableness (1–5)")
    N: float = Field(..., ge=1.0, le=5.0, description="Neuroticism (1–5)")


class ItemAnswers(BaseModel):
    """
    Request body schema for when the frontend sends all 50 IPIP item scores directly.

    Expected keys in `answers`:
      'EXT1'..'EXT10',
      'EST1'..'EST10',
      'AGR1'..'AGR10',
      'CSN1'..'CSN10',
      'OPN1'..'OPN10'
    """
    answers: Dict[str, float]


class PredictResponse(BaseModel):
    """
    Response schema for personality cluster prediction.
    Contains:
      - cluster_id: numeric ID (0–4)
      - cluster_name: human-readable label
      - description_en: English description of the cluster
      - probabilities: class probabilities for all clusters
    """
    cluster_id: int
    cluster_name: str
    description_en: str
    probabilities: Dict[str, float]  


@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_scheduler, daemon=True).start()


# API endpoints


@app.post("/personality", response_model=PredictResponse)
def personality(input_data: OceanInput):
    """
    Endpoint 1: Predict from OCEAN scores.

    Use this when the frontend already computes O, C, E, A, N.

    Example request body:
    {
      "O": 3.6,
      "C": 3.2,
      "E": 2.9,
      "A": 3.8,
      "N": 3.1
    }
    """
    try:
        pred, proba = predict_cluster_from_ocean(
            input_data.O,
            input_data.C,
            input_data.E,
            input_data.A,
            input_data.N,
        )
    except ValueError as ve:
        # Validation error on input values (400 Bad Request)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Any unexpected error during prediction (500 Internal Server Error)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    # Convert probability vector to JSON-serializable dict
    prob_dict = {str(i): float(p) for i, p in enumerate(proba)}

    return PredictResponse(
        cluster_id=pred,
        cluster_name=cluster_names.get(pred, f"Cluster {pred}"),
        description_en=cluster_desc_en.get(pred, f"Cluster {pred}"),
        probabilities=prob_dict,
    )

@app.post("/predict")
def predict_jobs(profile: UserProfile):
    X_vec = preprocess_input(profile.education, profile.gpa, profile.interests, profile.skills)
    probs = model.predict_proba(X_vec)[0]

    print("Raw prediction probabilities:", probs)
    print("Top confidence score:", max(probs))

    top_indices = probs.argsort()[-5:][::-1]
    job_categories = label_encoder.inverse_transform(top_indices)

    response = []
    for category in job_categories:
        rec = recommend_courses_for_job(category, profile.skills)
        response.append({
            "job_category": category,
            "confidence": float(probs[top_indices[list(job_categories).index(category)]]),
            "missing_skills": rec.get("missing_skills", []),  # default to empty list
            "recommended_courses": rec.get("recommended_courses", [])
        })

    return {"predictions": response}
