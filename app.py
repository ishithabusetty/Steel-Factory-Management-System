"""
Full app.py for SteelFactoryDBMS
Features:
 - Dashboard data endpoint with OEE recompute
 - IsolationForest ML anomalies (optional if sklearn/numpy installed)
 - Write anomalies into anomaly_detection table
 - Add deduped Alerts and Maintenance entries
 - Returns JSON structured for the dashboard.html below

Required packages (if you want ML):
  pip install numpy scikit-learn python-dotenv mysql-connector-python
"""

from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import mysql.connector
import hashlib
import os
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime
import logging

# Optional ML imports
try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    ML_AVAILABLE = True
except Exception as e:
    logging.getLogger(__name__).warning("ML libraries not available: %s", e)
    ML_AVAILABLE = False

# -------------------------
# Load env and config
# -------------------------
load_dotenv()
MASTER_OVERRIDE = os.getenv("OVERRIDE_PASSWORD", "admin123")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_local_secret")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "Ishitha!cs2")
DB_NAME = os.getenv("DB_NAME", "steel_factory_db")

app = Flask(__name__)
app.secret_key = SECRET_KEY

# -------------------------
# DB helper
# -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=False
    )

# -------------------------
# Hash generator
# -------------------------
def generate_hash(data_string):
    return hashlib.sha256(data_string.encode()).hexdigest()

# -------------------------
# Admin required decorator
# -------------------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated

