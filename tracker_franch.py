import requests
import json

def get_fe_tracking_info(cno):
    url = "https://franchexpress.com/proxy.php"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {"awb": cno, "captcha": ""}

    res = requests.post(url, headers=headers, data=json.dumps(payload))

    if res.status_code != 200:
        return None

    return res.json()
