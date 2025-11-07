import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

def train_model():
    job_postings = pd.read_csv("app/data/job_postings.csv")
    job_skills = pd.read_csv("app/data/job_skills.csv")

    df = pd.merge(job_postings, job_skills, left_on="job_title", right_on="Title", how="inner")

    df["combined_features"] = (
        df["company"].fillna('') + " " +
        df["job_location"].fillna('') + " " +
        df["Responsibilities"].fillna('') + " " +
        df["Minimum Qualifications"].fillna('') + " " +
        df["Preferred Qualifications"].fillna('')
    )

    print(df["job_title"].value_counts())


    X_text = df["combined_features"]
    y = df["job_title"]

    tfidf = TfidfVectorizer(
        max_features=5000,      # increase from 500 → 5000
        ngram_range=(1,2),
        stop_words='english'
    )

    X_vec = tfidf.fit_transform(X_text)

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X_vec, y_enc, test_size=0.2, random_state=42)

    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(max_iter=5000, class_weight='balanced')

    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Model training complete! Test Accuracy: {acc*100:.2f}%")

    from sklearn.metrics import classification_report
    print(classification_report(y_test, model.predict(X_test)))


    joblib.dump(model, "app/saved_model.pkl")
    joblib.dump(tfidf, "app/tfidf.pkl")
    joblib.dump(le, "app/label_encoder.pkl")

if __name__ == "__main__":
    train_model()
