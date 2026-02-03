# 🏭 Steel Factory Management System - Executive Summary

## What Does This System Do?

A **real-time production monitoring dashboard** that:
- ✅ Tracks machine health and performance (OEE metrics)
- ✅ Detects anomalies using Machine Learning
- ✅ Maintains tamper-proof audit trails using blockchain
- ✅ Stores historical data in MongoDB
- ✅ Generates alerts automatically
- ✅ Provides admin dashboard with real-time charts

**In Simple Terms:** It's like a smart supervisor for a steel factory that watches every machine, spots problems before they happen, and keeps an unbreakable record of everything.

---

## 🏗️ How It's Built

### The Stack
```
┌─ Frontend ─────────┐
│ HTML / CSS / JS    │ ← What you see in browser
└────────────────────┘
          ↓
┌─ Web Server ───────┐
│ Flask (Python)     │ ← Handles requests, processes data
└────────────────────┘
          ↓
┌─ Databases ────────┐
│ MySQL (SQL)        │ ← Structured data (machines, performance)
│ MongoDB (NoSQL)    │ ← Flexible data (audit logs, analytics)
│ Blockchain         │ ← Immutable records (tamper-proof)
└────────────────────┘
```

### The Three Databases (Why Three?)

| Database | Purpose | Data Type | Why? |
|----------|---------|-----------|------|
| **MySQL** | Core operations | Transactions | Fast, structured, ACID-compliant |
| **MongoDB** | Analytics & audit | Time-series | Flexible, scalable, easy to query |
| **Blockchain** | Security record | Immutable chain | Tamper-proof, cryptographic |

---

## 📊 System Architecture (Simple)

```
                      User (Admin)
                           │
                    Visits web page
                           │
                           ▼
                    Flask Web Server
                    (Python app.py)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    Queries              Writes               Queries
        │                  │                  │
        ▼                  ▼                  ▼
    MYSQL           MONGODB              BLOCKCHAIN
  (Read-only)      (Write logs)        (Write hash)
  Get machines    Store anomalies      Create blocks
  Get perf data   Store audits         Verify chain
  Get alerts      Store sessions
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    Returns data to UI
                           │
                           ▼
                  Browser shows dashboard
                   with charts & tables
```

---

## 🔄 How Data Flows (5 Minute Version)

### **Scenario: Admin runs anomaly detection**

**Step 1: Admin clicks "Run Scan"**
- Browser sends request to Flask

**Step 2: Flask gets data**
- Queries MySQL: "Give me all performance data"
- Gets 1000+ records of machine operations

**Step 3: ML Processing**
- Uses Isolation Forest algorithm
- Finds 50 records that are unusual
- Assigns anomaly scores to each

**Step 4: Store Results (3 places)**
- ✅ MySQL: Saves for quick lookup
- ✅ MongoDB: Saves for historical analytics
- ✅ Blockchain: Saves with hash for proof

**Step 5: Generate Alerts**
- High-severity anomalies create alerts
- Inserted into Alerts table

**Step 6: Display Results**
- Redirects admin to /anomalies page
- Shows color-coded list of anomalies

**Total Time:** ~5 seconds

---

## 🔐 Multi-Database Strategy

### **Why Not Just One Database?**

**MySQL alone is problematic:**
- Good for transactions but not for analytics
- Stores everything in rigid table structures
- Can't prevent tampering
- Not great for time-series data

**Solution: Use 3 databases for different purposes**

```
┌─ MySQL ──────────────────┐
│ Real-time operations     │
│ • Current machine status │
│ • User logins            │
│ • Alert states           │
│ • Anomaly records        │
└──────────────────────────┘
    Fast lookups, ACID safe

┌─ MongoDB ─────────────────┐
│ Historical analytics      │
│ • Anomaly logs (time     │
│   series)                │
│ • Audit trail (who did  │
│   what when)             │
│ • Scan sessions (stats)  │
└───────────────────────────┘
    Flexible, great for analytics

┌─ Blockchain ──────────────┐
│ Tamper-proof audit        │
│ • Immutable record        │
│ • Cryptographically       │
│   hashed                  │
│ • Can verify integrity    │
│ • Detect unauthorized     │
│   changes                 │
└───────────────────────────┘
    Impossible to fake, proof of integrity
```

---

## 🗺️ Key Routes (URLs)

### **What Can You Access?**

```
Public Routes (anyone):
  /login              ← Login page
  /register           ← Create account

Admin Routes (requires login):
  /dashboard          ← Main dashboard with charts
  /machines           ← Manage machines
  /performance        ← Add/view performance data
  /anomalies          ← ML detection results
  /alerts             ← System alerts
  /blockchain         ← Verify integrity
  /audit_logs         ← MongoDB audit trail
  /mongodb_stats      ← Database statistics
```

### **How Routes Work**

