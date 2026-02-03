# 📚 Documentation Index

## Start Here! 👈

If you don't know anything about the project, **read these in order:**

### **🔴 Level 1: Absolute Beginners** (30 minutes)
1. **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** ← START HERE
   - What does the system do?
   - Why 3 databases?
   - How data flows
   - Key concepts explained

### **🟠 Level 2: Want to Understand Architecture** (1 hour)
2. **[VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md)** ← Read this next
   - System overview diagram
   - Request-response cycle
   - Data flow visualizations
   - All relationships explained visually

3. **[ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)**
   - Detailed component breakdown
   - Database layer architecture
   - ML pipeline explained
   - Integration map

### **🟡 Level 3: Ready to Code** (2 hours)
4. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**
   - Complete routing map
   - Component connections
   - Request lifecycle examples
   - Frontend architecture

5. **app.py** (start with lines 1-100)
   - Configuration
   - Imports
   - Database helpers
   - Environment setup

### **🟢 Level 4: Advanced** (4+ hours)
6. **app.py** (read specific routes)
   - /login (simple example) - lines 676-750
   - /machines (read example) - lines 1700-1750
   - /run_anomaly_scan (complex example) - lines 1920-1940
   - /verify_blockchain (verification) - lines 1850-1900

7. **schema.sql** (understand database)
   - Table definitions
   - Relationships
   - Constraints