# -------------------------
# Alerts helper (prevents duplicates within a timeframe)
# -------------------------
def add_alert(machine_id, message, severity="MEDIUM", dedupe_minutes=60):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # check if same message exists within dedupe_minutes
        cur.execute("""
            SELECT AlertID FROM Alerts
            WHERE MachineID=%s AND AlertMessage=%s AND Timestamp > DATE_SUB(NOW(), INTERVAL %s MINUTE)
            LIMIT 1
        """, (machine_id, message, dedupe_minutes))
        if cur.fetchone():
            return False  # duplicate recently, skip insert

        cur.execute("""
            INSERT INTO Alerts (MachineID, AlertMessage, Severity)
            VALUES (%s, %s, %s)
        """, (machine_id, message, severity))
        conn.commit()
        return True
    except Exception as e:
        logging.getLogger(__name__).warning("add_alert failed: %s", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# -------------------------
# Maintenance helper (prevents duplicate pending entries)
# -------------------------
def add_maintenance(machine_id, issue, status="PENDING"):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # If there's already a pending maintenance with same issue recently, skip
        cur.execute("""
            SELECT MaintenanceID FROM maintenance_log
            WHERE MachineID=%s AND IssueDescription=%s AND Status=%s
            LIMIT 1
        """, (machine_id, issue, status))
        if cur.fetchone():
            return False

        cur.execute("""
            INSERT INTO maintenance_log (MachineID, IssueDescription, MaintenanceDate, Status)
            VALUES (%s, %s, NOW(), %s)
        """, (machine_id, issue, status))
        conn.commit()
        return True
    except Exception as e:
        logging.getLogger(__name__).warning("add_maintenance failed: %s", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

# -------------------------
# Blockchain helpers (unchanged)
# -------------------------
def add_block_to_chain(performance_id, data_string):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Hash FROM blockchain_log ORDER BY BlockID DESC LIMIT 1")
        last = cursor.fetchone()
        prev_hash = last[0] if last else "0"
        new_hash = generate_hash(data_string + prev_hash)
        cursor.execute("""
            INSERT INTO blockchain_log (PerformanceID, Hash, PrevHash, Data)
            VALUES (%s, %s, %s, %s)
        """, (performance_id, new_hash, prev_hash, data_string))
        conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning("add_block_to_chain failed: %s", e)
        try:
            conn.rollback()
        except:
            pass
    finally:
        cursor.close()
        conn.close()

def log_machine_event(data_string):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Hash FROM blockchain_log ORDER BY BlockID DESC LIMIT 1")
        last = cursor.fetchone()
        prev_hash = last[0] if last else "0"
        new_hash = generate_hash(data_string + prev_hash)
        cursor.execute("""
            INSERT INTO blockchain_log (PerformanceID, Hash, PrevHash, Data)
            VALUES (%s, %s, %s, %s)
        """, (None, new_hash, prev_hash, data_string))
        conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning("log_machine_event failed: %s", e)
        try:
            conn.rollback()
        except:
            pass
    finally:
        cursor.close()
        conn.close()

# -------------------------
# OEE update helper (unchanged)
# -------------------------
def update_oee_values():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT PerformanceID, OperatingTime, Downtime, ActualOutput, IdealOutput, GoodUnits, TotalUnits
            FROM Performance_Data
        """)
        rows = cursor.fetchall()
        for r in rows:
            pid = r[0]
            ot = float(r[1] or 0)
            down = float(r[2] or 0)
            ao = int(r[3] or 0)
            io = int(r[4] or 0)
            gu = int(r[5] or 0)
            tu = int(r[6] or 0)

            planned = ot + down
            if planned <= 0 or io <= 0 or tu <= 0:
                oee = 0.0
            else:
                availability = ot / planned if planned > 0 else 0
                performance = (ao / io) if io > 0 else 0
                quality = (gu / tu) if tu > 0 else 0
                oee = availability * performance * quality * 100

            cursor.execute("UPDATE Performance_Data SET OEE=%s WHERE PerformanceID=%s", (oee, pid))
        conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning("update_oee_values failed: %s", e)
        try:
            conn.rollback()
        except:
            pass
    finally:
        cursor.close()
        conn.close()

# -------------------------
# Auth routes (mostly unchanged)
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or url_for('dashboard')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if ADMIN_USER and ADMIN_PASS and username == ADMIN_USER and password == ADMIN_PASS:
            session['is_admin'] = True
            session['admin_name'] = username
            flash("Logged in as admin.", "success")
            return redirect(request.form.get('next') or url_for('dashboard'))
        else:
            flash("Invalid credentials.", "error")
            return render_template('login.html', next=next_url)
    return render_template('login.html', next=next_url)

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    session.pop('admin_name', None)
    flash("Logged out.", "info")
    return redirect(url_for('dashboard'))

# -------------------------
# Dashboard routes + data
# -------------------------
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', is_admin=session.get('is_admin', False))

@app.route('/dashboard_data')
def dashboard_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ensure OEE updated
    update_oee_values()

    # 1) OEE trend + per-row metrics
    try:
        cursor.execute("""
            SELECT PerformanceID, MachineID, OperatingTime, Downtime, ActualOutput, IdealOutput, GoodUnits, TotalUnits, OEE
            FROM Performance_Data
            ORDER BY PerformanceID ASC
        """)
        perf_rows_full = cursor.fetchall()
    except Exception as e:
        logging.getLogger(__name__).warning("Perf full fetch failed: %s", e)
        perf_rows_full = []

    oee_labels = []
    oee_values = []
    availability_values = []
    performance_values = []
    quality_values = []

    # ML feature containers
    ml_features = []
    ml_map = []  # list of tuples (PerformanceID, MachineID)

    for r in perf_rows_full:
        pid, mid, ot, down, ao, io, gu, tu, oee = r
        ot = float(ot or 0)
        down = float(down or 0)
        ao = int(ao or 0)
        io = int(io or 0)
        gu = int(gu or 0)
        tu = int(tu or 0)

        planned = ot + down
        availability = (ot / planned * 100) if planned > 0 else 0
        performance = (ao / io * 100) if io > 0 else 0
        quality = (gu / tu * 100) if tu > 0 else 0

        oee_labels.append(str(pid))
        oee_values.append(float(oee or 0))
        availability_values.append(round(availability, 2))
        performance_values.append(round(performance, 2))
        quality_values.append(round(quality, 2))

        ml_features.append([float(oee or 0), down, ao])
        ml_map.append((pid, mid))

    # 2) Machine summary
    try:
        cursor.execute("""
            SELECT m.MachineID, m.MachineName,
                   AVG(p.OEE) as avg_oee,
                   SUM(p.Downtime) as total_downtime,
                   AVG(CASE WHEN p.TotalUnits>0 THEN p.GoodUnits/p.TotalUnits ELSE 0 END) * 100 as avg_quality
            FROM Machine m
            LEFT JOIN Performance_Data p ON m.MachineID = p.MachineID
            GROUP BY m.MachineID
        """)
        machine_rows = cursor.fetchall()
    except Exception as e:
        logging.getLogger(__name__).warning("Machine summary fetch failed: %s", e)
        machine_rows = []

    machines_health = []
    all_oee = []
    for row in machine_rows:
        mid = row[0]
        name = row[1] or f"Machine-{mid}"
        avg_oee = float(row[2]) if row[2] is not None else 0.0
        downtime = float(row[3]) if row[3] is not None else 0.0
        avg_quality = float(row[4]) if row[4] is not None else 0.0

        all_oee.append(avg_oee)
        machines_health.append({
            "id": mid,
            "name": name,
            "oee": round(avg_oee, 2),
            "downtime": round(downtime, 2),
            "quality": round(avg_quality, 2),
            "status": "healthy" if avg_oee >= 85 else "warning" if avg_oee >= 70 else "critical"
        })

    factory_avg_oee = (sum(all_oee) / len(all_oee)) if all_oee else 0.0
    factory_status = "healthy" if factory_avg_oee >= 85 else "warning" if factory_avg_oee >= 70 else "critical"

    # 3) Good vs defective
    try:
        cursor.execute("SELECT SUM(GoodUnits), SUM(TotalUnits) FROM Performance_Data")
        r = cursor.fetchone()
        good_units = int(r[0] or 0)
        total_units = int(r[1] or 0)
        defective_units = max(total_units - good_units, 0)
    except Exception:
        good_units = 0
        total_units = 0
        defective_units = 0

    # 4) Recent alerts (fetch last 50, we'll dedupe later)
    recent_alerts = []
    try:
        cursor.execute("""
            SELECT a.AlertID, a.MachineID, a.AlertMessage, m.MachineName, a.Severity, a.Timestamp
            FROM Alerts a
            LEFT JOIN Machine m ON a.MachineID = m.MachineID
            ORDER BY a.Timestamp DESC
            LIMIT 50
        """)
        ar = cursor.fetchall()
        for row in ar:
            aid, mid, msg, mname, sev, ts = row
            recent_alerts.append({
                "id": aid,
                "machine_id": mid,
                "machine": mname or f"Machine-{mid}",
                "message": msg,
                "severity": sev or "MEDIUM",
                "time": ts.strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            })
    except Exception as e:
        logging.getLogger(__name__).warning("Fetch recent_alerts failed: %s", e)
        recent_alerts = []

    # dedupe alerts: keep newest per machine+message
    deduped_alerts_map = {}
    for a in recent_alerts:
        key = f"{a['machine']}|{a['message']}"
        if key not in deduped_alerts_map:
            deduped_alerts_map[key] = a
    deduped_alerts = list(deduped_alerts_map.values())

    # 5) Simple anomalies (top low OEE rows) - keep these for fallback
    anomalies = []
    try:
        cursor.execute("""
            SELECT p.PerformanceID, m.MachineName, p.OEE
            FROM Performance_Data p
            LEFT JOIN Machine m ON p.MachineID = m.MachineID
            ORDER BY p.OEE ASC LIMIT 3
        """)
        low_rows = cursor.fetchall()
        for lr in low_rows:
            anomalies.append({
                "machine": lr[1] or "Unknown",
                "issue": "Low OEE detected",
                "recommendation": "Schedule inspection"
            })
    except Exception:
        anomalies = []

    # 6) ML anomaly detection + populate anomaly_detection table safely
    ml_anomalies = []
    try:
        # optional: clear previous anomaly_detection if you want fresh each run
        # cursor.execute("DELETE FROM anomaly_detection")
        # conn.commit()
        pass
    except Exception as e:
        logging.getLogger(__name__).warning("Failed to clear anomaly_detection: %s", e)
        try:
            conn.rollback()
        except:
            pass

    if ML_AVAILABLE and len(ml_features) >= 6:
        try:
            X = np.array(ml_features, dtype=float)
            contamination = 0.05 if len(X) > 100 else 0.08
            iso = IsolationForest(contamination=contamination, random_state=42)
            preds = iso.fit_predict(X)  # -1 anomaly, 1 normal
            scores = iso.decision_function(X)  # higher -> less anomalous

            # Insert anomalies and create alerts/maintenance with dedupe checks
            for i, pred in enumerate(preds):
                pid, mid = ml_map[i]
                score = float(scores[i])
                is_anom = 1 if pred == -1 else 0

                # Insert anomaly row into DB (store score + flag)
                try:
                    cursor.execute("""
                        INSERT INTO anomaly_detection (MachineID, PerformanceID, AnomalyScore, IsAnomaly, Timestamp)
                        VALUES (%s, %s, %s, %s, NOW())
                    """, (mid, pid, score, is_anom))
                    conn.commit()
                except Exception as e:
                    logging.getLogger(__name__).warning("Insert anomaly_detection failed: %s", e)
                    try:
                        conn.rollback()
                    except:
                        pass

                if is_anom:
                    severity = "HIGH" if score < -0.25 else "MEDIUM"
                    # friendly machine name if available
                    try:
                        cursor2 = conn.cursor()
                        cursor2.execute("SELECT MachineName FROM Machine WHERE MachineID=%s", (mid,))
                        mn = cursor2.fetchone()
                        machine_name = mn[0] if mn and mn[0] else f"Machine {mid}"
                        cursor2.close()
                    except Exception:
                        machine_name = f"Machine {mid}"

                    ml_anomalies.append({
                        "machine": machine_name,
                        "issue": f"ML anomaly detected (score {score:.3f})",
                        "severity": severity,
                        "score": round(score, 3),
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    # Add an alert (deduped by DB helper)
                    try:
                        add_alert(mid, f"{machine_name}: ML anomaly detected (score {score:.3f})", severity, dedupe_minutes=60)
                    except Exception as e:
                        logging.getLogger(__name__).warning("add_alert in ML loop failed: %s", e)

                    # If HIGH severity, schedule maintenance (dedup checks inside add_maintenance)
                    if severity == "HIGH":
                        try:
                            add_maintenance(mid, f"{machine_name}: Predicted failure risk - HIGH")
                        except Exception as e:
                            logging.getLogger(__name__).warning("add_maintenance in ML loop failed: %s", e)

        except Exception as e:
            logging.getLogger(__name__).warning("ML pipeline error: %s", e)
    else:
        logging.getLogger(__name__).info("Skipping ML: available=%s, rows=%d", ML_AVAILABLE, len(ml_features))

    # dedupe ml_anomalies by machine (keep latest)
    dedup_ml = {}
    for a in ml_anomalies:
        dedup_ml[a["machine"]] = a
    ml_final = list(dedup_ml.values())

    # 7) Maintenance list for dashboard (pending) - dedupe by machine name
    maintenance = []
    try:
        cursor.execute("""
            SELECT ml.MaintenanceID, ml.MachineID, ml.IssueDescription, ml.MaintenanceDate, ml.Status, m.MachineName
            FROM maintenance_log ml
            LEFT JOIN Machine m ON ml.MachineID = m.MachineID
            WHERE ml.Status IN ('PENDING','SCHEDULED')
            ORDER BY ml.MaintenanceDate DESC
            LIMIT 50
        """)
        maint_rows = cursor.fetchall()
        # dedupe by machine name, keep the latest
        seen_maint = {}
        for mr in maint_rows:
            mid = mr[1]
            mname = mr[5] or f"Machine-{mid}"
            if mname not in seen_maint:
                seen_maint[mname] = {
                    "maintenance_id": mr[0],
                    "machine": mname,
                    "reason": mr[2],
                    "date": mr[3].strftime("%Y-%m-%d %H:%M:%S") if mr[3] else "",
                    "status": mr[4]
                }
        maintenance = list(seen_maint.values())
    except Exception as e:
        logging.getLogger(__name__).warning("Fetch maintenance failed: %s", e)
        maintenance = []

    # close cursor/connection
    try:
        cursor.close()
        conn.close()
    except:
        pass

    payload = {
        "oee_labels": oee_labels,
        "oee_values": oee_values,
        "availability": availability_values,
        "performance": performance_values,
        "quality": quality_values,

        "machines_health": machines_health,
        "factory_avg_oee": round(factory_avg_oee, 2),
        "factory_status": factory_status,

        "good_units": good_units,
        "defective_units": defective_units,
        "factory_total_units": total_units,

        "anomalies": anomalies,            # simple OEE-based anomalies (fallback)
        "ml_anomalies": ml_final,          # ML anomalies (deduped)
        "recent_alerts": deduped_alerts,   # deduped alerts
        "maintenance": maintenance         # deduped maintenance entries
    }

    return jsonify(payload)

# -------------------------
# Machines routes (unchanged)
# -------------------------
@app.route('/machines')
def view_machines():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MachineID, MachineName, MachineType, Location, Status FROM Machine")
    machines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('machines.html', machines=machines, is_admin=session.get('is_admin', False))

@app.route('/add_machine', methods=['GET', 'POST'])
@admin_required
def add_machine():
    message = ""
    if request.method == 'POST':
        name = request.form['name'].strip()
        mtype = request.form['type'].strip()
        location = request.form['location'].strip()
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Machine WHERE MachineName=%s", (name,))
        existing = cursor.fetchone()

        if existing:
            message = f"⚠️ Machine '{name}' already exists!"
        else:
            cursor.execute("""
                INSERT INTO Machine (MachineName, MachineType, Location, Status)
                VALUES (%s, %s, %s, %s)
            """, (name, mtype, location, status))
            conn.commit()
            new_mid = cursor.lastrowid
            message = f"✅ Machine '{name}' added successfully!"
            event = f"ADD_MACHINE|MachineID={new_mid}|Name={name}|Type={mtype}|Loc={location}|Status={status}"
            log_machine_event(event)

        cursor.close()
        conn.close()
        return render_template('add_machine.html', message=message, is_admin=True)

    return render_template('add_machine.html', message=message, is_admin=True)

@app.route('/modify_machine/<int:mid>', methods=['GET', 'POST'])
@admin_required
def modify_machine(mid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MachineID, MachineName, MachineType, Location, Status FROM Machine WHERE MachineID=%s", (mid,))
    machine = cursor.fetchone()
    if not machine:
        cursor.close(); conn.close()
        flash("Machine not found.", "error")
        return redirect(url_for('view_machines'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        mtype = request.form['type'].strip()
        location = request.form['location'].strip()
        status = request.form['status']
        override = request.form.get('override_password', '')
        if override != MASTER_OVERRIDE:
            cursor.close(); conn.close()
            return render_template('modify_machine.html', machine=machine, message="❌ Wrong override password", is_admin=True)
        cursor.execute("""
            UPDATE Machine SET MachineName=%s, MachineType=%s, Location=%s, Status=%s WHERE MachineID=%s
        """, (name, mtype, location, status, mid))
        conn.commit()
        event = f"MODIFY_MACHINE|MachineID={mid}|NewName={name}|NewType={mtype}|NewLocation={location}|NewStatus={status}"
        log_machine_event(event)
        cursor.close(); conn.close()
        flash("Machine updated.", "success")
        return redirect(url_for('view_machines'))

    cursor.close(); conn.close()
    return render_template('modify_machine.html', machine=machine, message="", is_admin=True)

@app.route('/delete_machine/<int:mid>', methods=['POST'])
@admin_required
def delete_machine(mid):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Performance_Data WHERE MachineID=%s", (mid,))
        cursor.execute("DELETE FROM Machine WHERE MachineID=%s", (mid,))
        conn.commit()
        event = f"DELETE_MACHINE|MachineID={mid}|By={session.get('admin_name','admin')}"
        log_machine_event(event)
        flash("Machine deleted.", "info")
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting machine: {str(e)}", "error")
    finally:
        cursor.close(); conn.close()
    return redirect(url_for('view_machines'))

# -------------------------
# Performance routes (unchanged)
# -------------------------
@app.route('/performance')
def view_performance():
    update_oee_values()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.PerformanceID, m.MachineName, p.OperatingTime, p.Downtime,
               p.ActualOutput, p.IdealOutput, p.GoodUnits, p.TotalUnits, p.OEE
        FROM Performance_Data p
        LEFT JOIN Machine m ON p.MachineID = m.MachineID
    """)
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('performance.html', data=data, is_admin=session.get('is_admin', False))

@app.route('/add_performance', methods=['GET', 'POST'])
@admin_required
def add_performance():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MachineID, MachineName FROM Machine")
    machines = cursor.fetchall()
    if request.method == 'POST':
        mid = int(request.form['machine_id'])
        ot = float(request.form['operating_time'])
        down = float(request.form['downtime'])
        ao = int(request.form['actual_output'])
        io = int(request.form['ideal_output'])
        gu = int(request.form['good_units'])
        tu = int(request.form['total_units'])
        planned = ot + down
        availability = (ot / planned) if planned > 0 else 0
        performance = (ao / io) if io > 0 else 0
        quality = (gu / tu) if tu > 0 else 0
        oee = availability * performance * quality * 100
        cursor.execute("""
            INSERT INTO Performance_Data (MachineID, OperatingTime, Downtime, ActualOutput, IdealOutput, GoodUnits, TotalUnits, OEE)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (mid, ot, down, ao, io, gu, tu, oee))
        conn.commit()
        pid = cursor.lastrowid
        data_string = f"ADD_PERFORMANCE|PerformanceID={pid}|MachineID={mid}|OperatingTime={ot}|Downtime={down}|ActualOutput={ao}|IdealOutput={io}|GoodUnits={gu}|TotalUnits={tu}|OEE={oee}|By={session.get('admin_name','admin')}"
        add_block_to_chain(pid, data_string)
        cursor.close(); conn.close()
        flash("Performance entry added.", "success")
        return redirect(url_for('view_performance'))
    cursor.close(); conn.close()
    return render_template('add_performance.html', machines=machines, is_admin=True)

@app.route('/modify_performance/<int:pid>', methods=['GET', 'POST'])
@admin_required
def modify_performance(pid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT PerformanceID, MachineID, OperatingTime, Downtime, ActualOutput, IdealOutput, GoodUnits, TotalUnits
        FROM Performance_Data WHERE PerformanceID=%s
    """, (pid,))
    row = cursor.fetchone()
    if not row:
        cursor.close(); conn.close()
        flash("Performance record not found.", "error")
        return redirect(url_for('view_performance'))

    if request.method == 'POST':
        new_ot = float(request.form['operating_time'])
        new_down = float(request.form['downtime'])
        new_ao = int(request.form['actual_output'])
        new_io = int(request.form['ideal_output'])
        new_gu = int(request.form['good_units'])
        new_tu = int(request.form['total_units'])
        override = request.form.get('override_password', '')
        if override != MASTER_OVERRIDE:
            cursor.close(); conn.close()
            return render_template('modify_performance.html', data=row, message="❌ Wrong override password", is_admin=True)
        planned = new_ot + new_down
        availability = (new_ot / planned) if planned > 0 else 0
        performance = (new_ao / new_io) if new_io > 0 else 0
        quality = (new_gu / new_tu) if new_tu > 0 else 0
        oee = availability * performance * quality * 100
        cursor.execute("""
            UPDATE Performance_Data SET OperatingTime=%s, Downtime=%s, ActualOutput=%s, IdealOutput=%s, GoodUnits=%s, TotalUnits=%s, OEE=%s
            WHERE PerformanceID=%s
        """, (new_ot, new_down, new_ao, new_io, new_gu, new_tu, oee, pid))
        conn.commit()
        data_string = f"MODIFY_PERFORMANCE|PerformanceID={pid}|NewOperatingTime={new_ot}|NewDowntime={new_down}|NewActualOutput={new_ao}|NewIdealOutput={new_io}|NewGoodUnits={new_gu}|NewTotalUnits={new_tu}|NewOEE={oee}|By={session.get('admin_name','admin')}"
        add_block_to_chain(pid, data_string)
        cursor.close(); conn.close()
        flash("Performance updated.", "success")
        return redirect(url_for('view_performance'))

    cursor.close(); conn.close()
    return render_template('modify_performance.html', data=row, is_admin=True, message="")

# -------------------------
# Blockchain route (unchanged)
# -------------------------
@app.route('/blockchain')
def view_blockchain():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT BlockID, PerformanceID, Hash, PrevHash, Data, Timestamp
        FROM blockchain_log
        ORDER BY BlockID ASC
    """)
    blocks = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('blockchain.html', blocks=blocks, is_admin=session.get('is_admin', False))

# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
