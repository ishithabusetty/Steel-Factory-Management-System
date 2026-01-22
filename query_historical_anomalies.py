"""
Query Historical Anomalies from MongoDB
Shows all anomalies from last 6 months with trend analysis
"""
from pymongo import MongoClient
from datetime import datetime, timedelta
from collections import defaultdict

# Connect
client = MongoClient('mongodb://localhost:27017')
db = client['steel_factory_nosql']

# Calculate date 6 months ago
six_months_ago = datetime.now() - timedelta(days=180)

print("=" * 80)
print(f"Anomalies from Last 6 Months (since {six_months_ago.strftime('%Y-%m-%d')})")
print("=" * 80)

# Query anomalies from last 6 months
query = {
    "timestamp": {"$gte": six_months_ago},
    "is_anomaly": True
}

anomalies = list(db.anomaly_logs.find(query).sort("timestamp", -1))

print(f"\nTotal Anomalies Found: {len(anomalies)}\n")

if anomalies:
    # Show all anomalies
    print("All Anomalies:")
    print("-" * 80)
    for i, anom in enumerate(anomalies, 1):
        print(f"{i}. {anom['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - "
              f"{anom['machine_name']} (ID: {anom['machine_id']}) - "
              f"Score: {anom['anomaly_score']:.4f} - "
              f"Level: {anom['log_level']}")
    
    # Trend analysis
    print("\n" + "=" * 80)
    print("Trend Analysis by Machine")
    print("=" * 80)
    
    machine_counts = defaultdict(list)
    for anom in anomalies:
        machine_counts[anom['machine_name']].append(anom['anomaly_score'])
    
    for machine, scores in sorted(machine_counts.items(), key=lambda x: len(x[1]), reverse=True):
        avg_score = sum(scores) / len(scores)
        print(f"{machine:20} - Anomalies: {len(scores):3} | Avg Score: {avg_score:+.4f}")
    
    # Timeline analysis
    print("\n" + "=" * 80)
    print("Monthly Distribution")
    print("=" * 80)
    
    monthly = defaultdict(int)
    for anom in anomalies:
        month_key = anom['timestamp'].strftime('%Y-%m')
        monthly[month_key] += 1
    
    for month in sorted(monthly.keys()):
        count = monthly[month]
        bar = "█" * count
        print(f"{month}: {bar} ({count})")
    
else:
    print("No anomalies found in the last 6 months.")

print("\n" + "=" * 80)
print("Query Completed")
print("=" * 80)
