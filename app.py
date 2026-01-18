"""
Steel Factory Management System - Flask App
Option A: ML runs ONLY via manual scan (/run_anomaly_scan). No ML inside /dashboard_data.
- Dashboard reads from anomaly_detection (read-only).
- run_ml_scan wipes anomaly_detection, re-inserts fresh results, and raises alerts/maintenance.
"""
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, send_file
import mysql.connector
import hashlib
import os
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime
import logging
from fpdf import FPDF
import io

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
DB_PASS = os.getenv("DB_PASS", "1A2b3c4@")
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
        if not session.get('user_id') or session.get('role') != 'admin':
            flash("Admin access required.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role = request.form['role']  # 'admin' or 'user'

        if role not in ('admin', 'user'):
            flash("Invalid role.", "error")
            return redirect(url_for('register'))

        pw_hash = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (Username, PasswordHash, Role)
                VALUES (%s, %s, %s)
            """, (username, pw_hash, role))
            conn.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("Username already exists.", "error")
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')


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
        cur.execute(
            """
            SELECT AlertID FROM Alerts
            WHERE MachineID=%s AND AlertMessage=%s AND Timestamp > DATE_SUB(NOW(), INTERVAL %s MINUTE)
            LIMIT 1
            """,
            (machine_id, message, dedupe_minutes),
        )
        if cur.fetchone():
            return False  # duplicate recently, skip insert

        cur.execute(
            """
            INSERT INTO Alerts (MachineID, AlertMessage, Severity)
            VALUES (%s, %s, %s)
            """,
            (machine_id, message, severity),
        )
        conn.commit()
        return True
    except Exception as e:
        logging.getLogger(__name__).warning("add_alert failed: %s", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

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
        cur.execute(
            """
            SELECT MaintenanceID FROM maintenance_log
            WHERE MachineID=%s AND IssueDescription=%s AND Status=%s
            LIMIT 1
            """,
            (machine_id, issue, status),
        )
        if cur.fetchone():
            return False

        cur.execute(
            """
            INSERT INTO maintenance_log (MachineID, IssueDescription, MaintenanceDate, Status)
            VALUES (%s, %s, NOW(), %s)
            """,
            (machine_id, issue, status),
        )
        conn.commit()
        return True
    except Exception as e:
        logging.getLogger(__name__).warning("add_maintenance failed: %s", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# -------------------------
# Blockchain helpers
# -------------------------
def add_block_to_chain(performance_id, data_string):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Hash FROM blockchain_log ORDER BY BlockID DESC LIMIT 1")
        last = cursor.fetchone()
        prev_hash = last[0] if last else "0"
        new_hash = generate_hash(data_string + prev_hash)
        cursor.execute(
            """
            INSERT INTO blockchain_log (PerformanceID, Hash, PrevHash, Data)
            VALUES (%s, %s, %s, %s)
            """,
            (performance_id, new_hash, prev_hash, data_string),
        )
        conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning("add_block_to_chain failed: %s", e)
        try:
            conn.rollback()
        except Exception:
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
        cursor.execute(
            """
            INSERT INTO blockchain_log (PerformanceID, Hash, PrevHash, Data)
            VALUES (%s, %s, %s, %s)
            """,
            (None, new_hash, prev_hash, data_string),
        )
        conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning("log_machine_event failed: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        cursor.close()
        conn.close()

# -------------------------
# OEE update helper
# -------------------------
def update_oee_values():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT PerformanceID, OperatingTime, Downtime, ActualOutput, IdealOutput, GoodUnits, TotalUnits
            FROM Performance_Data
            """
        )
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

            cursor.execute(
                "UPDATE Performance_Data SET OEE=%s WHERE PerformanceID=%s",
                (oee, pid),
            )
        conn.commit()
    except Exception as e:
        logging.getLogger(__name__).warning("update_oee_values failed: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        cursor.close()
        conn.close()


# -------------------------
# Report helpers
# -------------------------
def fetch_report_extras(machine_ids):
    """Fetch predictive anomalies, alerts, and maintenance for selected machines."""
    if not machine_ids:
        return [], [], []

    placeholders = ','.join(['%s'] * len(machine_ids))
    params = tuple(machine_ids)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Machine info map
        cursor.execute(
            f"""
            SELECT MachineID, MachineName, Location
            FROM Machine
            WHERE MachineID IN ({placeholders})
            """,
            params,
        )
        machine_info = {}
        for mid, name, loc in cursor.fetchall():
            machine_info[mid] = {
                'name': name,
                'location': loc if loc not in (None, '') else 'N/A'
            }

        # Predictive anomalies (latest per machine)
        cursor.execute(
            f"""
            SELECT a.MachineID, m.MachineName, m.Location, a.AnomalyScore, a.Timestamp
            FROM anomaly_detection a
            JOIN Machine m ON a.MachineID = m.MachineID
            WHERE a.IsAnomaly = 1 AND a.MachineID IN ({placeholders})
            ORDER BY a.Timestamp DESC
            """,
            params,
        )
        anomalies = []
        seen_machines = set()
        for mid, name, loc, score, ts in cursor.fetchall():
            if mid in seen_machines:
                continue
            seen_machines.add(mid)
            severity = 'HIGH' if float(score) < -0.25 else 'MEDIUM' if float(score) < -0.15 else 'LOW'
            anomalies.append({
                'machine': name,
                'location': loc if loc not in (None, '') else 'N/A',
                'score': round(float(score), 3),
                'severity': severity,
                'time': ts.strftime('%Y-%m-%d %H:%M') if ts else ''
            })

        # Recent alerts (latest per machine)
        cursor.execute(
            f"""
            SELECT al.MachineID, m.MachineName, m.Location, al.AlertMessage, al.Severity, al.Timestamp
            FROM Alerts al
            JOIN Machine m ON al.MachineID = m.MachineID
            WHERE al.MachineID IN ({placeholders})
            ORDER BY al.Timestamp DESC
            """,
            params,
        )
        alerts = []
        seen_alerts = set()
        for mid, name, loc, msg, severity, ts in cursor.fetchall():
            if mid in seen_alerts:
                continue
            seen_alerts.add(mid)
            alerts.append({
                'machine': name,
                'location': loc if loc not in (None, '') else 'N/A',
                'message': msg,
                'severity': severity if severity else 'MEDIUM',
                'time': ts.strftime('%Y-%m-%d %H:%M') if ts else ''
            })

        # Maintenance logs (active/pending latest per machine)
        cursor.execute(
            f"""
            SELECT ml.MachineID, m.MachineName, m.Location, ml.IssueDescription, ml.Status, ml.MaintenanceDate
            FROM maintenance_log ml
            JOIN Machine m ON ml.MachineID = m.MachineID
            WHERE ml.MachineID IN ({placeholders}) AND ml.Status IN ('PENDING', 'ACTIVE')
            ORDER BY ml.MaintenanceDate DESC
            """,
            params,
        )
        maintenance = []
        seen_maint = set()
        for mid, name, loc, issue, status, dt in cursor.fetchall():
            if mid in seen_maint:
                continue
            seen_maint.add(mid)
            maintenance.append({
                'machine': name,
                'location': loc if loc not in (None, '') else 'N/A',
                'issue': issue,
                'status': status,
                'date': dt.strftime('%Y-%m-%d %H:%M') if dt else ''
            })

        return anomalies, alerts, maintenance
    finally:
        cursor.close()
        conn.close()

# -------------------------
# ML scan helper (manual trigger only)
# -------------------------
def run_ml_scan():
    """
    Runs IsolationForest on Performance_Data,
    refreshes anomaly_detection table,
    and creates Alerts + Maintenance for true anomalies.

    Features used: [OEE, Downtime, ActualOutput]
    """
    if not ML_AVAILABLE:
        logging.getLogger(__name__).warning("ML not available, skipping scan.")
        return 0, 0  # total rows, anomaly count

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1) Load performance data
        cursor.execute(
            """
            SELECT PerformanceID, MachineID, OEE, Downtime, ActualOutput
            FROM Performance_Data
            ORDER BY PerformanceID ASC
            """
        )
        rows = cursor.fetchall()

        if not rows:
            return 0, 0

        perf_ids = []
        machine_ids = []
        features = []

        for pid, mid, oee, down, actual in rows:
            oee = float(oee or 0.0)
            down = float(down or 0.0)
            actual = int(actual or 0)

            perf_ids.append(pid)
            machine_ids.append(mid)
            features.append([oee, down, actual])

        # Too few rows → no ML
        if len(features) < 5:
            logging.getLogger(__name__).info("Not enough rows for ML scan.")
            return len(features), 0

        X = np.array(features, dtype=float)

        contamination = 0.10 if len(X) >= 20 else 0.20
        iso = IsolationForest(contamination=contamination, random_state=42)
        preds = iso.fit_predict(X)        # -1 = anomaly, 1 = normal
        scores = iso.decision_function(X) # lower = more anomalous

        # 2) Refresh anomaly_detection table with latest scan only
        cursor.execute("DELETE FROM anomaly_detection")
        conn.commit()

        anomaly_count = 0

        for i, pid in enumerate(perf_ids):
            mid = machine_ids[i]
            score = float(scores[i])
            is_anom = 1 if preds[i] == -1 else 0

            cursor.execute(
                """
                INSERT INTO anomaly_detection (MachineID, PerformanceID, AnomalyScore, IsAnomaly, Timestamp)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (mid, pid, score, is_anom),
            )

            # For *true* anomalies, also create Alerts + Maintenance
            if is_anom:
                anomaly_count += 1

                # Machine name for prettier messages
                try:
                    c2 = conn.cursor()
                    c2.execute(
                        "SELECT MachineName FROM Machine WHERE MachineID=%s",
                        (mid,),
                    )
                    r = c2.fetchone()
                    mname = r[0] if r and r[0] else f"Machine {mid}"
                    c2.close()
                except Exception:
                    mname = f"Machine {mid}"

                severity = "HIGH" if score < -0.25 else "MEDIUM"
                msg = f"{mname}: ML anomaly detected (score {score:.3f})"

                try:
                    add_alert(mid, msg, severity=severity, dedupe_minutes=60)
                except Exception as e:
                    logging.getLogger(__name__).warning("add_alert from scan failed: %s", e)

                if severity == "HIGH":
                    try:
                        add_maintenance(mid, f"{mname}: Predicted failure risk - HIGH")
                    except Exception as e:
                        logging.getLogger(__name__).warning("add_maintenance from scan failed: %s", e)

        conn.commit()
        logging.getLogger(__name__).info(
            "ML scan complete: %d rows, %d anomalies", len(features), anomaly_count
        )
        return len(features), anomaly_count

    except Exception as e:
        logging.getLogger(__name__).warning("run_ml_scan error: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass
        return 0, 0
    finally:
        cursor.close()
        conn.close()

# -------------------------
# Auth routes
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT UserID, PasswordHash, Role
            FROM users
            WHERE Username=%s
        """, (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))


