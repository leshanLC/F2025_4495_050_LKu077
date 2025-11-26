# model.py
from typing import Dict, Tuple
import joblib
import numpy as np


# Load trained model and scaler

try:
    rf_model = joblib.load("rf_cluster_k5.pkl")     # RandomForest classifier
    scaler = joblib.load("ocean_scaler.pkl")        # StandardScaler for OCEAN inputs
except Exception as e:

    raise RuntimeError(f"Failed to load model or scaler: {e}")



# Cluster labels and descriptions

# Mapping from cluster ID to human-readable name and English description.

cluster_names = {
    0: "Balanced Collaborator",
    1: "Reserved Analyzer",
    2: "Calm Problem-Solver",
    3: "Supportive Team Member",
    4: "Creative Explorer",
}

    


cluster_desc_en = {
    0: (
        "This type is a steady, balanced collaborator who stays calm under pressure and works reliably in team settings. "
        "They are emotionally stable, cooperative, and consistent, which makes group work feel predictable and smooth. "
        "Strengths: reliability, emotional stability, organization, and consideration for others. "
        "Growth areas: may hesitate to take bold risks or move away from familiar routines. "
        "Career fit: project coordination, HR support, operations, customer service, and administrative roles."
    ),
    1: (
        "This type is a reserved, detail-focused analyzer who prefers quiet, independent work and thinks carefully before acting. "
        "They are introspective and sensitive, which helps them notice risks or issues others might miss. "
        "Strengths: thoughtfulness, analytical thinking, caution, and ability to work independently. "
        "Growth areas: may overthink decisions, feel easily stressed, or find fast-paced, highly social environments overwhelming. "
        "Career fit: research, data entry, writing, quality control, and back-office roles."
    ),
    2: (
        "This type is a practical, calm problem-solver who combines creative thinking with emotional stability. "
        "They prefer structured problem-solving over highly social or chaotic environments and stay composed under pressure. "
        "Strengths: steady decision-making, creative but grounded thinking, patience, and logical reasoning. "
        "Growth areas: may communicate too little, be less assertive in groups, or keep ideas to themselves. "
        "Career fit: UX research, engineering support, IT troubleshooting, product analysis, and design support roles."
    ),
    3: (
        "This type is a warm, socially supportive team member who values harmony and positive relationships. "
        "They are friendly, cooperative, and emotionally stable, helping to maintain a calm and supportive team atmosphere. "
        "Strengths: empathy, teamwork, patience, and reliability in group settings. "
        "Growth areas: may avoid conflict, hesitate to speak up strongly, or hold back their own opinions to keep peace. "
        "Career fit: customer service, community engagement, teaching assistant roles, and team coordination."
    ),
    4: (
        "This type is a creative, emotionally intuitive explorer who enjoys flexible, dynamic environments and new ideas. "
        "They are imaginative and expressive, with strong emotional awareness that supports empathy and creativity. "
        "Strengths: originality, idea generation, expressiveness, and understanding of others' feelings. "
        "Growth areas: may feel overwhelmed under stress, struggle with consistency, or need clearer structure and routines. "
        "Career fit: marketing, design, content creation, creative strategy, and arts-related roles."
    ),
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
