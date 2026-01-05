import pandas as pd
from models import db, FranchExpress

EXPECTED_FE_COLS = ["Consignment No", "Date", "Name", "Pincode", "Destination", "WEIGHT", "Pcs"]

def process_excel_fe(path):
    df = pd.read_excel(path, dtype=str)

    for col in EXPECTED_FE_COLS:
        if col not in df.columns:
            df[col] = ""

    count = 0

    for _, row in df.iterrows():
        cno = str(row["Consignment No"]).strip().upper()
        if not cno or not cno.isdigit():
            continue

        existing = FranchExpress.query.filter_by(cno=cno).first()

        if not existing:
            existing = FranchExpress(cno=cno)
            db.session.add(existing)
            count += 1  # Only count new entries

        existing.tdate = str(row["Date"]).split(" ")[0]  # only date
        existing.cnee = row["Name"]
        existing.cpincode = row["Pincode"]
        existing.destn = row["Destination"]
        existing.wt = row["WEIGHT"]
        existing.pcs = row["Pcs"]

    db.session.commit()
    return count