```
URL: http://127.0.0.1:5000/machines
     │                       │
     │                       └─ Route name
     └─ Server address & port

Flask receives GET /machines:
  ├─ Check: Is user logged in? @admin_required
  ├─ Query: SELECT * FROM Machine
  ├─ Format: Convert to list
  └─ Response: Render machines.html

Browser displays: List of all machines
```

---

## 💻 Frontend vs Backend

### **Frontend (What you see)**
- HTML pages (templates/)
- CSS styling (static/style.css)
- JavaScript for interactions
- Charts using Chart.js library
- Forms for data entry

### **Backend (What happens behind the scenes)**
- Flask server (Python code)
- Database queries
- ML algorithms
- Business logic
- Data processing

### **How They Talk**

```
Frontend                          Backend
(Browser)                         (Flask)
   │                                 │
   │───────────► GET /machines ────→ │
   │                                 │
   │                          Query MySQL
   │                                 │
   │◄─ HTML table with machines ───│
   │                                 │
   │ User clicks "Edit"              │
   │                                 │
   │───────────► POST /modify ─────→ │
   │              machine/1           │
   │                                 │
   │                          UPDATE MySQL
   │                                 │
   │◄─ Redirect to /machines ──────│
   │                                 │
   │ User sees updated list          │
```

---

## 🤖 ML Anomaly Detection Explained

### **What is Isolation Forest?**

An algorithm that finds unusual patterns in data.

**Like a bouncer at a nightclub:**
- Most people = normal (score: +0.1 to +0.5)
- Drunk person = anomaly (score: -0.3 to -0.5)
- Suspicious person = high anomaly (score: -0.8 to -1.0)

**How it works:**

```
Input: 1000 performance records
  ├─ Machine 1: Downtime=2h, Output=1000 ✓ Normal
  ├─ Machine 2: Downtime=5h, Output=950 ✓ Normal
  ├─ Machine 3: Downtime=480h, Output=0 ← ANOMALY!
  └─ Machine 4: Downtime=1h, Output=1100 ✓ Normal

Algorithm: "Machine 3 is VERY different from others"
Output: "This is an anomaly, score = -0.8"

Action: Create alert, flag for maintenance
```

---

## 🔒 Security Features

### **Authentication (Who Are You?)**
```
User submits username & password
            ↓
Flask checks MySQL User table
            ↓
Hashes password & compares
            ↓
✓ Match → Create session
✗ No match → Deny access
```

### **Authorization (What Can You Do?)**
```
All admin routes have @admin_required decorator

If not logged in → Redirect to /login
If not admin → Deny access
If admin → Proceed
```

### **Blockchain Tamper Detection**
```
Normal blockchain:
Block 1 → Block 2 → Block 3 (hashes match, all good)

If someone tries to change Block 1:
Block 1 (modified) → Hash changes
Block 2 expects old hash but gets new one
🚨 MISMATCH = TAMPERING DETECTED!
```

---

## 📈 Example: Real-World Usage

### **Morning: Factory Manager Logs In**

```
9:00 AM: Opens browser, logs in as admin

9:05 AM: Views dashboard
         → Sees all 10 machines
         → OEE = 85.5% (good)
         → 0 active alerts (all good)

9:30 AM: Adds new performance data
         → Furnace A1 ran for 8 hours
         → Produced 800 units
         → System calculates OEE automatically

2:00 PM: Runs anomaly detection
         → System scans all data
         → Finds 2 machines with odd patterns
         → Creates alerts automatically
         → Logs everything to MongoDB
         → Creates tamper-proof blockchain record

2:05 PM: Clicks "Verify Blockchain"
         → System recalculates all hashes
         → All match → Integrity confirmed ✓

3:00 PM: Checks audit log
         → Sees all actions today
         → Perfect accountability record
```

---

## 🛠️ How To Understand the Code

### **Read in This Order**

1. **This document** - Understand overall concept
2. **QUICK_REFERENCE.md** - Understand routing
3. **VISUAL_DIAGRAMS.md** - See visual examples
4. **schema.sql** (first 100 lines) - Understand database structure
5. **app.py** (lines 1-100) - Understand configuration
6. **app.py** (lines 676-750) - Study login (simple route)
7. **app.py** (lines 1944-2000) - Study anomaly view (read from DB)
8. **app.py** (lines 1920-1940) - Study anomaly scan (complex write)
9. **templates/base.html** - Understand layout
10. **templates/dashboard.html** - Understand AJAX & charts

---

## 🎯 Key Concepts

| Concept | Explanation |
|---------|-------------|
| **Route** | URL pattern like /machines that triggers code |
| **Template** | HTML file that Flask fills with data |
| **Session** | Data stored for logged-in user |
| **Decorator** | @symbol that adds functionality to function |
| **ORM/Query** | Way to talk to database from Python |
| **AJAX** | JavaScript that updates page without reload |
| **Hash** | Unique fingerprint of data (detects tampering) |
| **Anomaly** | Unusual pattern in data (detected by ML) |
| **Foreign Key** | Link between tables (referential integrity) |
| **Index** | Speed up database searches |

