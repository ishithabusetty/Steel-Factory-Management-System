import pandas as pd
from sklearn.ensemble import IsolationForest

# 1. Load dataset (make sure the CSV is in the same folder)
df = pd.read_csv("synthetic_performance_1000.csv")

print("Dataset loaded:", df.shape)
print(df.head())

# 2. Features for anomaly detection
# Using OEE, Downtime, ActualOutput
X = df[["OEE", "Downtime", "ActualOutput"]]

# 3. Train Isolation Forest
model = IsolationForest(
    contamination=0.10,   # ~10% anomalies expected (100 out of 1000)
    random_state=42
)

preds = model.fit_predict(X)          # -1 = anomaly, 1 = normal
scores = model.decision_function(X)   # lower score => more abnormal

# 4. Attach predictions back to dataframe
df["PredictedAnomaly"] = [1 if p == -1 else 0 for p in preds]
df["Score"] = scores

# 5. Filter detected anomalies
anoms = df[df["PredictedAnomaly"] == 1]

print("\n===== DETECTED ANOMALIES (sample) =====")
print(anoms.head())

# 6. Save anomalies to a separate CSV
anoms.to_csv("detected_anomalies_1000.csv", index=False)
print("\nSaved detected anomalies to detected_anomalies_1000.csv")
