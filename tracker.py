from test_excel import submit_batch

def get_tracking_info(cno):
    from requests import Session
    s = Session()
    df = submit_batch(s, [cno])

    if "Error" in df.columns:
        return []

    results = []
    for _, row in df.iterrows():
        results.append({
            "Consignment": row["CONSIGNMENT NO."],
            "Delivery Date": row["Delivery Date"],
            "Destination": row["Destination"],
            "Delivery Area": row["Delivery Area"],
            "Status": row["Status"],
            "DRS No": row["DRS No"],
            "Stamp": row["Stamp"],
        })

    return results