---

## ⚡ Quick Facts

- **Language:** Python (Flask web framework)
- **Frontend:** HTML, CSS, JavaScript
- **Databases:** 3 (MySQL, MongoDB, Blockchain)
- **ML Algorithm:** Isolation Forest
- **Lines of Code:** ~2,100 (app.py)
- **Templates:** 15+ HTML pages
- **Routes:** 30+ different URLs
- **Features:** Dashboard, anomaly detection, blockchain, audit trail
- **Security:** Password hashing, session management, blockchain verification

---

## 🚀 To Get Started

### **1. First Time?**
- Read this document (you're reading it! ✓)
- Read VISUAL_DIAGRAMS.md
- Read QUICK_REFERENCE.md

### **2. Want to Modify?**
- Run the app: `python app.py`
- Visit: `http://127.0.0.1:5000`
- Login with credentials from .env
- Test existing features

### **3. Want to Add Features?**
- Read app.py around the relevant route
- Add new route with @app.route('/new_page')
- Create template in templates/
- Query database as needed
- Return render_template() with data

### **4. Debug Issues?**
- Check Flask terminal for error messages
- Look at browser developer console (F12)
- Check MySQL/MongoDB connections
- Review logs in /audit_logs page

---

## 📚 File Structure Explained

```
project/
├─ app.py                      ← Main Flask application (2100+ lines)
│  ├─ Configuration (lines 1-100)
│  ├─ Helper functions (lines 100-300)
│  ├─ Routes (lines 300+)
│  └─ error handlers
│
├─ schema.sql                  ← Database table definitions
│  ├─ MySQL tables
│  └─ Sample data
│
├─ templates/                  ← HTML pages (Jinja2)
│  ├─ base.html               ← Main layout
│  ├─ dashboard.html          ← Charts & metrics
│  ├─ machines.html           ← Machine management
│  ├─ anomalies.html          ← ML results
│  ├─ alerts.html             ← Alert list (NEW)
│  ├─ blockchain.html         ← Verification
│  └─ [others...]
│
├─ static/                     ← CSS & assets
│  ├─ style.css               ← Styling
│  └─ [images, fonts, etc.]
│
├─ ARCHITECTURE_GUIDE.md       ← Comprehensive guide (this!)
├─ QUICK_REFERENCE.md         ← Routes & components
├─ VISUAL_DIAGRAMS.md         ← Visual explanations
└─ README.md                  ← Setup instructions
```

---

## 🎓 Learning Path

**Complete Beginner:**
1. Run the app and explore UI
2. Read this document
3. Read VISUAL_DIAGRAMS.md
4. Try logging in and using features

**Want to Code:**
1. Read QUICK_REFERENCE.md
2. Read first 100 lines of app.py
3. Study a simple route (e.g., /machines)
4. Read corresponding template
5. Understand data flow

**Want to Modify:**
1. Understand the route you want to change
2. Read the database query for that route
3. Modify the query or template
4. Restart Flask to test changes
5. Check browser console for errors

**Want to Add Features:**
1. Decide what URL/route you need
2. Write the Flask route handler
3. Create the template
4. Test with Flask running

---

## 💡 Pro Tips

- **Always check Flask console** - Error messages appear there first
- **Use browser F12 Developer Tools** - See network requests, console errors
- **Test routes individually** - Visit /machines, /anomalies, etc. separately
- **Understand foreign keys** - They link tables together
- **Blockchain is read-only** - Can't modify once written
- **MongoDB is flexible** - No schema required
- **Session expires on logout** - Always log back in for security

---

## 🤝 Common Questions

**Q: Why Flask and not Django?**
A: Flask is simpler, lighter, good for small-medium projects

**Q: Why MongoDB AND MySQL?**
A: MySQL for transactions, MongoDB for analytics (different strengths)

**Q: Why blockchain?**
A: Tamper-proof audit trail, can't hide modifications

**Q: Is the ML good?**
A: Isolation Forest is good for anomaly detection on numerical data

**Q: Can I use this in production?**
A: Not yet - needs better error handling, logging, security hardening

**Q: How do I add a new page?**
A: Create route in app.py, create template in templates/, add link in base.html

---

## 🎯 Next Steps

1. ✅ Understand overall architecture (done!)
2. 📖 Read VISUAL_DIAGRAMS.md (visual examples)
3. 🗺️ Read QUICK_REFERENCE.md (routing details)
4. 🚀 Run the app: `python app.py`
5. 🧪 Explore features in browser
6. 💻 Start reading app.py line by line
7. 🔧 Make small modifications
8. 📚 Add new features!

---

**That's it! You now understand how this system works. The rest is just details.**

Happy coding! 🚀

