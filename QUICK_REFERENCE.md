# Quick Reference: Routes & Components

## 🗺️ Complete Routing Map

```
ROOT (/)
│
├─→ Login Pages
│   ├─ GET  /login           → LoginTemplate
│   ├─ POST /login           → Authenticate → Redirect to /dashboard
│   ├─ GET  /register        → RegisterTemplate
│   └─ POST /register        → Create User → Redirect to /dashboard
│
├─→ Dashboard & Analytics (Admin Only)
│   ├─ GET  /dashboard       → MainDashboard.html
│   ├─ GET  /dashboard_data  → JSON {oee, availability, performance...}
│   └─ GET  /logout          → Clear session → /login
│
├─→ Machine Management (Admin Only)
│   ├─ GET  /machines        → List all machines
│   ├─ GET  /add_machine     → Form to add machine
│   ├─ POST /add_machine     → INSERT into MySQL → /machines
│   ├─ GET  /modify_machine/<id>  → Edit form
│   └─ POST /modify_machine/<id>  → UPDATE MySQL → /machines
│
├─→ Performance Management (Admin Only)
│   ├─ GET  /performance     → Enter performance data
│   ├─ POST /add_performance → INSERT into MySQL → /performance
│   ├─ GET  /modify_performance/<id> → Edit form
│   ├─ POST /modify_performance/<id> → UPDATE MySQL → /performance
│   └─ GET  /performance/report → Detailed performance report
│
├─→ ML & Anomalies (Admin Only)
│   ├─ GET  /anomalies       → Show ML detection results
│   ├─ POST /run_anomaly_scan → Run ML → INSERT to MySQL/MongoDB/Blockchain
│   └─ GET  /query_historical_anomalies → Historical analysis
│
├─→ Alerts (Admin Only)
│   └─ GET  /alerts          → List recent alerts from MySQL
│
├─→ Blockchain & Verification (Admin Only)
│   ├─ GET  /blockchain      → Show blockchain log
│   ├─ GET  /verify_blockchain → Check hash integrity → JSON result
│   ├─ GET  /debug_blockchain   → Debug tool
│   └─ POST /repair_blockchain  → Fix corrupted blocks
│
└─→ Audit & Logs (Admin Only)
    ├─ GET  /audit_logs      → MongoDB audit trail
    ├─ GET  /mongodb_stats   → Database statistics
    └─ GET  /blockchain      → Blockchain verification page
```

---

## 🎯 Component Connections

### **Frontend → Backend → Database**

```
Page: Dashboard (/dashboard)
├─ Template: dashboard.html
├─ Flask Route: @app.route('/dashboard')
├─ Data Source 1: MySQL (machines_health)
├─ Data Source 2: MySQL (anomalies, alerts)
├─ Return Type: HTML with embedded JavaScript
└─ AJAX Endpoint: /dashboard_data
   ├─ Called by: JavaScript in dashboard.html
   ├─ Returns: JSON {oee_values, availability, performance...}
   └─ Used for: Real-time charts (Chart.js)

Page: Machines (/machines)
├─ Template: machines.html
├─ Flask Route: @app.route('/machines')
├─ Database: MySQL
├─ Query: SELECT * FROM Machine
└─ Display: Table of machines with Edit/Delete buttons

Page: Anomalies (/anomalies)
├─ Template: anomalies.html
├─ Flask Route: @app.route('/anomalies')
├─ Database 1: MySQL (anomaly_detection table)
├─ Database 2: MongoDB (anomaly_logs collection)
├─ Database 3: Blockchain_log (blockchain verification)
├─ Display: Severity-colored list of anomalies
├─ Admin Feature: "Run Scan" button triggers /run_anomaly_scan
└─ Verification: AJAX call to /verify_blockchain

Page: Alerts (/alerts)
├─ Template: alerts.html
├─ Flask Route: @app.route('/alerts')
├─ Database: MySQL (Alerts table)
├─ Query: SELECT * FROM Alerts ORDER BY Timestamp DESC
└─ Display: Color-coded alert cards
```

---

## 💾 Database Layer Mapping

### **MySQL Tables ↔ Flask Routes**

```
Machine Table
├─ Read by: /machines, /dashboard_data
├─ Written by: /add_machine, /modify_machine
└─ Used in: Machine management, dropdowns

Performance_Data Table
├─ Read by: /performance, /dashboard_data, /run_anomaly_scan
├─ Written by: /add_performance, /modify_performance
└─ Used in: Charts, OEE calculations, ML features

Anomaly_Detection Table
├─ Read by: /anomalies
├─ Written by: /run_anomaly_scan
└─ Used in: Anomaly display, verification

Alerts Table
├─ Read by: /alerts, /dashboard_data
├─ Written by: /run_anomaly_scan (auto-generates alerts)
└─ Used in: Alert display, badges

Blockchain_Log Table
├─ Read by: /blockchain, /verify_blockchain
├─ Written by: /run_anomaly_scan (creates blocks)
└─ Used in: Tampering detection, verification

User Table
├─ Read by: /login
├─ Written by: /register
└─ Used in: Authentication
```

