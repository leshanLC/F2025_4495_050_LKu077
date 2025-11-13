# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pydantic import BaseModel
import joblib
from typing import Dict
from preprocess import preprocess_input
from recommend import recommend_courses
from fastapi.middleware.cors import CORSMiddleware

from personality_model import (
    predict_cluster_from_ocean,
    compute_ocean_from_items,
    cluster_names,
    cluster_desc_en,
)

app = FastAPI(title="Career Path Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] for security
    allow_credentials=True,
    allow_methods=["*"],  # <== allows OPTIONS, GET, POST, etc.
    allow_headers=["*"],
)

model = joblib.load("saved_model.pkl")
tfidf = joblib.load("tfidf.pkl")
label_encoder = joblib.load("label_encoder.pkl")

class UserProfile(BaseModel):
    education: str
    gpa: float
    interests: list[str]
    skills: list[str]

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
    probabilities: Dict[str, float]   # Example: {"0": 0.12, "1": 0.08, ...}


# API endpoints


@app.post("/predict", response_model=PredictResponse)
def predict(input_data: OceanInput):
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
        rec = recommend_courses(category, profile.skills)
        response.append({
            "job_category": category,
            "confidence": float(probs[top_indices[list(job_categories).index(category)]]),
            "missing_skills": rec["missing_skills"],
            "recommended_courses": rec["course_suggestions"]
        })

    return {"predictions": response}
