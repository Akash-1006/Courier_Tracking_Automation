import requests
from bs4 import BeautifulSoup

# -----------------------------------------
# CONSIGNMENT LIST (for initial testing)
# Replace with your excel values later
# -----------------------------------------
consignments = ["MAA709470809"]
formatted = (",".join(consignments)).rstrip(",") + ","
print(formatted)

# -----------------------------------------
# Create a session
# -----------------------------------------
session = requests.Session()

# -----------------------------------------
# STEP 1: GET the tracking page to fetch VIEWSTATE
# -----------------------------------------
url = "https://www.tpcindia.com/multiple-tracking.aspx"
get_page = session.get(url)

soup = BeautifulSoup(get_page.text, "html.parser")

viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
viewgen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]

print("[+] VIEWSTATE length:", len(viewstate))
print("[+] VIEWSTATEGENERATOR:", viewgen)

# -----------------------------------------
# STEP 2: Create POST payload
# -----------------------------------------
payload = {
    "__EVENTTARGET": "ctl00$ctl00$ContentPlaceHolderBottom$ContentPlaceHolderQuickLinkBottom$Button1",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": viewstate,
    "__VIEWSTATEGENERATOR": viewgen,
    "ctl00$ctl00$ContentPlaceHolderBottom$ContentPlaceHolderQuickLinkBottom$podno": formatted
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0"
}

# -----------------------------------------
# STEP 3: POST the request
# -----------------------------------------
post_resp = session.post(url, data=payload, headers=headers)

print("\n[+] POST Status:", post_resp.status_code)

# -----------------------------------------
# STEP 4: Parse the tracking table
# -----------------------------------------
soup = BeautifulSoup(post_resp.text, "html.parser")
table = soup.find("table", {"id": "ContentPlaceHolderBottom_ContentPlaceHolderQuickLinkBottom_GridView1"})

if table is None:
    print("\n[!] No table found. The request may not have worked.")
    exit()

rows = []
for tr in table.find_all("tr")[1:]:
    cols = [td.get_text(strip=True) for td in tr.find_all("td")]
    rows.append(cols)

print("\n[+] Extracted Tracking Data:")
for r in rows:
    print(r)
