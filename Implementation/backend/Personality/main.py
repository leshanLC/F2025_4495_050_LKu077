# main.py
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Import core logic and metadata from model.py
from model import (
    predict_cluster_from_ocean,
    compute_ocean_from_items,
    cluster_names,
    cluster_desc_en,
)


# Create FastAPI app

# Initialize the FastAPI application with metadata for documentation.
app = FastAPI(
    title="Personality Cluster API",
    description="Predict Big Five-based personality cluster from OCEAN or IPIP-50 item scores.",
    version="1.0.0",
)


# Pydantic schemas


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


@app.post("/predict_from_items", response_model=PredictResponse)
def predict_from_items(item_data: ItemAnswers):
    """
    Endpoint 2: Predict from raw IPIP-50 item answers.

    Use this when the frontend sends all 50 item scores, and the backend
    computes O, C, E, A, N internally.

    Example request body:
    {
      "answers": {
        "EXT1": 4,
        "EXT2": 2,
        ...
        "OPN10": 5
      }
    }
    """
    try:
        # Step 1: Compute OCEAN averages from 50 items
        O, C, E, A, N = compute_ocean_from_items(item_data.answers)
        # Step 2: Predict cluster based on OCEAN scores
        pred, proba = predict_cluster_from_ocean(O, C, E, A, N)
    except ValueError as ve:
        # Input validation or missing items
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Any unexpected server-side error
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    prob_dict = {str(i): float(p) for i, p in enumerate(proba)}

    return PredictResponse(
        cluster_id=pred,
        cluster_name=cluster_names.get(pred, f"Cluster {pred}"),
        description_en=cluster_desc_en.get(pred, f"Cluster {pred}"),
        probabilities=prob_dict,
    )


# 3. Run locally

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
