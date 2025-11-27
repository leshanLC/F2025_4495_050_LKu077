# app/preprocess.py
import joblib

def preprocess_input(education, gpa, interests, skills):
    tfidf = joblib.load("tfidf.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    text_input = f"{education} {' '.join(interests)} {' '.join(skills)}"
    X_vec = tfidf.transform([text_input])
    return X_vec
