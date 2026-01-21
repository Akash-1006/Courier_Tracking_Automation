from datetime import datetime

def parse_statement_date(date_str):
    # Handles: "20/01/2026 07:30:50"
    return datetime.strptime(date_str.split()[0], "%d/%m/%Y").date()

def parse_receipt_date(date_str):
    return datetime.strptime(date_str, "%d-%b-%y").date()

def date_diff(d1, d2):
    return abs((d1 - d2).days)

def match_entries(statement, receipts):
    matched = []
    missed = []
    used_receipts = set()

    for stmt in statement:
        stmt_date = parse_statement_date(stmt["date"])
        found_match = None

        for idx, rcp in enumerate(receipts):
            if idx in used_receipts:
                continue

            rcp_date = parse_receipt_date(rcp["date"])

            # ✅ MATCH ONLY ON AMOUNT + DATE
            if stmt["amount"] == rcp["amount"]:
                if date_diff(stmt_date, rcp_date) <= 2:
                    found_match = rcp
                    used_receipts.add(idx)
                    break

        if found_match:
            matched.append({
                "statement": stmt,
                "receipt": found_match
            })
        else:
            missed.append(stmt)

    return matched, missed
