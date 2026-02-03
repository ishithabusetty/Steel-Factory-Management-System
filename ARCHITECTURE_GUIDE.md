# Steel Factory Management System - Complete Architecture Guide

## 🏭 What Is This Project?

A **production monitoring dashboard** for a steel factory that tracks:
- Machine health and performance metrics (OEE, downtime, quality)
- Real-time anomaly detection using ML (Isolation Forest)
- Tamper-proof audit logs using blockchain
- Multi-database system (MySQL + MongoDB + Blockchain)

---

## 📊 Overall Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         WEB BROWSER                         │
│              (Visit: http://127.0.0.1:5000)                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests/Responses
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FLASK WEB SERVER (app.py)                      │
│  • Handles all web routes (/dashboard, /machines, etc.)    │
│  • Processes form submissions                              │
│  • Manages user authentication                             │
└──┬──────────────────────┬──────────────────────┬────────────┘
   │                      │                      │
   ▼                      ▼                      ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│   MYSQL      │  │   MONGODB    │  │   BLOCKCHAIN LOG     │
│  (OLTP)      │  │  (Analytics) │  │   (Audit Trail)      │
│              │  │              │  │                      │
│ • Machines   │  │ • Anomaly    │  │ • Hash-verified      │
│ • Performance│  │   logs       │  │ • Tamper-proof       │
│ • Alerts     │  │ • Audit logs │  │                      │
│ • Users      │  │ • Sessions   │  │                      │
└──────────────┘  └──────────────┘  └──────────────────────┘
```

---

## 🔌 Technology Stack

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Frontend** | User interface | HTML, CSS, JavaScript |
| **Web Server** | Request handling | Flask (Python) |
| **Database 1** | Operational data | MySQL (Transactions) |
| **Database 2** | Historical analytics | MongoDB (NoSQL) |
| **Database 3** | Security audit log | MySQL Blockchain (SHA256 hashes) |
| **ML Engine** | Anomaly detection | scikit-learn (Isolation Forest) |

---

## 📁 Project File Structure

```
Steel-Factory-Management-System/
├── app.py                          # Main Flask application (2100+ lines)
├── schema.sql                      # Database table definitions
├── requirements.txt                # Python dependencies
├── .env                           # Configuration file (passwords, URIs)
│
├── templates/                     # HTML pages (Jinja2 templates)
│   ├── base.html                 # Navigation menu + layout
│   ├── dashboard.html            # Main dashboard
│   ├── machines.html             # Machine management
│   ├── performance.html          # Performance data entry
│   ├── anomalies.html            # ML anomaly results
│   ├── blockchain.html           # Blockchain verification
│   ├── alerts.html               # Alert list (NEW)
│   ├── audit_logs.html           # MongoDB audit trail
│   └── login.html                # Authentication
│
├── static/                        # CSS & static assets
│   ├── style.css                 # Main stylesheet
│   └── lavender-dashboard.css    # Alternative theme
│
└── debug_blockchain.py            # Utilities for blockchain debugging
    repair_blockchain.py           # Tools to repair corrupted blocks
```

---

## 🔄 How Data Flows Through the System

### **Scenario 1: Admin Adds a New Machine**

```
1. Admin clicks "Add Machine" → Goes to /add_machine (Flask Route)
2. Fills form with: Machine Name, Type, Location
3. Clicks Submit → POST request to /add_machine
4. Flask receives data:
   - Validates input
   - Connects to MySQL
   - Inserts into Machine table
   - Logs action to MongoDB audit_logs
5. Redirects to /machines
6. Dashboard shows updated machine list
```

### **Scenario 2: Admin Runs ML Anomaly Scan**

```
1. Admin clicks "Run Anomaly Scan" on /anomalies page
2. POST request to /run_anomaly_scan
3. Flask app (app.py):
   - Fetches ALL performance data from MySQL
   - Loads ML model (Isolation Forest)
   - Calculates anomaly scores for each record
   - Creates blockchain hash of anomalies
   
4. Data written to 3 places simultaneously:
   ┌─────────────────┐
   │   Write to      │
   │   MySQL         │
   │   (anomaly_     │
   │   detection)    │
   └─────────────────┘
   ┌─────────────────┐
   │   Write to      │
   │   MongoDB       │
   │   (anomaly_logs)│
   └─────────────────┘
   ┌─────────────────┐
   │   Write to      │
   │   Blockchain    │
   │   (with hash)   │
   └─────────────────┘

5. User redirected to /anomalies
6. Results displayed with severity badges
7. User can verify blockchain integrity with verify button
```

### **Scenario 3: User Views Dashboard**

```
1. User navigates to /dashboard
2. Flask route loads:
   ├─ Machine health data (MySQL)
   ├─ OEE calculations (MySQL)
   ├─ Recent alerts (MySQL)
   ├─ ML anomalies (MySQL)
   └─ Maintenance schedule (MySQL)

3. Flask returns HTML with embedded JavaScript

4. JavaScript (in browser) makes AJAX call to /dashboard_data

5. Flask /dashboard_data returns JSON data:
   {
     "machines_health": [...],
     "factory_avg_oee": 85.5,
     "recent_alerts": [...],
     "ml_anomalies": [...]
   }

6. JavaScript updates charts dynamically:
   - OEE trend chart (Chart.js)
   - Quality donut chart
   - Machine health cards
   - Alert badges
```

---

## 🗺️ Flask Routes (URL Mapping)

### **Public Routes** (anyone can access)
```
GET  /                      → Redirect to dashboard
GET  /login                 → Login page
POST /login                 → Authenticate user
GET  /register              → Registration page
POST /register              → Create new user
GET  /logout                → Logout
```

### **Admin-Only Routes** (requires @admin_required decorator)
```
GET  /dashboard             → Main dashboard
GET  /dashboard_data        → Returns JSON for charts
GET  /machines              → List all machines
POST /add_machine           → Create machine
GET  /modify_machine/<id>   → Edit machine form
POST /modify_machine/<id>   → Update machine
GET  /performance           → Performance data entry
POST /add_performance       → Insert performance record
POST /run_anomaly_scan      → Trigger ML scan
GET  /anomalies             → View anomaly results
GET  /alerts                → View system alerts
GET  /blockchain            → View blockchain log
GET  /verify_blockchain     → Verify chain integrity
GET  /audit_logs            → MongoDB audit trail
GET  /mongodb_stats         → Database statistics
```

### **API Routes** (return JSON)
```
GET  /dashboard_data        → Dashboard metrics
GET  /verify_blockchain     → Blockchain verification result
```

---

## 🔐 Database Layer Architecture

### **MySQL Tables** (Transactional - structured data)

```
Machine
├─ MachineID (Primary Key)
├─ MachineName
├─ MachineType
└─ Location

Performance_Data
├─ PerformanceID (Primary Key)
├─ MachineID (Foreign Key → Machine)
├─ OperatingTime
├─ Downtime
├─ ActualOutput
└─ OEE (calculated)

Alerts
├─ AlertID
├─ MachineID
├─ AlertMessage
└─ Severity

Anomaly_Detection
├─ AnomalyID
├─ MachineID
├─ AnomalyScore
├─ IsAnomaly
└─ Timestamp

Blockchain_Log
├─ BlockID
├─ Data
├─ Hash (SHA256)
├─ PreviousHash
└─ Timestamp
```

### **MongoDB Collections** (Analytical - flexible schema)

```
steel_factory_nosql
├─ anomaly_logs
│  └─ {_id, machine_id, score, timestamp, ...}
│
├─ audit_logs
│  └─ {_id, user, action, affected_table, timestamp, ...}
│
└─ scan_sessions
   └─ {_id, start_time, end_time, anomalies_found, status, ...}
```

**Why 3 databases?**
- **MySQL**: Fast, structured, transactional (OLTP)
- **MongoDB**: Scalable, flexible, good for time-series data (OLAP)
- **Blockchain**: Immutable, tamper-proof audit trail

---

## 🚀 Request/Response Cycle Example

### **User Clicks "View Machines"**

```
Step 1: Browser
  Action: Click link
  URL: /machines
  Request Type: GET

Step 2: Flask App (app.py)
  Route Handler: @app.route('/machines') def view_machines():
  Authentication: @admin_required checks if user is logged in
  Database: Connects to MySQL
  Query: SELECT * FROM Machine
  Processing: Converts results to list of dicts
  Response: render_template('machines.html', machines=machines)

Step 3: Jinja2 Template (templates/machines.html)
  Process: 
    - Inherits from base.html (navigation menu)
    - Loops through machines list: {% for machine in machines %}
    - Generates HTML table rows
    - Each row has Edit/Delete buttons
  
Step 4: Browser Receives
  HTML page with:
  - Navigation menu (from base.html)
  - Machines table
  - CSS styling (from static/style.css)
  - JavaScript for interactions

Step 5: User Sees
  Beautiful formatted page with all machines
  Can click "Edit" or "Delete"
```

---

## 🔄 ML Anomaly Detection Flow

```
User clicks "Run Anomaly Scan"
              ↓
Flask route: /run_anomaly_scan
              ↓
┌─────────────────────────────────────┐
│ Step 1: Fetch Data from MySQL       │
│ Query: SELECT * FROM Performance_Data
│ Result: 1000+ performance records    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Step 2: Prepare ML Features         │
│ Extract columns:                    │
│ - OperatingTime                     │
│ - Downtime                          │
│ - ActualOutput                      │
│ - GoodUnits                         │
│ Create feature matrix X             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Step 3: Run Isolation Forest        │
│ Model: IsolationForest(random_state=42)
│ Predict: [-1, 1, 1, -1, 1, ...]    │
│ (-1 = anomaly, 1 = normal)          │
│ Score: [-0.25, 0.1, 0.05, ...]     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Step 4: Store Results in 3 Places   │
│                                     │
│ MySQL anomaly_detection:            │
│ INSERT with is_anomaly, score       │
│                                     │
│ MongoDB anomaly_logs:               │
│ INSERT timestamp, machine_id, score │
│                                     │
│ Blockchain_log:                     │
│ INSERT hash = SHA256(data+prevhash) │
└─────────────────────────────────────┘
              ↓
Redirect to /anomalies
              ↓
Display results with color coding:
🔴 HIGH severity (score < -0.25)
🟠 MEDIUM severity (score -0.25 to 0)
🟢 NORMAL (score > 0)
```

---

## 🔐 User Authentication & Authorization

```
User visits /login
         ↓
Enters username & password
         ↓
Flask receives POST /login
         ↓
Query MySQL: SELECT * FROM User WHERE Username = 'admin'
         ↓
Check password: check_password_hash(stored_hash, input_password)
         ↓
If correct:
  - Create session: session['user_id'] = user_id
  - Create session: session['is_admin'] = True
  - Redirect to /dashboard
  
If wrong:
  - Flash error message
  - Redirect back to /login

Protected Routes:
  Every admin route has @admin_required decorator
  
  @admin_required checks:
    if 'user_id' not in session → Redirect to /login
    if session['is_admin'] != True → Deny access
```

---

## 🧩 Component Integration Map

```
                    ┌─────────────────┐
                    │   base.html     │
                    │  (Navigation)   │
                    └────────┬────────┘
                             │ extends
                             ▼
        ┌────────────────────────────────────────────┐
        │                                            │
    ┌───▼───┐  ┌──────────┐  ┌────────┐  ┌────────┐
    │login  │  │dashboard │  │machines│  │alerts  │
    │       │  │          │  │        │  │        │
    └───┬───┘  └────┬─────┘  └────┬───┘  └────┬───┘
        │           │             │           │
        │ calls     │ calls       │ calls    │ calls
        ▼           ▼             ▼         ▼
    ┌──────────────────────────────────────────────┐
    │         Flask Routes (app.py)               │
    │                                             │
    │ /login  /dashboard  /machines  /alerts    │
    │ /register /add_machine /run_anomaly_scan   │
    │ /anomalies /blockchain /verify_blockchain  │
    └──────────────────────────────────────────────┘
        │                │                  │
        │ queries        │ queries         │ queries
        ▼                ▼                 ▼
    ┌──────────┐   ┌──────────┐   ┌──────────────┐
    │  MySQL   │   │ MongoDB  │   │ Blockchain   │
    │          │   │          │   │ (MySQL)      │
    │ Users    │   │ Anomaly  │   │              │
    │ Machines │   │ Logs     │   │ Tamper-proof │
    │ Perf.    │   │ Audit    │   │ Records      │
    │ Alerts   │   │ Sessions │   │              │
    └──────────┘   └──────────┘   └──────────────┘
```

---

## 🎯 Key Concepts Explained

### **1. Jinja2 Templates**
- HTML files with Python-like syntax
- `{% for item in items %}` → Loop through data
- `{{ variable }}` → Display variable value
- `{% extends "base.html" %}` → Inherit layout

### **2. Flask Routes**
- `@app.route('/path')` → URL pattern
- `def function():` → What happens when someone visits that URL
- `render_template('file.html', data=data)` → Send HTML to browser
- `redirect(url_for('other_route'))` → Redirect to another page

### **3. Decorators**
- `@admin_required` → Only admins can access
- Checks if user is logged in and is admin
- If not, redirects to login

### **4. AJAX (Asynchronous JavaScript)**
- JavaScript makes background HTTP requests
- Updates page without full reload
- Used for real-time charts on dashboard
- `fetch('/dashboard_data')` → Get JSON from Flask

### **5. Blockchain Concept**
- Each block contains: Data + Hash of previous block
- If someone tampers with old data:
  - Old block's hash changes
  - All subsequent hashes break
  - Tampering is immediately visible
- Formula: `Hash = SHA256(current_data + previous_hash)`

---

## 🔌 Data Flow Summary

```
Admin Action → Flask Route → Database Query → Process → Response → UI Update

Example 1: Add Machine
  Click "Add" → POST /add_machine → INSERT into MySQL → Redirect → Show machines

Example 2: Run Scan
  Click "Scan" → POST /run_anomaly_scan → ML Processing → INSERT 3 DBs → Redirect → Show results

Example 3: View Dashboard
  Visit /dashboard → GET MySQL data → Format JSON → AJAX calls endpoint → JavaScript renders charts

Example 4: Check Blockchain
  Click "Verify" → GET /verify_blockchain → Recalculate all hashes → Compare → Return result
```

---

## 📝 Configuration (.env)

The `.env` file stores secrets:

```
# Flask
SECRET_KEY=your_secret_key              # Session encryption
ADMIN_USER=admin                        # Default admin username
ADMIN_PASS=admin123                     # Default admin password

# MySQL (Transactional)
DB_HOST=localhost
DB_USER=root
DB_PASS=your_mysql_password
DB_NAME=steel_factory_db

# MongoDB (Analytics)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=steel_factory_nosql
```

---

## 🚀 How Everything Works Together

1. **User logs in** → Session created, stored in Flask
2. **User navigates** → Browser requests page via URL
3. **Flask receives request** → Checks authentication
4. **Flask queries databases** → Gets data from MySQL/MongoDB
5. **Flask processes data** → Calculates OEE, finds anomalies
6. **Flask renders template** → Jinja2 creates HTML
7. **Browser receives HTML** → Loads CSS, runs JavaScript
8. **JavaScript calls API** → Makes AJAX requests for live data
9. **User sees dashboard** → Real-time charts and alerts
10. **User takes action** → Creates new records in databases

---

## 🎓 To Understand Code Better

Start here:
1. **app.py lines 1-100** → Configuration & setup
2. **app.py line 676** → Login route (simple example)
3. **app.py line 1944** → View anomalies route (read from DB)
4. **app.py line 1920** → Run anomaly scan (write to DB)
5. **templates/base.html** → Navigation structure
6. **templates/dashboard.html** → Complex template with AJAX

---

## 📊 Current Status

✅ **Working**
- Login/Registration
- Machine management
- Performance data entry
- Dashboard with charts
- Anomaly detection
- Blockchain verification
- MongoDB logging
- Alerts page (NEW)

⚠️ **Note**
- Alert table exists in MySQL but could have more data
- MongoDB stats now shows connection info
- All 3 databases are integrated and working

