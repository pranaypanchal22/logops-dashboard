from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
from .db import get_db

bp = Blueprint("main", __name__)

VALID_LEVELS = {"INFO", "WARN", "ERROR"}

@bp.get("/health")
def health():
    return jsonify(status="ok")

@bp.post("/api/logs")
def ingest_logs():
    data = request.get_json(silent=True) or {}
    level = (data.get("level") or "").upper()
    service = (data.get("service") or "").strip()
    message = (data.get("message") or "").strip()
    timestamp = data.get("timestamp") or datetime.utcnow().isoformat()

    if level not in VALID_LEVELS:
        return jsonify(error="Invalid level. Use INFO/WARN/ERROR"), 400
    if not service or not message:
        return jsonify(error="service and message are required"), 400

    db = get_db()
    db.execute(
        "INSERT INTO logs (timestamp, level, service, message) VALUES (?, ?, ?, ?)",
        (timestamp, level, service, message),
    )
    db.commit()

    return jsonify(status="ingested")

@bp.get("/api/stats")
def stats():
    minutes = int(request.args.get("minutes", 15))
    since = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()

    db = get_db()

    errors_last_window = db.execute(
        "SELECT COUNT(*) AS c FROM logs WHERE level='ERROR' AND timestamp >= ?",
        (since,),
    ).fetchone()["c"]

    top_services = db.execute(
        """
        SELECT service, COUNT(*) AS c
        FROM logs
        WHERE level='ERROR' AND timestamp >= ?
        GROUP BY service
        ORDER BY c DESC
        LIMIT 5
        """,
        (since,),
    ).fetchall()

    recent_errors = db.execute(
        """
        SELECT id, timestamp, level, service, message
        FROM logs
        WHERE level='ERROR'
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

    return jsonify(
        window_minutes=minutes,
        errors_last_window=errors_last_window,
        top_services=[dict(r) for r in top_services],
        recent_errors=[dict(r) for r in recent_errors],
    )

@bp.get("/")
def home():
    return render_template("dashboard.html")

@bp.get("/dashboard")
def dashboard():
    # filters
    level = (request.args.get("level") or "").upper().strip()
    service = (request.args.get("service") or "").strip()
    q = (request.args.get("q") or "").strip()
    minutes = int(request.args.get("minutes", 15))

    since_dt = datetime.utcnow() - timedelta(minutes=minutes)
    since = since_dt.isoformat()

    where = []
    params = []

    if level in VALID_LEVELS:
        where.append("level = ?")
        params.append(level)

    if service:
        where.append("service = ?")
        params.append(service)

    if q:
        where.append("message LIKE ?")
        params.append(f"%{q}%")

    where.append("timestamp >= ?")
    params.append(since)

    where_sql = " AND ".join(where)

    db = get_db()

    errors_last_window = db.execute(
        "SELECT COUNT(*) AS c FROM logs WHERE level='ERROR' AND timestamp >= ?",
        (since,),
    ).fetchone()["c"]

    top_services = db.execute(
        """
        SELECT service, COUNT(*) AS c
        FROM logs
        WHERE level='ERROR' AND timestamp >= ?
        GROUP BY service
        ORDER BY c DESC
        LIMIT 5
        """,
        (since,),
    ).fetchall()

    recent = db.execute(
        f"""
        SELECT id, timestamp, level, service, message
        FROM logs
        WHERE {where_sql}
        ORDER BY id DESC
        LIMIT 50
        """,
        tuple(params),
    ).fetchall()

    # Optional: simple alert banner (threshold)
    alert_threshold = int(request.args.get("alert_threshold", 10))
    alert_active = errors_last_window >= alert_threshold

    return render_template(
        "dashboard.html",
        errors_last_window=errors_last_window,
        top_services=top_services,
        logs=recent,
        minutes=minutes,
        level=level,
        service=service,
        q=q,
        alert_threshold=alert_threshold,
        alert_active=alert_active,
    )
