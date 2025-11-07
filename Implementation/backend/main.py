# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from app.preprocess import preprocess_input
from app.recommend import recommend_courses

app = FastAPI(title="Career Path Prediction API")

model = joblib.load("app/saved_model.pkl")
tfidf = joblib.load("app/tfidf.pkl")
label_encoder = joblib.load("app/label_encoder.pkl")

class UserProfile(BaseModel):
    education: str
    gpa: float
    interests: list[str]
    skills: list[str]

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
        rec = recommend_courses(category, profile.skills)
        response.append({
            "job_category": category,
            "confidence": float(probs[top_indices[list(job_categories).index(category)]]),
            "missing_skills": rec["missing_skills"],
            "recommended_courses": rec["course_suggestions"]
        })

    return {"predictions": response}
