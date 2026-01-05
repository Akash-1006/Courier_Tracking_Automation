import re
import time
import math
import pathlib
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ------------------ CONFIG ------------------
EXCEL_PATH = r"MPK0006811.xls"   # change to your path if needed
COLUMN_NAME = "CNo"           # the column in your Excel with consignment numbers
PREFIX = "MAA"                   # what to prepend (e.g., "MAA")
MAX_PER_REQUEST = 100            # site allows max 100 at a time
BASE_URL = "https://www.tpcindia.com/multiple-tracking.aspx"
TIMEOUT = 30
# --------------------------------------------

def read_consignment_numbers(xls_path: str, column: str, prefix: str) -> list[str]:
    df = pd.read_excel(xls_path, dtype=str)  # keep as strings
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found. Available: {list(df.columns)}")

    vals = []
    for raw in df[column].dropna().astype(str):
        s = raw.strip()
        if not s:
            continue
        # Keep only alnum
        s = re.sub(r"[^A-Za-z0-9]", "", s)

        # If it already starts with letters (e.g., MAA...), keep as-is; else add PREFIX
        if re.match(r"^[A-Za-z]+", s):
            vals.append(s.upper())
        else:
            vals.append(f"{prefix}{s}".upper())

    # de-dup while preserving order
    seen = set()
    unique_vals = []
    for v in vals:
        if v not in seen:
            seen.add(v)
            unique_vals.append(v)
    return unique_vals

def fetch_viewstate(session: requests.Session) -> dict:
    r = session.get(BASE_URL, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    vs = soup.select_one("#__VIEWSTATE")
    vsg = soup.select_one("#__VIEWSTATEGENERATOR")
    if not vs or not vsg:
        raise RuntimeError("Could not find __VIEWSTATE / __VIEWSTATEGENERATOR on page.")
    return {
        "__VIEWSTATE": vs.get("value", ""),
        "__VIEWSTATEGENERATOR": vsg.get("value", ""),
    }

def submit_batch(session: requests.Session, numbers: list[str]) -> pd.DataFrame:

    # ---------------------------------------
    # ✅ Your trailing comma logic applied here
    # ---------------------------------------
    formatted = (",".join(numbers)).rstrip(",") + ","
    # ---------------------------------------

    # The page expects a postback triggered by the "Track" button
    payload_base = {
        "__EVENTTARGET": "ctl00$ctl00$ContentPlaceHolderBottom$ContentPlaceHolderQuickLinkBottom$Button1",
        "__EVENTARGUMENT": "",
        "ctl00$ctl00$ContentPlaceHolderBottom$ContentPlaceHolderQuickLinkBottom$podno": formatted,
    }

    # 1) GET to capture fresh viewstate
    vs = fetch_viewstate(session)
    payload = payload_base | vs

    # 2) POST
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.tpcindia.com",
        "Referer": BASE_URL,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/140.0.0.0 Safari/537.36",
    }
    resp = session.post(BASE_URL, data=payload, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()

    # 3) Parse result table
    soup = BeautifulSoup(resp.text, "lxml")
    table = soup.select_one("#ContentPlaceHolderBottom_ContentPlaceHolderQuickLinkBottom_GridView1")
    if table is None:
        err = soup.select_one("#ContentPlaceHolderBottom_ContentPlaceHolderQuickLinkBottom_Label2")
        msg = err.get_text(strip=True) if err else "No result table found."
        return pd.DataFrame({"Error": [msg]})

    # Extract header
    headers = [th.get_text(strip=True) for th in table.select("tr:first-child th")]
    rows = []
    for tr in table.select("tr")[1:]:
        tds = tr.find_all(["td", "th"])
        if not tds:
            continue
        row = [td.get_text(strip=True) for td in tds]
        while len(row) < len(headers):
            row.append("")
        rows.append(row[:len(headers)])

    df = pd.DataFrame(rows, columns=headers if headers else None)
    return df

def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]

def main():
    excel_path = pathlib.Path(EXCEL_PATH)
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path.resolve()}")

    numbers = read_consignment_numbers(str(excel_path), COLUMN_NAME, PREFIX)
    if not numbers:
        print("No consignment numbers found. Check your Excel and column name.")
        return

    print(f"Found {len(numbers)} consignment numbers. Submitting in batches of {MAX_PER_REQUEST}…")
    print(numbers)
    all_results = []
    with requests.Session() as s:
        for idx, batch in enumerate(chunked(numbers, MAX_PER_REQUEST), start=1):
            print(f"Batch {idx}: {len(batch)} numbers")
            try:
                df = submit_batch(s, batch)
                # Tag which batch the rows came from
                if not df.empty:
                    df.insert(0, "Batch", idx)
                all_results.append(df)
            except Exception as e:
                err_df = pd.DataFrame({
                    "Batch": [idx],
                    "Error": [str(e)],
                })
                all_results.append(err_df)
            # Be polite to the server
            time.sleep(1.0)

    result_df = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    out_csv = "tpc_results.csv"
    result_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"\nDone. Saved results to {out_csv}")
    # Show a quick preview in console
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(result_df.head(20))

if __name__ == "__main__":
    main()
