from flask import Flask, request, jsonify
from models import db, Consignment, TrackingHistory, FranchExpress
from processor import process_excel
from flask_cors import CORS
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
load_dotenv() 

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite3.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()
IST = pytz.timezone("Asia/Kolkata")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")


def send_email(subject, html_body, attachment_path=None):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    if attachment_path and os.path.exists(attachment_path):
        part = MIMEBase("application", "octet-stream")
        part.set_payload(open(attachment_path, "rb").read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
        msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASS)
    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    server.quit()


# -----------------------------------------------------------
#  DAILY EMAIL DIGEST (sent at 9 AM IST)
# -----------------------------------------------------------
def generate_daily_report():
    with app.app_context():
        today = datetime.now(IST).date()
        today_str = today.strftime("%d-%m-%Y")
        print(f"Daily report sent {today}")

        # Professional Courier Pending
        professional_pending = Consignment.query.filter_by(is_delivered=False).all()

        # Franch Express Pending
        fe_pending = FranchExpress.query.filter_by(is_delivered=False).all()

        if not professional_pending and not fe_pending:
            return  # nothing to report

        def build_rows(items, model_type="normal"):
            rows = []
            for c in items:
                rows.append({
                    "CNo": c.cno,
                    "TDate": (
                        datetime
                            .combine(datetime.strptime(c.tdate, "%Y-%m-%d"), datetime.min.time())
                            .astimezone(IST)
                            .strftime("%d-%m-%Y")
                        if c.tdate else "—"
                    ),
                    "Cnee": c.cnee or "—",
                    "Pincode": c.cpincode or "—",
                    "Destination": c.destn or "—",
                    "Weight": c.wt or "—",
                    "Pcs": c.pcs or "—",
                    "Last Status": c.last_status or "—",
                    "Last Checked": (
                        c.last_checked.astimezone(IST).strftime("%d-%m-%Y %H:%M:%S")
                        if c.last_checked else "—"
                    )
                })
            return rows

        rows_professional = build_rows(professional_pending)
        rows_fe = build_rows(fe_pending)

        # Light safe escape
        def esc(s):
            return (str(s)
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))

        def create_table(rows, title):
            if not rows:
                return f"<p><b>No pending consignments for {title}</b></p>"

            table_headers = "".join([
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>CNo</th>",
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>T-Date</th>",
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>Cnee</th>",
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>Pincode</th>",
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>Destination</th>",
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>Weight</th>",
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>Pcs</th>",
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>Last Status</th>",
                "<th style='text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;'>Last Checked (IST)</th>",
            ])

            rows_html = "".join([
                "<tr>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6;font-weight:600'>{esc(r['CNo'])}</td>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['TDate'])}</td>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Cnee'])}</td>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Pincode'])}</td>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Destination'])}</td>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Weight'])}</td>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Pcs'])}</td>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Last Status'])}</td>" +
                f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Last Checked'])}</td>" +
                "</tr>"
                for r in rows
            ])

            return f"""
            <h3 style="margin:20px 0 10px 0;">{title} (Pending: {len(rows)})</h3>
            <table style="border-collapse:collapse;width:100%;font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111827;background:#ffffff;border:1px solid #e5e7eb;">
                <thead style="background:#f9fafb">
                    <tr>{table_headers}</tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """

        # Build full HTML email
        html_body = f"""
        <div style="font-family:Arial,Helvetica,sans-serif;color:#111827;">
          <h2 style="margin:0 0 8px 0;">Pending Consignments Report as on {today_str}</h2>
          
          {create_table(rows_professional, " Professional Courier")}
          <br/><br/>

          {create_table(rows_fe, " Franch Express")}
        </div>
        """

        send_email(
            subject=f" Pending Consignments Report - {today_str}",
            html_body=html_body
        )


@app.route("/send_daily_email", methods=["GET"])
def manual_email():
    generate_daily_report()
    return jsonify({"message": "Daily email sent manually!"})

@app.route("/upload", methods=["POST"])
def upload_excel():
    file = request.files['file']
    path = f"uploads/{file.filename}"
    file.save(path)

    count = process_excel(path)
    track_all()
    return jsonify({"message": "Uploaded and processed", "count": count})