# -------------------------
# Dashboard routes + data
# -------------------------
@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', is_admin=(session.get('role') == 'admin'))


@app.route('/dashboard_data')
def dashboard_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ensure OEE updated
    update_oee_values()

    # 1) OEE trend + per-row metrics
    try:
        cursor.execute(
            """
            SELECT PerformanceID, MachineID, OperatingTime, Downtime,
                   ActualOutput, IdealOutput, GoodUnits, TotalUnits, OEE
            FROM Performance_Data
            ORDER BY PerformanceID ASC
            """
        )
        perf_rows_full = cursor.fetchall()
    except Exception as e:
        logging.getLogger(__name__).warning("Perf full fetch failed: %s", e)
        perf_rows_full = []

    oee_labels = []
    oee_values = []
    availability_values = []
    performance_values = []
    quality_values = []

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

    # 2) Machine summary
    try:
        cursor.execute(
            """
            SELECT m.MachineID, m.MachineName,
                   AVG(p.OEE) as avg_oee,
                   SUM(p.Downtime) as total_downtime,
                   AVG(CASE WHEN p.TotalUnits>0 THEN p.GoodUnits/p.TotalUnits ELSE 0 END) * 100 as avg_quality
            FROM Machine m
            LEFT JOIN Performance_Data p ON m.MachineID = p.MachineID
            GROUP BY m.MachineID
            """
        )
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
        machines_health.append(
            {
                "id": mid,
                "name": name,
                "oee": round(avg_oee, 2),
                "downtime": round(downtime, 2),
                "quality": round(avg_quality, 2),
                "status": "healthy"
                if avg_oee >= 85
                else "warning"
                if avg_oee >= 70
                else "critical",
            }
        )

    factory_avg_oee = (sum(all_oee) / len(all_oee)) if all_oee else 0.0
    factory_status = (
        "healthy" if factory_avg_oee >= 85 else "warning" if factory_avg_oee >= 70 else "critical"
    )

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
        cursor.execute(
            """
            SELECT a.AlertID, a.MachineID, a.AlertMessage, m.MachineName, a.Severity, a.Timestamp
            FROM Alerts a
            LEFT JOIN Machine m ON a.MachineID = m.MachineID
            ORDER BY a.Timestamp DESC
            LIMIT 50
            """
        )
        ar = cursor.fetchall()
        for row in ar:
            aid, mid, msg, mname, sev, ts = row
            recent_alerts.append(
                {
                    "id": aid,
                    "machine_id": mid,
                    "machine": mname or f"Machine-{mid}",
                    "message": msg,
                    "severity": sev or "MEDIUM",
                    "time": ts.strftime("%Y-%m-%d %H:%M:%S") if ts else "",
                }
            )
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

    # 5) Simple anomalies (top low OEE rows) - fallback only (not ML)
    anomalies = []
    try:
        cursor.execute(
            """
            SELECT p.PerformanceID, m.MachineName, p.OEE
            FROM Performance_Data p
            LEFT JOIN Machine m ON p.MachineID = m.MachineID
            ORDER BY p.OEE ASC LIMIT 3
            """
        )
        low_rows = cursor.fetchall()
        for lr in low_rows:
            anomalies.append(
                {
                    "machine": lr[1] or "Unknown",
                    "issue": "Low OEE detected",
                    "recommendation": "Schedule inspection",
                }
            )
    except Exception:
        anomalies = []

    # 6) Load latest ML anomalies from anomaly_detection table (read-only)
    ml_anomalies = []
    try:
        cursor.execute("""
            SELECT a.MachineID,
                m.MachineName,
                a.PerformanceID,
                a.AnomalyScore,
                a.Timestamp
            FROM anomaly_detection a
            JOIN (
                SELECT MachineID, MAX(Timestamp) AS latest_ts
                FROM anomaly_detection
                WHERE IsAnomaly = 1
                GROUP BY MachineID
            ) latest
            ON a.MachineID = latest.MachineID
            AND a.Timestamp = latest.latest_ts
            LEFT JOIN Machine m ON a.MachineID = m.MachineID
            WHERE a.IsAnomaly = 1
            ORDER BY a.Timestamp DESC
        """)
        rows = cursor.fetchall()
        for r in rows:
            mid, mname, pid, score, ts = r
            mname = mname or f"Machine {mid}"
            severity = "HIGH" if float(score) < -0.25 else "MEDIUM"
            ml_anomalies.append(
                {
                    "machine": mname,
                    "issue": f"ML anomaly detected (score {float(score):.3f})",
                    "severity": severity,
                    "score": round(float(score), 3),
                    "time": ts.strftime("%Y-%m-%d %H:%M:%S") if ts else "",
                }
            )
    except Exception as e:
        logging.getLogger(__name__).warning("Fetch ml anomalies failed: %s", e)
        ml_anomalies = []

    # dedupe ml anomalies by machine (keep latest)
    dedup_ml = {}
    for a in ml_anomalies:
        dedup_ml[a["machine"]] = a
    ml_final = list(dedup_ml.values())

    # 7) Maintenance list for dashboard (pending) - dedupe by machine name
    maintenance = []
    try:
        cursor.execute(
            """
            SELECT ml.MaintenanceID, ml.MachineID, ml.IssueDescription, ml.MaintenanceDate, ml.Status, m.MachineName
            FROM maintenance_log ml
            LEFT JOIN Machine m ON ml.MachineID = m.MachineID
            WHERE ml.Status IN ('PENDING','SCHEDULED')
            ORDER BY ml.MaintenanceDate DESC
            LIMIT 50
            """
        )
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
                    "status": mr[4],
                }
        maintenance = list(seen_maint.values())
    except Exception as e:
        logging.getLogger(__name__).warning("Fetch maintenance failed: %s", e)
        maintenance = []

    # close cursor/connection
    try:
        cursor.close()
        conn.close()
    except Exception:
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
        "ml_anomalies": ml_final,          # ML anomalies from anomaly_detection (deduped)
        "recent_alerts": deduped_alerts,   # deduped alerts
        "maintenance": maintenance,        # deduped maintenance entries
    }

    return jsonify(payload)