### **MongoDB Collections ↔ Flask Routes**

```
anomaly_logs Collection
├─ Written by: /run_anomaly_scan
├─ Read by: /mongodb_stats, /audit_logs
└─ Purpose: Historical anomaly records

audit_logs Collection
├─ Written by: Most routes (via log_audit_action function)
├─ Read by: /audit_logs, /mongodb_stats
└─ Purpose: User action tracking

scan_sessions Collection
├─ Written by: /run_anomaly_scan (session start/end)
├─ Read by: /mongodb_stats
└─ Purpose: Scan execution history
```

---

## 🔄 Request Lifecycle Examples

### **Example 1: User Adds a Machine**

```
1. Browser: GET /add_machine
   ↓
2. Flask Route Handler: def add_machine()
   ├─ Check: @admin_required (is user logged in?)
   ├─ Action: render_template('add_machine.html')
   └─ Return: HTML form
   ↓
3. Browser: User fills form (name="Furnace A1", type="Furnace")
   ↓
4. Browser: POST /add_machine
   ├─ Data: {name: "Furnace A1", type: "Furnace", ...}
   ↓
5. Flask Route Handler: def add_machine()
   ├─ Receive: request.form data
   ├─ Validate: Check if name is not empty
   ├─ Database: conn = get_db_connection()
   ├─ Execute: INSERT INTO Machine (MachineName, MachineType) VALUES (...)
   ├─ Log: log_audit_action("INSERT", "Machine", machine_id)
   ├─ Commit: conn.commit()
   ├─ Result: Machine created in MySQL
   └─ Action: redirect(url_for('view_machines'))
   ↓
6. Browser: Redirect to GET /machines
   ↓
7. Flask Route Handler: def view_machines()
   ├─ Database: cursor.execute("SELECT * FROM Machine")
   ├─ Process: Convert to list of dicts
   └─ Render: render_template('machines.html', machines=machines)
   ↓
8. Browser: Receives HTML
   ├─ Display: Table with all machines including new one
   └─ Show: Edit and Delete buttons for each
```

### **Example 2: Admin Runs Anomaly Scan**

```
1. Browser: GET /anomalies
   ↓
2. Flask: Show anomalies.html with "Run Scan" button
   ↓
3. User: Clicks "Run Scan" button
   ↓
4. Browser: POST /run_anomaly_scan
   ↓
5. Flask Route Handler: def run_anomaly_scan()
   │
   ├─ Step A: Fetch Data
   │  ├─ Query MySQL: SELECT * FROM Performance_Data
   │  └─ Result: 1000+ records
   │
   ├─ Step B: Prepare ML Features
   │  ├─ Extract: [OperatingTime, Downtime, ActualOutput, GoodUnits]
   │  └─ Create: Feature matrix X (1000 rows × 4 columns)
   │
   ├─ Step C: Run ML Model
   │  ├─ Load: IsolationForest(random_state=42)
   │  ├─ Predict: model.predict(X) → [-1, 1, 1, -1, ...]
   │  ├─ Score: model.score_samples(X) → [-0.25, 0.1, 0.05, ...]
   │  └─ Result: 50 anomalies found
   │
   ├─ Step D: Write to MySQL
   │  └─ For each anomaly:
   │     INSERT INTO Anomaly_Detection (MachineID, AnomalyScore, IsAnomaly, Timestamp)
   │
   ├─ Step E: Write to MongoDB
   │  └─ For each anomaly:
   │     db['anomaly_logs'].insert_one({machine_id, score, timestamp})
   │
   ├─ Step F: Write to Blockchain
   │  ├─ Create data string: "MachineID:1,Score:-0.25,Time:2026-02-02..."
   │  ├─ Calculate hash: SHA256(data + previous_block_hash)
   │  ├─ Insert block: INSERT INTO Blockchain_Log (Data, Hash, PrevHash)
   │  └─ Result: Tamper-proof record
   │
   ├─ Step G: Generate Alerts
   │  └─ For anomalies with high score:
   │     INSERT INTO Alerts (MachineID, AlertMessage, Severity)
   │
   └─ Step H: Log to MongoDB Audit
      └─ log_audit_action("RUN_SCAN", "Anomaly_Detection", num_anomalies)
   ↓
6. Flask: redirect(url_for('view_anomalies'))
   ↓
7. Browser: GET /anomalies
   ↓
8. Flask: 
   ├─ Query MySQL: SELECT * FROM Anomaly_Detection
   ├─ Format: Convert to list with severity colors
   └─ Render: render_template('anomalies.html', anomalies=anomalies)
   ↓
9. Browser: Shows updated anomaly list with badges
```