@app.route("/track_consignments", methods=["GET"])
def track_all():
    from datetime import datetime
    from tracker import get_tracking_info
    from models import db, Consignment, TrackingHistory
    ist = pytz.timezone("Asia/Kolkata")
    pending = Consignment.query.filter_by(is_delivered=False).all()

    for cons in pending:
        cno = cons.cno

        data = get_tracking_info(cno)

        if not data:
            continue

        last_row = data[-1]
        status = last_row["Status"].strip()

        cons.last_status = status
        cons.is_delivered = status.lower() == "delivered"
        cons.last_checked = datetime.now(ist)

        for row in data:

            exists = TrackingHistory.query.filter_by(
                consignment_id=cons.id,
                delivery_date=row["Delivery Date"],
                destination=row["Destination"],
                delivery_area=row["Delivery Area"],
                status=row["Status"],
                drs_no=row["DRS No"],
                stamp=row["Stamp"]
            ).first()

            if exists:
                continue  

            hist = TrackingHistory(
                consignment_id=cons.id,
                delivery_date=row["Delivery Date"],
                destination=row["Destination"],
                delivery_area=row["Delivery Area"],
                status=row["Status"],
                drs_no=row["DRS No"],
                stamp=row["Stamp"],
                scraped_at= datetime.now(ist)

            )
            db.session.add(hist)

    db.session.commit()

    consignments = Consignment.query.all()

    return jsonify([
        {
            "cno": c.cno,
            "status": c.last_status,
            "delivered": c.is_delivered,
            "last_checked": c.last_checked.isoformat() if c.last_checked else None,

            # ✅ New fields
            "tdate": c.tdate,
            "cnee": c.cnee,
            "cpincode": c.cpincode,
            "destn": c.destn,
            "wt": c.wt,
            "pcs": c.pcs,
        }
        for c in consignments
    ])
@app.route("/consignments", methods=["GET"])
def list_all():
    consignments = Consignment.query.all()
    return jsonify([
        {
            "cno": c.cno,
            "status": c.last_status,
            "delivered": c.is_delivered,
            "last_checked": c.last_checked.isoformat() if c.last_checked else None,

            # ✅ New fields
            "tdate": c.tdate,
            "cnee": c.cnee,
            "cpincode": c.cpincode,
            "destn": c.destn,
            "wt": c.wt,
            "pcs": c.pcs,
        }
        for c in consignments
    ])


@app.route("/track_franch", methods=["GET"])
def track_franch():
    from tracker_franch import get_fe_tracking_info
    ist = pytz.timezone("Asia/Kolkata")
    pending = FranchExpress.query.filter_by(is_delivered=False).all()

    for cons in pending:
        data = get_fe_tracking_info(cons.cno)
        if not data or data.get("status") != "success":
            continue

        details = data["data"]
        status = details.get("dl_status_txt", "")

        cons.last_status = status
        cons.is_delivered = status.lower() == "delivered"
        cons.last_checked = datetime.now(ist)

    db.session.commit()

    return jsonify([
        {
            "cno": c.cno,
            "status": c.last_status,
            "delivered": c.is_delivered,
            "last_checked": c.last_checked.isoformat() if c.last_checked else None,
            "tdate": c.tdate,
            "cnee": c.cnee,
            "cpincode": c.cpincode,
            "destn": c.destn,
            "wt": c.wt,
            "pcs": c.pcs,
        }
        for c in FranchExpress.query.all()
    ])

@app.route("/upload_fe", methods=["POST"])
def upload_fe():
    file = request.files['file']
    path = f"uploads/{file.filename}"
    file.save(path)

    from process_excel_fe import process_excel_fe
    count = process_excel_fe(path)
    track_franch()

    return jsonify({"message": "FE Excel processed", "count": count})

@app.route("/fe_consignments", methods=["GET"])
def list_all_fe():
    consignments = FranchExpress.query.all()
    return jsonify([
        {
            "cno": c.cno,
            "status": c.last_status,
            "delivered": c.is_delivered,
            "last_checked": c.last_checked.isoformat() if c.last_checked else None,

            # 📌 Fields from Franch Express model
            "tdate": c.tdate,
            "cnee": c.cnee,
            "cpincode": c.cpincode,
            "destn": c.destn,
            "wt": c.wt,
            "pcs": c.pcs,
        }
        for c in consignments
    ])

@app.route("/mark_delivered/<cno>", methods=["POST"])
def mark_delivered(cno):
    cons = Consignment.query.filter_by(cno=cno).first()

    if not cons:
        return jsonify({"error": "Consignment not found"}), 404

    cons.is_delivered = True
    cons.last_status = "Delivered"
    cons.last_checked = datetime.now(IST)

    db.session.commit()

    return jsonify({"message": "Marked as delivered"})


@app.route("/fe/mark_delivered/<cno>", methods=["POST"])
def mark_delivered_fe(cno):
    cons = FranchExpress.query.filter_by(cno=cno).first()

    if not cons:
        return jsonify({"error": "Franch Express consignment not found"}), 404

    cons.is_delivered = True
    cons.last_status = "Delivered"
    cons.last_checked = datetime.now(IST)

    db.session.commit()

    return jsonify({"message": "Franch Express consignment marked as delivered"})




if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone=IST)
    print(IST)
    scheduler.add_job(generate_daily_report, "cron", hour=9, minute=00)  # daily 9 AM IST
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True,use_reloader=False)