# -------------------------
# Machines routes
# -------------------------
@app.route('/machines')
@login_required
def view_machines():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MachineID, MachineName, MachineType, Location, Status FROM Machine")
    machines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('machines.html', machines=machines, is_admin=(session.get('role') == 'admin')
)


@app.route('/add_machine', methods=['GET', 'POST'])

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
            cursor.execute(
                """
                INSERT INTO Machine (MachineName, MachineType, Location, Status)
                VALUES (%s, %s, %s, %s)
                """,
                (name, mtype, location, status),
            )
            conn.commit()
            new_mid = cursor.lastrowid
            message = f"✅ Machine '{name}' added successfully!"
            event = (
                f"ADD_MACHINE|MachineID={new_mid}|Name={name}|Type={mtype}|"
                f"Loc={location}|Status={status}"
            )
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
    cursor.execute(
        "SELECT MachineID, MachineName, MachineType, Location, Status FROM Machine WHERE MachineID=%s",
        (mid,),
    )
    machine = cursor.fetchone()
    if not machine:
        cursor.close()
        conn.close()
        flash("Machine not found.", "error")
        return redirect(url_for('view_machines'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        mtype = request.form['type'].strip()
        location = request.form['location'].strip()
        status = request.form['status']
        override = request.form.get('override_password', '')
        if override != MASTER_OVERRIDE:
            cursor.close()
            conn.close()
            return render_template(
                'modify_machine.html',
                machine=machine,
                message="❌ Wrong override password",
                is_admin=True,
            )
        cursor.execute(
            """
            UPDATE Machine SET MachineName=%s, MachineType=%s, Location=%s, Status=%s
            WHERE MachineID=%s
            """,
            (name, mtype, location, status, mid),
        )
        conn.commit()
        event = (
            f"MODIFY_MACHINE|MachineID={mid}|NewName={name}|NewType={mtype}|"
            f"NewLocation={location}|NewStatus={status}"
        )
        log_machine_event(event)
        cursor.close()
        conn.close()
        flash("Machine updated.", "success")
        return redirect(url_for('view_machines'))

    cursor.close()
    conn.close()
    return render_template(
        'modify_machine.html', machine=machine, message="", is_admin=True
    )

# Safe delete with FK cleanup
def safe_delete_machine(mid, admin_name="admin"):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1. Delete anomaly logs
        cur.execute(
            """
            DELETE FROM anomaly_detection
            WHERE PerformanceID IN (
                SELECT PerformanceID FROM Performance_Data WHERE MachineID=%s
            )
            """,
            (mid,),
        )

        # 2. Delete alerts
        cur.execute("DELETE FROM Alerts WHERE MachineID=%s", (mid,))

        # 3. Delete maintenance logs
        cur.execute("DELETE FROM Maintenance_Log WHERE MachineID=%s", (mid,))

        # 4. Delete blockchain logs linked to performance records
        cur.execute(
            """
            DELETE FROM blockchain_log
            WHERE PerformanceID IN (
                SELECT PerformanceID FROM Performance_Data WHERE MachineID=%s
            )
            """,
            (mid,),
        )

        # 5. Delete performance rows
        cur.execute("DELETE FROM Performance_Data WHERE MachineID=%s", (mid,))

        # 6. Finally delete the machine
        cur.execute("DELETE FROM Machine WHERE MachineID=%s", (mid,))

        conn.commit()

        # 7. Log blockchain event
        event = f"DELETE_MACHINE|MachineID={mid}|By={admin_name}"
        log_machine_event(event)

        return True

    except Exception as e:
        conn.rollback()
        print("SAFE DELETE FAILED:", e)
        return False

    finally:
        cur.close()
        conn.close()


@app.route('/delete_machine/<int:mid>', methods=['POST'])
@admin_required
def delete_machine(mid):
    ok = safe_delete_machine(mid, admin_name=session.get("admin_name", "admin"))

    if ok:
        flash("Machine deleted safely.", "info")
    else:
        flash("Failed to delete machine.", "error")


    return redirect(url_for('view_machines'))

# -------------------------
# Performance routes
# -------------------------
@app.route('/performance')
@login_required
def view_performance():
    update_oee_values()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.PerformanceID, m.MachineName, p.OperatingTime, p.Downtime,
               p.ActualOutput, p.IdealOutput, p.GoodUnits, p.TotalUnits, p.OEE
        FROM Performance_Data p
        LEFT JOIN Machine m ON p.MachineID = m.MachineID
        """
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        'performance.html', data=data, is_admin=(session.get('role') == 'admin'))
    


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
        cursor.execute(
            """
            INSERT INTO Performance_Data
            (MachineID, OperatingTime, Downtime, ActualOutput, IdealOutput, GoodUnits, TotalUnits, OEE)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (mid, ot, down, ao, io, gu, tu, oee),
        )
        conn.commit()
        pid = cursor.lastrowid
        data_string = (
            f"ADD_PERFORMANCE|PerformanceID={pid}|MachineID={mid}|OperatingTime={ot}|"
            f"Downtime={down}|ActualOutput={ao}|IdealOutput={io}|GoodUnits={gu}|"
            f"TotalUnits={tu}|OEE={oee}|By={session.get('admin_name','admin')}"
        )
        add_block_to_chain(pid, data_string)
        cursor.close()
        conn.close()
        flash("Performance entry added.", "success")
        return redirect(url_for('view_performance'))
    cursor.close()
    conn.close()
    return render_template('add_performance.html', machines=machines, is_admin=True)


@app.route('/modify_performance/<int:pid>', methods=['GET', 'POST'])
@admin_required
def modify_performance(pid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT PerformanceID, MachineID, OperatingTime, Downtime, ActualOutput,
               IdealOutput, GoodUnits, TotalUnits
        FROM Performance_Data WHERE PerformanceID=%s
        """,
        (pid,),
    )
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
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
            cursor.close()
            conn.close()
            return render_template(
                'modify_performance.html',
                data=row,
                message="❌ Wrong override password",
                is_admin=True,
            )
        planned = new_ot + new_down
        availability = (new_ot / planned) if planned > 0 else 0
        performance = (new_ao / new_io) if new_io > 0 else 0
        quality = (new_gu / new_tu) if new_tu > 0 else 0
        oee = availability * performance * quality * 100
        cursor.execute(
            """
            UPDATE Performance_Data
            SET OperatingTime=%s, Downtime=%s, ActualOutput=%s, IdealOutput=%s,
                GoodUnits=%s, TotalUnits=%s, OEE=%s
            WHERE PerformanceID=%s
            """,
            (new_ot, new_down, new_ao, new_io, new_gu, new_tu, oee, pid),
        )
        conn.commit()
        data_string = (
            f"MODIFY_PERFORMANCE|PerformanceID={pid}|NewOperatingTime={new_ot}|"
            f"NewDowntime={new_down}|NewActualOutput={new_ao}|NewIdealOutput={new_io}|"
            f"NewGoodUnits={new_gu}|NewTotalUnits={new_tu}|NewOEE={oee}|"
            f"By={session.get('admin_name','admin')}"
        )
        add_block_to_chain(pid, data_string)
        cursor.close()
        conn.close()
        flash("Performance updated.", "success")
        return redirect(url_for('view_performance'))

    cursor.close()
    conn.close()
    return render_template('modify_performance.html', data=row, is_admin=True, message="")

# -------------------------
# Weekly Performance Report routes
# -------------------------
@app.route('/performance/report', methods=['GET', 'POST'])
@login_required
def performance_report():
    """
    GET: Show report generation form with machine and metric checkboxes
    POST: Generate report and redirect to view
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all machines
    cursor.execute("SELECT MachineID, MachineName FROM Machine ORDER BY MachineName")
    machines = cursor.fetchall()
    
    if request.method == 'POST':
        # Get selected machines and metrics
        machine_ids = request.form.getlist('machine_ids')
        selected_metrics = request.form.getlist('metrics')
        
        if not machine_ids:
            flash("Please select at least one machine.", "error")
            cursor.close()
            conn.close()
            return render_template('performance_report.html', machines=machines)
        
        if not selected_metrics:
            flash("Please select at least one metric.", "error")
            cursor.close()
            conn.close()
            return render_template('performance_report.html', machines=machines)
        
        # Convert to integers
        machine_ids = [int(mid) for mid in machine_ids]
        
        # Build report data
        report_data = []
        
        for machine_id in machine_ids:
            # Get machine name
            cursor.execute("SELECT MachineName FROM Machine WHERE MachineID=%s", (machine_id,))
            machine_row = cursor.fetchone()
            machine_name = machine_row[0] if machine_row else f"Machine {machine_id}"
            
            # Fetch recent performance records (using PerformanceID as recency proxy)
            # Fetch last 100 records for this machine to get recent data
            cursor.execute("""
                SELECT 
                    p.OEE,
                    p.OperatingTime,
                    p.Downtime,
                    p.ActualOutput,
                    p.IdealOutput,
                    p.GoodUnits,
                    p.TotalUnits
                FROM Performance_Data p
                WHERE p.MachineID = %s
                ORDER BY p.PerformanceID DESC
                LIMIT 100
            """, (machine_id,))
            
            performance_records = cursor.fetchall()
            
            # Calculate aggregates in Python
            if performance_records:
                oee_values = []
                availability_values = []
                performance_values = []
                quality_values = []
                downtime_total = 0
                
                for record in performance_records:
                    oee = float(record[0] or 0)
                    operating_time = float(record[1] or 0)
                    downtime = float(record[2] or 0)
                    actual_output = float(record[3] or 0)
                    ideal_output = float(record[4] or 0)
                    good_units = float(record[5] or 0)
                    total_units = float(record[6] or 0)
                    
                    oee_values.append(oee)
                    
                    # Calculate availability
                    planned = operating_time + downtime
                    if planned > 0:
                        availability_values.append((operating_time / planned) * 100)
                    
                    # Calculate performance
                    if ideal_output > 0:
                        performance_values.append((actual_output / ideal_output) * 100)
                    
                    # Calculate quality
                    if total_units > 0:
                        quality_values.append((good_units / total_units) * 100)
                    
                    downtime_total += downtime
                
                avg_oee = round(sum(oee_values) / len(oee_values), 2) if oee_values else 0
                avg_availability = round(sum(availability_values) / len(availability_values), 2) if availability_values else 0
                avg_performance = round(sum(performance_values) / len(performance_values), 2) if performance_values else 0
                avg_quality = round(sum(quality_values) / len(quality_values), 2) if quality_values else 0
                total_downtime = round(downtime_total, 2)
            else:
                avg_oee = avg_availability = avg_performance = avg_quality = total_downtime = 0
            
            # Fetch recent anomalies for this machine
            cursor.execute("""
                SELECT AnomalyScore, Timestamp
                FROM anomaly_detection
                WHERE MachineID = %s
                  AND Timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY Timestamp DESC
                LIMIT 5
            """, (machine_id,))
            
            anomalies = []
            for anom_row in cursor.fetchall():
                score = float(anom_row[0])
                timestamp = anom_row[1].strftime("%Y-%m-%d %H:%M") if anom_row[1] else "N/A"
                severity = "HIGH" if score < -0.25 else "MEDIUM" if score < -0.1 else "LOW"
                anomalies.append({
                    'score': round(score, 3),
                    'timestamp': timestamp,
                    'severity': severity
                })
            
            # Check for pending maintenance
            cursor.execute("""
                SELECT IssueDescription
                FROM maintenance_log
                WHERE MachineID = %s AND Status = 'PENDING'
                ORDER BY MaintenanceDate DESC
                LIMIT 1
            """, (machine_id,))
            
            maintenance_row = cursor.fetchone()
            maintenance_reminder = maintenance_row[0] if maintenance_row else None
            
            # Build machine report
            machine_report = {
                'machine_id': machine_id,
                'machine_name': machine_name,
                'avg_oee': avg_oee,
                'avg_availability': avg_availability,
                'avg_performance': avg_performance,
                'avg_quality': avg_quality,
                'total_downtime': total_downtime,
                'anomalies': anomalies,
                'maintenance_reminder': maintenance_reminder
            }
            
            report_data.append(machine_report)
        
        # Store report in session for PDF export
        session['report_data'] = report_data
        session['selected_metrics'] = selected_metrics
        session['selected_machine_ids'] = machine_ids
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('performance_report_view'))
    
    cursor.close()
    conn.close()
    return render_template('performance_report.html', machines=machines)


@app.route('/performance/report/view')
@login_required
def performance_report_view():
    """Display the generated report"""
    report_data = session.get('report_data', [])
    selected_metrics = session.get('selected_metrics', [])
    selected_machine_ids = session.get('selected_machine_ids', [])
    
    if not report_data:
        flash("No report data available. Please generate a report first.", "error")
        return redirect(url_for('performance_report'))

    # Fallback: derive machine ids from report data if not in session
    if not selected_machine_ids:
        selected_machine_ids = [item.get('machine_id') for item in report_data if item.get('machine_id')]
    
    # Fetch extra report context (anomalies, alerts, maintenance)
    report_anomalies, report_alerts, report_maintenance = fetch_report_extras(selected_machine_ids)
    
    # Generate timestamp for report display
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('report_view.html', 
                         report_data=report_data, 
                         selected_metrics=selected_metrics,
                         report_anomalies=report_anomalies,
                         report_alerts=report_alerts,
                         report_maintenance=report_maintenance,
                         generated_at=generated_at,
                         is_admin=(session.get('role') == 'admin'))


@app.route('/performance/report/pdf')
@login_required
def performance_report_pdf():
    """Generate and download PDF report"""
    report_data = session.get('report_data', [])
    selected_metrics = session.get('selected_metrics', [])
    selected_machine_ids = session.get('selected_machine_ids', [])
    
    if not report_data:
        flash("No report data available. Please generate a report first.", "error")
        return redirect(url_for('performance_report'))

    if not selected_machine_ids:
        selected_machine_ids = [item.get('machine_id') for item in report_data if item.get('machine_id')]

    report_anomalies, report_alerts, report_maintenance = fetch_report_extras(selected_machine_ids)
    
    report_anomalies, report_alerts, report_maintenance = fetch_report_extras(selected_machine_ids)
    
    # Create PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Weekly Performance Report", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)
    
    # Iterate through each machine
    for machine_data in report_data:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Machine: {machine_data['machine_name']}", ln=True)
        pdf.ln(2)
        
        # Metrics table
        pdf.set_font("Arial", "B", 10)
        pdf.cell(50, 8, "Metric", border=1)
        pdf.cell(50, 8, "Value", border=1)
        pdf.ln()
        
        pdf.set_font("Arial", "", 10)
        
        if 'oee' in selected_metrics:
            pdf.cell(50, 8, "Avg OEE (%)", border=1)
            pdf.cell(50, 8, str(machine_data['avg_oee']), border=1)
            pdf.ln()
        
        if 'availability' in selected_metrics:
            pdf.cell(50, 8, "Avg Availability (%)", border=1)
            pdf.cell(50, 8, str(machine_data['avg_availability']), border=1)
            pdf.ln()
        
        if 'performance' in selected_metrics:
            pdf.cell(50, 8, "Avg Performance (%)", border=1)
            pdf.cell(50, 8, str(machine_data['avg_performance']), border=1)
            pdf.ln()
        
        if 'quality' in selected_metrics:
            pdf.cell(50, 8, "Avg Quality (%)", border=1)
            pdf.cell(50, 8, str(machine_data['avg_quality']), border=1)
            pdf.ln()
        
        if 'downtime' in selected_metrics:
            pdf.cell(50, 8, "Total Downtime (hrs)", border=1)
            pdf.cell(50, 8, str(machine_data['total_downtime']), border=1)
            pdf.ln()
        
        pdf.ln(3)
        
        # Anomalies
        if machine_data['anomalies']:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, "Recent Anomalies:", ln=True)
            pdf.set_font("Arial", "", 9)
            
            for anom in machine_data['anomalies']:
                pdf.cell(0, 6, f"  - Score: {anom['score']}, Severity: {anom['severity']}, Time: {anom['timestamp']}", ln=True)
            pdf.ln(2)
        
        # Maintenance reminder
        if machine_data['maintenance_reminder']:
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 8, "Maintenance Required:", ln=True)
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, f"  {machine_data['maintenance_reminder']}")
            pdf.ln(2)
        
        pdf.ln(5)

    # Predictive Anomalies section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Predictive Anomalies", ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 8, "Machine", border=1)
    pdf.cell(40, 8, "Location", border=1)
    pdf.cell(35, 8, "Anomaly Score", border=1)
    pdf.cell(30, 8, "Severity", border=1)
    pdf.cell(45, 8, "Time", border=1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    if report_anomalies:
        for row in report_anomalies:
            pdf.cell(40, 8, row['machine'], border=1)
            pdf.cell(40, 8, row['location'], border=1)
            pdf.cell(35, 8, str(row['score']), border=1)
            pdf.cell(30, 8, row['severity'], border=1)
            pdf.cell(45, 8, row['time'], border=1)
            pdf.ln()
    else:
        pdf.cell(0, 8, "None detected for selected machines", border=1, ln=True)
    pdf.ln(5)

    # Recent Alerts section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Recent Alerts", ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 8, "Machine", border=1)
    pdf.cell(40, 8, "Location", border=1)
    pdf.cell(50, 8, "Alert Message", border=1)
    pdf.cell(25, 8, "Severity", border=1)
    pdf.cell(35, 8, "Time", border=1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    if report_alerts:
        for row in report_alerts:
            pdf.cell(40, 8, row['machine'], border=1)
            pdf.cell(40, 8, row['location'], border=1)
            pdf.cell(50, 8, row['message'][:30] if row['message'] else '', border=1)
            pdf.cell(25, 8, row['severity'], border=1)
            pdf.cell(35, 8, row['time'], border=1)
            pdf.ln()
    else:
        pdf.cell(0, 8, "None detected for selected machines", border=1, ln=True)
    pdf.ln(5)

    # Maintenance Logs section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Maintenance Logs", ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 8, "Machine", border=1)
    pdf.cell(40, 8, "Location", border=1)
    pdf.cell(55, 8, "Issue", border=1)
    pdf.cell(25, 8, "Status", border=1)
    pdf.cell(30, 8, "Date", border=1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    if report_maintenance:
        for row in report_maintenance:
            pdf.cell(40, 8, row['machine'], border=1)
            pdf.cell(40, 8, row['location'], border=1)
            pdf.cell(55, 8, row['issue'][:35] if row['issue'] else '', border=1)
            pdf.cell(25, 8, row['status'], border=1)
            pdf.cell(30, 8, row['date'], border=1)
            pdf.ln()
    else:
        pdf.cell(0, 8, "None detected for selected machines", border=1, ln=True)
    pdf.ln(5)
    
    # Output PDF to bytes
    pdf_output = pdf.output(dest='S').encode('latin-1')
    pdf_bytes = io.BytesIO(pdf_output)
    pdf_bytes.seek(0)
    
    filename = f"weekly_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        pdf_bytes,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

# -------------------------
# Blockchain route
# -------------------------
@app.route('/blockchain')
@login_required
def view_blockchain():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT BlockID, PerformanceID, Hash, PrevHash, Data, Timestamp
        FROM blockchain_log
        ORDER BY BlockID ASC
        """
    )
    blocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        'blockchain.html', blocks=blocks, is_admin=(session.get('role') == 'admin')

    )

# -------------------------
# Anomalies routes
# -------------------------
@app.route('/run_anomaly_scan', methods=['POST'])
@admin_required
def run_anomaly_scan_route():
    total, anomalies = run_ml_scan()
    flash(
        f"Anomaly scan completed on {total} records. Detected {anomalies} anomalies.",
        "info",
    )
    return redirect(url_for('view_anomalies'))


@app.route('/anomalies')
def view_anomalies():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            a.AnomalyID,
            m.MachineName,
            a.MachineID,
            a.PerformanceID,
            a.AnomalyScore,
            a.IsAnomaly,
            a.Timestamp
        FROM anomaly_detection a
        LEFT JOIN Machine m ON a.MachineID = m.MachineID
        ORDER BY a.Timestamp DESC
        LIMIT 200
        """
    )
    rows = cursor.fetchall()

    anomalies = []
    for r in rows:
        anomalies.append(
            {
                "id": r[0],
                "machine": r[1] if r[1] else f"Machine {r[2]}",
                "machine_id": r[2],
                "performance_id": r[3],
                "score": float(r[4]),
                "severity": "HIGH" if float(r[4]) < -0.25 else "MEDIUM",
                "is_anomaly": r[5],
                "time": r[6].strftime("%Y-%m-%d %H:%M:%S") if r[6] else "",
            }
        )

    cursor.close()
    conn.close()
    return render_template(
        'anomalies.html', anomalies=anomalies, is_admin=session.get("is_admin", False)
    )

# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
