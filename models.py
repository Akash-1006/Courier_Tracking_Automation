from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Consignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cno = db.Column(db.String(50), unique=True, nullable=False)

    # ✅ New Excel columns
    tdate = db.Column(db.String(50))
    cnee = db.Column(db.String(200))
    cpincode = db.Column(db.String(20))
    destn = db.Column(db.String(100))
    wt = db.Column(db.String(20))
    pcs = db.Column(db.String(20))

    # Tracking fields
    last_status = db.Column(db.String(200))
    is_delivered = db.Column(db.Boolean, default=False)
    last_checked = db.Column(db.DateTime)

class TrackingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consignment_id = db.Column(db.Integer, db.ForeignKey('consignment.id'))
    delivery_date = db.Column(db.String(100))
    destination = db.Column(db.String(200))
    delivery_area = db.Column(db.String(200))
    status = db.Column(db.String(200))
    drs_no = db.Column(db.String(100))
    stamp = db.Column(db.String(200))
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)

class FranchExpress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cno = db.Column(db.String(50), unique=True, nullable=False)
    
    tdate = db.Column(db.String(50))
    cnee = db.Column(db.String(200))
    cpincode = db.Column(db.String(20))
    destn = db.Column(db.String(100))
    wt = db.Column(db.String(20))
    pcs = db.Column(db.String(20))

    last_status = db.Column(db.String(200))
    is_delivered = db.Column(db.Boolean, default=False)
    last_checked = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
