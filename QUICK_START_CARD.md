# 🎯 Quick Reference Card

## In 30 Seconds...

**What is this?**
- Factory monitoring dashboard with ML anomaly detection

**Tech Stack:**
- Frontend: HTML/CSS/JavaScript
- Backend: Flask (Python)
- Databases: MySQL + MongoDB + Blockchain

**Why 3 databases?**
- MySQL: Fast transactions
- MongoDB: Flexible analytics  
- Blockchain: Tamper-proof audit

---

## 🔄 Data Flow (Simple)

```
User Action → Flask Route → Database Query → Process → Display
```

**Example:** Click "Run Scan"
```
POST /run_anomaly_scan
    ↓
Fetch 1000 performance records from MySQL
    ↓
Run ML (Isolation Forest) algorithm
    ↓
Write results to MySQL + MongoDB + Blockchain
    ↓
Redirect to /anomalies
    ↓
Show updated anomaly list with color badges
```

---

## 📍 Main Routes (Quick Access)

| URL | What It Does |
|-----|--------------|
| `/login` | User login |
| `/dashboard` | Main dashboard with charts |
| `/machines` | List/manage machines |
| `/performance` | Add performance data |
| `/anomalies` | View ML results |
| `/alerts` | View system alerts |
| `/blockchain` | Verify integrity |
| `/audit_logs` | View MongoDB logs |

---

## 🗄️ Database Tables (Quick Lookup)

```
MySQL:
├─ Machine (machines list)
├─ Performance_Data (sensor readings)
├─ Anomaly_Detection (ML results)
├─ Alerts (system alerts)
├─ Blockchain_Log (hashed records)
└─ User (logins)

MongoDB:
├─ anomaly_logs (historical anomalies)
├─ audit_logs (who did what when)
└─ scan_sessions (scan stats)
```

---

## 🔐 User Roles

| Role | Access |
|------|--------|
| Not logged in | /login, /register only |
| Admin (logged in) | ALL routes |
| Regular user | (Not supported yet) |

---

## 📊 ML Anomaly Detection

**Input:** 1000+ performance records
**Algorithm:** Isolation Forest
**Output:** 
- Anomaly score (positive = normal, negative = anomaly)
- Severity badge (🔴 HIGH or 🟠 MEDIUM)
- Stored in 3 databases

---

## 🔗 Component Connections

```
HTML Templates
    ↓ render via
Jinja2 Engine
    ↓ uses data from
Flask Routes
    ↓ query
MySQL/MongoDB/Blockchain
```

---

## 🧩 File Locations

```
Code:           app.py (2100 lines)
Database:       schema.sql
Templates:      templates/*.html
Styles:         static/style.css
Config:         .env
```

---

## ⚡ Quick Commands

```bash
# Start app
python app.py

# Default URL
http://127.0.0.1:5000

# Default login
user: admin
pass: admin123 (from .env)

# Check services
MySQL: localhost:3306
MongoDB: localhost:27017
Flask: localhost:5000
```

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Table doesn't exist" | Run schema.sql to create tables |
| MongoDB connection failed | Make sure mongod is running |
| 404 Page Not Found | Check route name in app.py |
| Styling looks weird | Clear browser cache (Ctrl+Shift+Del) |
| Changes not showing | Restart Flask (Ctrl+C, python app.py) |

---

## 🧠 Key Concepts

| Term | Means |
|------|-------|
| **Route** | URL pattern like /machines |
| **Template** | HTML file with data |
| **Session** | Logged-in user info |
| **Hash** | Fingerprint of data |
| **AJAX** | Background HTTP request |
| **Anomaly** | Unusual pattern in data |
| **OEE** | Overall Equipment Effectiveness |

---

## 📚 Where to Learn More

| Topic | File |
|-------|------|
| System overview | COMPLETE_GUIDE.md |
| Visual diagrams | VISUAL_DIAGRAMS.md |
| Full architecture | ARCHITECTURE_GUIDE.md |
| Routes & components | QUICK_REFERENCE.md |
| Navigation | START_HERE.md |

---

## ✅ To Modify Code

1. **Find** the route in app.py
2. **Understand** the database query
3. **Edit** the code or template
4. **Restart** Flask: Ctrl+C → python app.py
5. **Test** in browser

---

## 🔍 To Debug

1. **Browser:** Press F12 → Console tab
2. **Flask terminal:** Look for error messages
3. **Database:** Check if tables exist
4. **Config:** Verify .env settings
5. **Restart:** Sometimes fixes mysteriously

---

## 📈 Example: Add Machine

```
User Input
    ↓
Form POST to /add_machine
    ↓
Flask validates data
    ↓
INSERT into MySQL Machine table
    ↓
Log to MongoDB audit_logs
    ↓
Redirect to /machines
    ↓
User sees new machine in list
```

---

## 💾 Example: Run ML Scan

```
User clicks "Run Scan"
    ↓
POST /run_anomaly_scan
    ↓
Fetch data from MySQL
    ↓
Run Isolation Forest
    ↓
Write to:
├─ MySQL anomaly_detection
├─ MongoDB anomaly_logs
└─ Blockchain (hashed)
    ↓
Redirect to /anomalies
    ↓
Display results
```

---

## 🔐 Example: Login

```
User enters credentials
    ↓
POST /login
    ↓
Query MySQL User table
    ↓
Check password hash
    ↓
Create session
    ↓
Redirect to /dashboard
```

---

## 🎯 3 Ways to Understand Code

| Way | How | Time |
|-----|-----|------|
| **Docs** | Read explanations | 2 hours |
| **Visual** | See diagrams | 1 hour |
| **Code** | Read app.py | 4 hours |

**Best:** Do all three!

---

## 📞 Questions?

| Question | Read This |
|----------|-----------|
| What does system do? | COMPLETE_GUIDE.md |
| How routes work? | QUICK_REFERENCE.md |
| How data flows? | VISUAL_DIAGRAMS.md |
| Full details? | ARCHITECTURE_GUIDE.md |
| Where to start? | START_HERE.md |

---

## 🚀 In 5 Steps

1. ✅ Read COMPLETE_GUIDE.md (understand WHAT)
2. ✅ Read VISUAL_DIAGRAMS.md (understand HOW)
3. ✅ Read QUICK_REFERENCE.md (understand WHERE)
4. ✅ Run `python app.py` (see it work)
5. ✅ Read app.py with docs open (understand WHY)

**Done!** You're now an expert on this system 🎉

---

**Print this page and keep it handy while reading code!**

