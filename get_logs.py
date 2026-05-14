#!/usr/bin/env python3
"""
PALM Smart Lock — Get Activity Logs
Fetches unlock history for the last 7 days.

Usage:
    python3 scripts/get_logs.py
    python3 scripts/get_logs.py --days 30
"""

import hmac, hashlib, time, requests, json, sys

CLIENT_ID     = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
DEVICE_ID     = "YOUR_DEVICE_ID"
BASE_URL      = "https://openapi.tuyaeu.com"

days = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--days" else 7

def sign(method, path, token="", body=""):
    t   = str(int(time.time() * 1000))
    bh  = hashlib.sha256(body.encode()).hexdigest()
    sts = "\n".join([method.upper(), bh, "", path])
    msg = CLIENT_ID + token + t + sts
    sig = hmac.new(CLIENT_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest().upper()
    h   = {"client_id":CLIENT_ID,"sign_method":"HMAC-SHA256","t":t,"nonce":"","sign":sig,"Content-Type":"application/json"}
    if token: h["access_token"] = token
    return h

path = "/v1.0/token?grant_type=1"
T    = requests.get(BASE_URL+path, headers=sign("GET",path)).json()["result"]["access_token"]

now   = int(time.time())
since = now - (days * 86400)

METHODS = {
    "unlock_fingerprint": "👆 Fingerprint",
    "unlock_password":    "🔢 Password",
    "unlock_temporary":   "🔑 Temp Code",
    "unlock_card":        "💳 Card",
    "unlock_app":         "📱 App",
    "unlock_face":        "😊 Face",
    "unlock_key":         "🗝 Key",
    "unlock_hand":        "✋ Hand",
}

qs   = f"end_time={now}&page_no=1&page_size=50&start_time={since}"
path = f"/v1.0/devices/{DEVICE_ID}/door-lock/open-logs?{qs}"
r    = requests.get(BASE_URL+path, headers=sign("GET",path,T))
data = r.json()

if not data.get("success"):
    print("Failed:", data); exit(1)

logs  = data["result"].get("logs", [])
total = data["result"].get("total", 0)

print(f"\nUnlock Activity — last {days} day(s) | Total: {total} events\n")
print(f"{'Time':<22}  {'Method':<20}  {'User'}")
print("-" * 65)

for e in logs:
    t   = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e["update_time"]))
    s   = e.get("status", {})
    code= s.get("code", "")
    val = s.get("value", "")
    meth= METHODS.get(code, code)
    name= e.get("nick_name") or e.get("unlock_name") or f"User #{val}"
    print(f"{t:<22}  {meth:<20}  {name}")