8. **templates/** (understand frontend)
   - base.html (layout)
   - dashboard.html (complex JS)
   - [specific pages as needed]

---

## 🗂️ Documentation Files

### **Core Documentation**
| File | Purpose | Read Time |
|------|---------|-----------|
| [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) | Executive summary, key concepts | 20 min |
| [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) | Diagrams and visual explanations | 30 min |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Routes, components, connections | 40 min |
| [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) | Deep dive into architecture | 60 min |
| [README.md](README.md) | Setup instructions | 15 min |

### **Code Files**
| File | Purpose | Lines | Importance |
|------|---------|-------|------------|
| app.py | Main Flask application | 2100+ | 🔴 CRITICAL |
| schema.sql | Database schema | 450+ | 🔴 CRITICAL |
| templates/base.html | Layout template | 80+ | 🟠 HIGH |
| templates/dashboard.html | Main dashboard | 250+ | 🟠 HIGH |
| requirements.txt | Python dependencies | 8 | 🟡 MEDIUM |
| .env | Configuration secrets | 10+ | 🔴 CRITICAL |

---

## 🎯 By Role

### **If You're a Manager/Stakeholder**
1. Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - understand value proposition
2. Skim [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - see architecture
3. Done! ✓

### **If You're a QA/Tester**
1. Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
2. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - understand all routes
3. Test each route manually
4. Check browser console for errors
5. Done! ✓

### **If You're a Junior Developer**
1. Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
2. Read [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md)
3. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. Read app.py lines 1-100 (setup)
5. Read one simple route (e.g., /login)
6. Read corresponding template
7. Follow that pattern to understand others

### **If You're a Senior Developer/Architect**
1. Skim [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
2. Review [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)
3. Read app.py in full
4. Review database schema
5. Identify improvements needed

### **If You're a Database Admin**
1. Read schema.sql
2. Understand relationships
3. Understand data flow to 3 databases
4. Set up indexes for performance
5. Plan backup strategy for blockchain_log

### **If You're a DevOps/Infra**
1. Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) (what it does)
2. Read requirements.txt (dependencies)
3. Check .env for configuration
4. Plan deployment environment
5. Set up MySQL + MongoDB

---

## 🔍 Quick Lookup

### **I want to understand...**

**How routes work?**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - "Complete Routing Map"
→ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Request-Response Cycle"
→ app.py - lines 676-750 (/login route)

**How databases connect?**
→ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Database Layer Architecture"
→ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Database Relationships"
→ schema.sql - full file

**How ML anomaly detection works?**
→ [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - "ML Anomaly Detection Explained"
→ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "ML Anomaly Detection Pipeline"
→ app.py - lines 1920-1940 (/run_anomaly_scan)

**How blockchain works?**
→ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Blockchain Concept"
→ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Blockchain Concept"
→ app.py - lines 1850-1900 (/verify_blockchain)

**How authentication works?**
→ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "User Authentication Flow"
→ app.py - lines 676-750 (/login route)

**How data flows?**
→ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Request-Response Cycle"
→ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Data Flow: Anomaly Scan"
→ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "How Data Flows"

**How templates work?**
→ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Template Inheritance Chain"
→ templates/base.html - understand layout
→ templates/dashboard.html - complex example with JavaScript

**How AJAX works?**
→ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Key Concepts Explained"
→ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Dashboard Real-Time Updates"
→ templates/dashboard.html - see AJAX in action

**How to add a new page?**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - "To Start Understanding"
→ Copy /machines route as template
→ Create new template in templates/
→ Add link to base.html navigation

**How to modify a route?**
→ Find route in app.py
→ Understand the database query
→ Modify query or template
→ Restart Flask (app.py)
→ Test in browser

---

## 📖 Reading Guide by Topic

### **Database**
```
Understanding Database Structure
├─ schema.sql (full file)
├─ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - Database Layer
└─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - Database Relationships

Understanding 3-Database Strategy
├─ [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - Multi-Database Strategy
├─ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Why 3 databases?"
└─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - Database section
```

### **Web Framework**
```
Understanding Flask
├─ [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - "How It's Built"
├─ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Flask Routes"
├─ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - "Complete Routing Map"
└─ app.py - read a simple route

Understanding Templates
├─ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Template Inheritance"
├─ templates/base.html
└─ templates/dashboard.html
```

### **Machine Learning**
```
Understanding Anomaly Detection
├─ [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - "ML Explained"
├─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "ML Pipeline"
├─ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "ML Anomaly Flow"
└─ app.py - /run_anomaly_scan route
```

### **Security**
```
Understanding Security
├─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Authentication Flow"
├─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Session Management"
├─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Blockchain Concept"
├─ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "User Authentication"
└─ app.py - /login and @admin_required
```

### **Frontend**
```
Understanding Frontend
├─ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Frontend Architecture"
├─ templates/base.html - layout
├─ templates/dashboard.html - complex example
├─ static/style.css - styling
└─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Template Inheritance"
```

### **Data Flow**
```
Understanding Complete Data Flow
├─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Complete System Overview"
├─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Request-Response Cycle"
├─ [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Data Flow: Anomaly Scan"
├─ [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "How Data Flows"
└─ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - "Request Lifecycle Examples"
```

---

## 🚀 Getting Started Checklist

### **Day 1: Understand the System**
- [ ] Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) (20 min)
- [ ] Read [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) (30 min)
- [ ] Understand: What does it do? Why 3 DBs? How does data flow?
- **Milestone:** You can explain the system to someone else ✓

### **Day 2: Understand Architecture**
- [ ] Read [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) (60 min)
- [ ] Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (40 min)
- [ ] Understand: All routes, components, how they connect
- **Milestone:** You can draw a diagram of the system ✓

### **Day 3: Start Reading Code**
- [ ] Read app.py lines 1-100 (20 min)
- [ ] Read schema.sql (20 min)
- [ ] Read /login route (app.py 676-750) (20 min)
- [ ] Understand one complete route end-to-end
- **Milestone:** You can trace a request from browser to database ✓

### **Day 4: Explore Features**
- [ ] Run the app: `python app.py`
- [ ] Visit all pages
- [ ] Test login/logout
- [ ] Run anomaly scan
- [ ] Check blockchain verification
- **Milestone:** You've used all features ✓

### **Day 5: Ready to Modify**
- [ ] Pick one simple route (e.g., /machines)
- [ ] Understand its database query
- [ ] Make a small modification
- [ ] Test your changes
- **Milestone:** You can modify existing code ✓

---

## 📞 Need Help?

**Question: "I don't understand routes"**
→ Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - "Complete Routing Map"
→ Read [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Request-Response Cycle"

**Question: "How does authentication work?"**
→ Read [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "User Authentication Flow"
→ Read app.py /login route

**Question: "Why 3 databases?"**
→ Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - "Multi-Database Strategy"
→ Read [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - "Database Layer"

**Question: "How do I add a new page?"**
→ Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - "To Start Understanding"
→ Copy existing route pattern
→ Create new template
→ Add to navigation in base.html

**Question: "What's blockchain doing here?"**
→ Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - "Multi-Database Strategy"
→ Read [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "Blockchain Concept"

**Question: "How does ML work?"**
→ Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - "ML Explained"
→ Read [VISUAL_DIAGRAMS.md](VISUAL_DIAGRAMS.md) - "ML Pipeline"

---

## 🎓 Learning Outcomes

After reading all documentation, you should understand:

- ✅ What the system does (factory monitoring)
- ✅ Why it's built this way (3 databases)
- ✅ How data flows through the system
- ✅ How every route works
- ✅ How database queries work
- ✅ How templates render
- ✅ How ML anomaly detection works
- ✅ How blockchain verification works
- ✅ How authentication works
- ✅ How to modify existing code
- ✅ How to add new features

---

## 🔗 Quick Links

| What | Where |
|------|-------|
| Main Python Code | [app.py](app.py) |
| Database Schema | [schema.sql](schema.sql) |
| HTML Templates | [templates/](templates/) |
| CSS Styling | [static/style.css](static/style.css) |
| Setup Guide | [README.md](README.md) |
| Configuration | [.env](.env) |

---

**Start with [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - it explains everything clearly! 👈**

