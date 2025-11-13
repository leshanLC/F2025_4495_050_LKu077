import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import RandomOverSampler
import joblib

def train_model():
    # Load datasets
    #job_postings = pd.read_csv("data/job_postings.csv")
    job_skills = pd.read_csv("data/job_skills.csv")

    # Merge datasets
    df = job_skills.copy()

    # Combine textual features
    df["combined_features"] = (
        df["Minimum Qualifications"].fillna('') + " " +
        df["Preferred Qualifications"].fillna('')
    )

    # Text features and labels
    X_text = df["combined_features"]
    y = df["Category"]

    # TF-IDF vectorization
    tfidf = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 200),
        stop_words='english'
    )
    X_vec = tfidf.fit_transform(X_text)

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y_enc, test_size=0.2, random_state=42)

    # Data imbalance handling — Oversampling
    ros = RandomOverSampler(random_state=42)
    X_train_res, y_train_res = ros.fit_resample(X_train, y_train)

    print(f"\nBefore Oversampling: {len(y_train)} samples")
    print(f"After Oversampling: {len(y_train_res)} samples")

    # Train model with balanced class weights
    model = LogisticRegression(max_iter=5000, class_weight='balanced')
    model.fit(X_train_res, y_train_res)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel training complete! Test Accuracy: {acc*100:.2f}%")
    print("\nClassification Report:\n",
      classification_report(y_test, y_pred,
                            labels=np.arange(len(le.classes_)),
                            target_names=le.classes_,
                            zero_division=0))


    # Save model, TF-IDF, and encoder
    joblib.dump(model, "saved_model.pkl")
    joblib.dump(tfidf, "tfidf.pkl")
    joblib.dump(le, "label_encoder.pkl")
    print("\n💾 Model, TF-IDF, and LabelEncoder saved successfully!")

if __name__ == "__main__":
    train_model()
