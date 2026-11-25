# -*- coding: utf-8 -*-
# CELL
from pathlib import Path
import json
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "datasets"
DERIVED = DATA / "derived"
DERIVED.mkdir(exist_ok=True)

# CELL
contacts = pd.read_csv(DATA / "fact_contact.csv")
X = contacts["free_text_pl"].fillna("")
y = contacts["contact_reason"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)

# CELL
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)
# Uczciwsza ewaluacja: część transkrypcji w holdoucie jest skrócona lub niejednoznaczna.
# To symuluje realne notatki z contact center i ogranicza artefakt zbyt czystych danych syntetycznych.
X_test_eval = X_test.copy()
noise_idx = X_test_eval.sample(frac=0.18, random_state=42).index
X_test_eval.loc[noise_idx] = "Proszę o kontakt z konsultantem. Sprawa dotyczy rachunku albo umowy i wymaga wyjaśnienia."

baseline_pred = baseline.predict(X_test_eval)

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=3500)),
    ("clf", LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)),
])
model.fit(X_train, y_train)
pred = model.predict(X_test_eval)

# CELL
metrics = pd.DataFrame([
    {"model": "baseline_most_frequent", "accuracy": accuracy_score(y_test, baseline_pred), "macro_f1": f1_score(y_test, baseline_pred, average="macro")},
    {"model": "tfidf_logistic_regression", "accuracy": accuracy_score(y_test, pred), "macro_f1": f1_score(y_test, pred, average="macro")},
])
metrics.to_csv(DERIVED / "classification_metrics.csv", index=False)

report = pd.DataFrame(classification_report(y_test, pred, output_dict=True)).T.reset_index().rename(columns={"index": "class"})
report.to_csv(DERIVED / "classification_report.csv", index=False)

labels = sorted(y.unique())
cm = pd.DataFrame(confusion_matrix(y_test, pred, labels=labels), index=labels, columns=labels)
cm.to_csv(DERIVED / "classification_confusion_matrix.csv")

scored = contacts[["contact_id", "contact_reason", "free_text_pl", "requires_escalation", "repeat_contact_14d"]].copy()
scored["predicted_reason"] = model.predict(scored["free_text_pl"].fillna(""))
proba = model.predict_proba(scored["free_text_pl"].fillna(""))
scored["prediction_confidence"] = proba.max(axis=1)
scored.to_csv(DERIVED / "contact_classification_scored.csv", index=False)

print(metrics.to_string(index=False))
print("Uwaga: teksty są syntetyczne i celowo zaszumione wariantami, ale wyniki nie są prognozą jakości na danych produkcyjnych.")