### **Example 3: Dashboard Real-Time Updates**

```
1. Browser: GET /dashboard
   ↓
2. Flask: Return dashboard.html with JavaScript
   ↓
3. Browser: Load page
   ├─ Load CSS from /static/style.css
   └─ Load JavaScript (inline in template)
   ↓
4. JavaScript: window.onload = function() { loadDashboard() }
   │
   ├─ Call AJAX: fetch('/dashboard_data')
   │
   ├─ Flask /dashboard_data receives request:
   │  ├─ Query MySQL: Get all machines, performance, alerts
   │  ├─ Calculate: OEE = (Availability × Performance × Quality) / 100
   │  ├─ Format: JSON {oee_values: [85, 87, 82, ...], machines: [...]}
   │  └─ Return: JSON response
   │
   ├─ JavaScript receives JSON:
   │  ├─ Update text: document.getElementById('factoryOee').innerText = data.factory_avg_oee
   │  ├─ Create chart: new Chart(ctx, {type: 'line', data: data})
   │  ├─ Update table: data.machines.forEach(m => { createElement... })
   │  └─ Update badges: document.getElementById('pulseAlerts').innerText = data.recent_alerts.length
   │
   └─ Browser: Display real-time dashboard with:
      ├─ OEE trend line chart
      ├─ Quality donut chart
      ├─ Machine health cards
      └─ Alert badges
```

---

## 🎨 Frontend Architecture

```
base.html (Layout Template)
├─ <header class="topbar">
│  ├─ Logo: "🏭 Factory Management System"
│  ├─ Navigation Menu:
│  │  ├─ Home
│  │  ├─ Machines
│  │  ├─ Performance
│  │  ├─ Blockchain
│  │  ├─ Anomalies
│  │  └─ Alerts (NEW)
│  └─ Login Button (if not logged in)
│
├─ <main class="page">
│  └─ {% block content %} ← Each page extends this
│
└─ <footer>

Specific Pages (extend base.html):
├─ dashboard.html
│  ├─ Charts (Chart.js)
│  ├─ Machine cards
│  └─ AJAX calls to /dashboard_data
│
├─ machines.html
│  ├─ Table of machines
│  └─ Edit/Delete buttons
│
├─ anomalies.html
│  ├─ Anomaly table
│  ├─ Severity badges
│  └─ Blockchain verify button
│
├─ alerts.html
│  ├─ Alert cards
│  └─ Severity colors
│
└─ Other pages...
```

---

## 🔐 Security Features

```
Authentication:
├─ POST /login → Hash password → Check against stored hash
├─ Session created → Stored in Flask memory
└─ @admin_required decorator checks session

Authorization:
├─ @admin_required checks: if session['is_admin'] != True
└─ Redirects to /login if not admin

Data Protection:
├─ Blockchain: Tamper-proof records with SHA256 hashes
├─ MongoDB: Audit log of all actions (who did what when)
└─ MySQL: Constraints, foreign keys, ACID transactions
```

---

## 🚀 To Start Understanding the Code

**Read in this order:**

1. **Architecture_Guide.md** ← You are here! Understand overall structure
2. **schema.sql** (lines 1-100) ← Understand database tables
3. **app.py** (lines 1-100) ← Configuration and imports
4. **app.py** (lines 676-750) ← /login route (simple example)
5. **app.py** (lines 1944-2000) ← /anomalies route (read example)
6. **app.py** (lines 1920-1940) ← /run_anomaly_scan (complex write)
7. **templates/base.html** ← Layout structure
8. **templates/dashboard.html** ← Advanced template with AJAX
9. **static/style.css** ← Styling system

---

## 🎯 Key Takeaways

| Concept | Explanation |
|---------|------------|
| **Route** | URL pattern + function that handles it |
| **Template** | HTML file with Python-like syntax |
| **Render** | Convert template + data → HTML |
| **Redirect** | Send user to different URL |
| **AJAX** | JavaScript makes background HTTP requests |
| **Foreign Key** | Links records between tables |
| **Hash** | Unique fingerprint of data (used in blockchain) |
| **Isolation Forest** | ML algorithm that finds anomalies |
| **Decorator** | @symbol that modifies function behavior |
| **Session** | Data stored per user (logged in or not) |

