from flask import Flask, request, jsonify
from models import db, Consignment, TrackingHistory
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


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite3.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()
IST = pytz.timezone("Asia/Kolkata")

EMAIL_FROM = "ingrify.help@gmail.com"
EMAIL_PASS = "cdyh tner fzod vhji"
EMAIL_TO = "fledge.enterprises@gmail.com"


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
# ✅ DAILY EMAIL DIGEST (sent at 9 AM IST)
# -----------------------------------------------------------
def generate_daily_report():
    with app.app_context():
        today = datetime.now(IST).date()
        print(f"Daily report sent {today}")
        # ✅ Fetch ONLY pending consignments (is_delivered = False / 0)
        pending = Consignment.query.filter_by(is_delivered=False).all()
        if not pending:
            # You can still send a "nothing pending" email if you prefer.
            return

        # ✅ Build rows (and keep the CSV too)
        rows = []
        for c in pending:
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

    df = pd.DataFrame(rows, columns=[
        "CNo", "TDate", "Cnee", "Pincode", "Destination", "Weight", "Pcs",
        "Last Status", "Last Checked"
    ])

    # ✅ Save CSV


    # ✅ Build HTML table for email (inline CSS for mail clients)
    def esc(s):
        # very light escape for HTML (in case any field contains < or &)
        return (str(s)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

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

    table_rows = []
    for r in rows:
        table_rows.append(
            "<tr>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6;font-weight:600'>{esc(r['CNo'])}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['TDate'])}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Cnee'])}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Pincode'])}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Destination'])}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Weight'])}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Pcs'])}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Last Status'])}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #f3f4f6'>{esc(r['Last Checked'])}</td>"
            "</tr>"
        )

    html_table = (
        "<table style='border-collapse:collapse;width:100%;font-family:Arial,Helvetica,sans-serif;"
        "font-size:14px;color:#111827;background:#ffffff;border:1px solid #e5e7eb;'>"
        "<thead style='background:#f9fafb'>"
        f"<tr>{table_headers}</tr>"
        "</thead>"
        "<tbody>"
        + "".join(table_rows) +
        "</tbody>"
        "</table>"
    )
    today_str = today.strftime("%d-%m-%Y")
    # ✅ Email body (with table embedded)
    html_body = f"""
    <div style="font-family:Arial,Helvetica,sans-serif;color:#111827;">
      <h2 style="margin:0 0 8px 0;">Pending Consignments Report as on {today_str}</h2>
      <h6 style="margin:0 0 16px 0;">Total pending: <b>{len(rows)}</b></h6>
      <p style="margin:0 0 16px 0;">Below is the latest list of consignments that are <b>not delivered</b> as of now.</p>
      {html_table}
    </div>
    """
    

    # 🔔 Send email with inline table + CSV attachment
    # Assumes you already have a send_email(subject, html_body, attachment_path) utility.
    send_email(
        subject=f"Pending Consignments as on {today_str}",
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



if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone=IST)
    print(IST)
    scheduler.add_job(generate_daily_report, "cron", hour=9, minute=00)  # daily 9 AM IST
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True,use_reloader=False)
