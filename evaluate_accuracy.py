import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# 1. Load dataset
df = pd.read_csv("synthetic_performance_1000.csv")

print("Dataset loaded:", df.shape)

# True labels (from dataset)
y_true = df["TrueAnomaly"]  # 0 = normal, 1 = anomaly

# Features for ML
X = df[["OEE", "Downtime", "ActualOutput"]]

# 2. Train Isolation Forest
model = IsolationForest(
    contamination=0.10,   # ~10% anomalies (100 / 1000)
    random_state=42
)

preds = model.fit_predict(X)  # -1 = anomaly, 1 = normal

# Convert to 0/1 for comparison
y_pred = [1 if p == -1 else 0 for p in preds]

# 3. Compute metrics
acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, zero_division=0)
rec = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)
cm = confusion_matrix(y_true, y_pred)

print("\n=========== EVALUATION RESULTS ===========")
print("Accuracy : ", round(acc, 3))
print("Precision:", round(prec, 3))
print("Recall   :", round(rec, 3))
print("F1 Score :", round(f1, 3))

print("\nConfusion Matrix [ [TN FP] [FN TP] ] :")
print(cm)

# 4. Save full results with prediction
df["PredictedAnomaly"] = y_pred
df.to_csv("synthetic_performance_1000_with_preds.csv", index=False)
print("\nSaved predictions to synthetic_performance_1000_with_preds.csv")
