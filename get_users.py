#!/usr/bin/env python3
"""
PALM Smart Lock — Get Registered Users
Lists all registered temp passwords / users on the lock.

Usage:
    python3 scripts/get_users.py
"""

import hmac, hashlib, time, requests, json

CLIENT_ID     = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
DEVICE_ID     = "YOUR_DEVICE_ID"
BASE_URL      = "https://openapi.tuyaeu.com"

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
print("Token OK\n")

path = f"/v1.0/devices/{DEVICE_ID}/door-lock/temp-passwords"
r    = requests.get(BASE_URL+path, headers=sign("GET",path,T))
data = r.json()

if not data.get("success"):
    print("Failed:", data)
    exit(1)

users = data["result"]
print(f"Found {len(users)} registered user(s):\n")
print(f"{'SN':>6}  {'Name':<20}  {'Type':<12}  {'Status':<10}  {'Valid Until'}")
print("-" * 70)
for u in users:
    sn      = u.get("sn", "?")
    name    = u.get("name", "unnamed")
    utype   = "Permanent" if u.get("type") == 0 else "Temporary"
    active  = "Active" if u.get("phase") == 2 else "Inactive"
    exp     = time.strftime('%Y-%m-%d %H:%M', time.localtime(u["invalid_time"])) if u.get("invalid_time") else "No expiry"
    print(f"{sn:>6}  {name:<20}  {utype:<12}  {active:<10}  {exp}")
