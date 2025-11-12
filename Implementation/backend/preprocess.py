# app/preprocess.py
import joblib

tfidf = joblib.load("tfidf.pkl")
label_encoder = joblib.load("label_encoder.pkl")

def preprocess_input(education, gpa, interests, skills):
    text_input = f"{education} {' '.join(interests)} {' '.join(skills)}"
    X_vec = tfidf.transform([text_input])
    return X_vec
