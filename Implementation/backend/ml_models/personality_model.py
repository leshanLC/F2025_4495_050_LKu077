# model.py
from typing import Dict, Tuple
import joblib
import numpy as np


# Load trained model and scaler

try:
    rf_model = joblib.load("./ml_models/rf_cluster_k5.pkl")     # RandomForest classifier
    scaler = joblib.load("./ml_models/ocean_scaler.pkl")        # StandardScaler for OCEAN inputs
except Exception as e:

    raise RuntimeError(f"Failed to load model or scaler: {e}")



# Cluster labels and descriptions

# Mapping from cluster ID to human-readable name and English description.
cluster_names = {
    0: "The Social Explorer",
    1: "The Organizer",
    2: "The Calm Analyst",
    3: "The Empathetic Mediator",
    4: "The Creative Thinker",
}

cluster_desc_en = {
    0: "a sociable, upbeat team player",
    1: "a responsible, systematic planner",
    2: "an analytical, calm thinker",
    3: "an empathetic, cooperative coordinator",
    4: "a creative, curious explorer",
}



# Core utility functions


def validate_ocean(o: float, c: float, e: float, a: float, n: float) -> None:
    """
    Validate that all OCEAN values are within the range [1, 5].
    This is an additional safety check before running predictions.
    """
    vals = [o, c, e, a, n]
    for v in vals:
        fv = float(v)
        if not (1.0 <= fv <= 5.0):
            raise ValueError("All O,C,E,A,N scores must be in [1,5].")


def predict_cluster_from_ocean(
    o: float,
    c: float,
    e: float,
    a: float,
    n: float,
) -> Tuple[int, np.ndarray]:
    """
    Predict the personality cluster from 5 OCEAN scores.

    Steps:
      1. Validate the input values.
      2. Scale them using the pre-trained StandardScaler.
      3. Use the RandomForest model to predict the cluster label.
      4. Return both the predicted label and probability vector.
    """
    validate_ocean(o, c, e, a, n)
    x = np.array([[o, c, e, a, n]], dtype="float32")
    x_scaled = scaler.transform(x)
    pred = int(rf_model.predict(x_scaled)[0])
    proba = rf_model.predict_proba(x_scaled)[0]   # Shape: (5,) for 5 clusters
    return pred, proba


def compute_ocean_from_items(answers: Dict[str, float]):
    """
    Convert 50 IPIP item responses into averaged O, C, E, A, N scores.

    Expected keys in `answers`:
      - EXT1..EXT10: Extraversion
      - EST1..EST10: Emotional Stability (inverse of Neuroticism)
      - AGR1..AGR10: Agreeableness
      - CSN1..CSN10: Conscientiousness
      - OPN1..OPN10: Openness

    Neuroticism (N) is derived as:
      N = 6 - mean(EST scores)
    """
    # Define expected item keys (must match training data)
    ext_cols = [f"EXT{i}" for i in range(1, 11)]
    est_cols = [f"EST{i}" for i in range(1, 11)]
    agr_cols = [f"AGR{i}" for i in range(1, 11)]
    csn_cols = [f"CSN{i}" for i in range(1, 11)]
    opn_cols = [f"OPN{i}" for i in range(1, 11)]

    required_cols = ext_cols + est_cols + agr_cols + csn_cols + opn_cols

    # (1) Ensure all required items are present
    missing = [c for c in required_cols if c not in answers]
    if missing:
        raise ValueError(f"Missing item(s): {missing[:3]} ... total {len(missing)}")

    # (2) Validate that each item is within the [1,5] range
    for key in required_cols:
        v = float(answers[key])
        if not (1.0 <= v <= 5.0):
            raise ValueError(f"Item {key} must be in [1,5], got {v}")

    # Helper to compute mean for each trait
    def mean(cols):
        return float(np.mean([float(answers[c]) for c in cols]))

    O = mean(opn_cols)
    C = mean(csn_cols)
    E = mean(ext_cols)
    A = mean(agr_cols)
    # Emotional Stability is reversed to derive Neuroticism
    N = 6.0 - mean(est_cols)

    validate_ocean(O, C, E, A, N)
    return O, C, E, A, N
