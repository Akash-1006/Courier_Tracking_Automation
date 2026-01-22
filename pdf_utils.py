import pdfplumber
import pandas as pd
import re
from datetime import datetime

def clean_amount(val):
    return float(str(val).replace(",", "").strip())

def normalize_text(text):
    text = text.upper()
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def parse_date(date_str):
    return datetime.strptime(date_str, "%d-%b-%y").date()

# -------- STATEMENT PDF --------
def extract_statement_entries(pdf_path):
    entries = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue

            for row in table:
                try:
                    # Skip header rows safely
                    if row[1] and "DATE" in row[1].upper():
                        continue

                    date = row[1]
                    desc = row[3]
                    deposit = row[6]

                    if date and deposit:
                        entries.append({
                            "date": date,
                            "description": normalize_text(desc),
                            "amount": clean_amount(deposit)
                        })
                except Exception:
                    continue

    return entries

# -------- RECEIPT PDF --------
def extract_receipt_entries(pdf_path):
    entries = []
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text().split("\n")

    for line in text:
        match = re.search(r"(\d{1,2}-[A-Za-z]{3}-\d{2})\s+(.*?)\s+([\d,]+\.\d{2})", line)
        if match:
            entries.append({
                "date": match.group(1),
                "party": normalize_text(match.group(2)),
                "amount": clean_amount(match.group(3))
            })
    return entries
