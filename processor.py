import pandas as pd
from models import db, Consignment
import re
from datetime import datetime

EXPECTED_COLS = ["CNo", "Tdate", "cnee", "CPincode", "Destn", "Wt", "Pcs"]


VALID_CNO_REGEX = re.compile(r"^MAA\d+$", re.IGNORECASE)
def process_excel(path):
    df = pd.read_excel(path, dtype=str)

    # ✅ Ensure missing columns exist
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = ""

    count = 0

    for _, row in df.iterrows():
        cno = str(row["CNo"]).strip().upper()
        if not cno or not VALID_CNO_REGEX.match(cno):
            continue

        existing = Consignment.query.filter_by(cno=cno).first()

        updated = False  # ✅ Flag to track changes

        # ✅ Insert new record
        if not existing:
            existing = Consignment(cno=cno)
            db.session.add(existing)
            updated = True

        # ✅ Convert Tdate safely
        raw_date = row["Tdate"]
        try:
            new_tdate = pd.to_datetime(raw_date).date()
        except:
            new_tdate = None

        # ✅ Update only if value changed
        def update_if_changed(obj, field, new_value):
            nonlocal updated
            old_value = getattr(obj, field)

            # Convert dates to string for comparison
            if hasattr(old_value, 'isoformat'):
                old_value = old_value.isoformat()

            if hasattr(new_value, 'isoformat'):
                new_value = new_value.isoformat()

            if str(old_value) != str(new_value):
                setattr(obj, field, new_value)
                updated = True

        update_if_changed(existing, "tdate", new_tdate)
        update_if_changed(existing, "cnee", row["cnee"])
        update_if_changed(existing, "cpincode", row["CPincode"])
        update_if_changed(existing, "destn", row["Destn"])
        update_if_changed(existing, "wt", row["Wt"])
        update_if_changed(existing, "pcs", row["Pcs"])

       
        if updated:
            db.session.commit()
            count += 1

    return count
