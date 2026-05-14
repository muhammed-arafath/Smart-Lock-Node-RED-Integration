#!/usr/bin/env python3
"""
PALM Smart Lock — Setup Check Script
Verifies Tuya credentials and fetches device information.

Usage:
    pip install pycryptodome requests
    python3 scripts/setup_check.py
"""

import hmac
import hashlib
import time
import requests
import json

# ── FILL IN YOUR CREDENTIALS ──────────────────────────────────────────────────
CLIENT_ID     = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
DEVICE_ID     = "YOUR_DEVICE_ID"
BASE_URL      = "https://openapi.tuyaeu.com"   # EU region — change if needed
# ──────────────────────────────────────────────────────────────────────────────

def sign(method, path, token="", body=""):
    t   = str(int(time.time() * 1000))
    bh  = hashlib.sha256(body.encode()).hexdigest()
    sts = "\n".join([method.upper(), bh, "", path])
    msg = CLIENT_ID + token + t + sts
    sig = hmac.new(CLIENT_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest().upper()
    h   = {
        "client_id":    CLIENT_ID,
        "sign_method":  "HMAC-SHA256",
        "t":            t,
        "nonce":        "",
        "sign":         sig,
        "Content-Type": "application/json"
    }
    if token:
        h["access_token"] = token
    return h


def main():
    print("=" * 60)
    print("PALM Smart Lock — Setup Check")
    print("=" * 60)

    # Step 1: Get token
    print("\n[1] Testing credentials...")
    path = "/v1.0/token?grant_type=1"
    r    = requests.get(BASE_URL + path, headers=sign("GET", path))
    data = r.json()

    if not data.get("success"):
        print(f"❌ Authentication failed: {data}")
        print("\nCheck your CLIENT_ID and CLIENT_SECRET.")
        return

    T = data["result"]["access_token"]
    print(f"✅ Token OK (expires in {data['result']['expire_time']}s)")

    # Step 2: Get device info
    print("\n[2] Fetching device info...")
    path = f"/v2.0/cloud/thing/{DEVICE_ID}"
    r    = requests.get(BASE_URL + path, headers=sign("GET", path, T))
    dev  = r.json()

    if dev.get("success"):
        d = dev["result"]
        print(f"✅ Device found:")
        print(f"   Name     : {d.get('name')}")
        print(f"   Category : {d.get('category')}")
        print(f"   Model    : {d.get('model')}")
        print(f"   Online   : {d.get('is_online')}")
        print(f"   Local Key: {d.get('local_key')}")
    else:
        print(f"❌ Device fetch failed: {dev}")

    # Step 3: Get device functions (DPS)
    print("\n[3] Fetching device functions (DPS)...")
    path = f"/v1.0/devices/{DEVICE_ID}/functions"
    r    = requests.get(BASE_URL + path, headers=sign("GET", path, T))
    fns  = r.json()

    if fns.get("success"):
        print("✅ Available functions:")
        for fn in fns["result"]["functions"]:
            print(f"   {fn['code']:30s} | {fn['type']:10s} | {fn.get('desc','')}")
    else:
        print(f"❌ Functions fetch failed: {fns}")

    # Step 4: Get current status
    print("\n[4] Current device status...")
    path = f"/v1.0/devices/{DEVICE_ID}/status"
    r    = requests.get(BASE_URL + path, headers=sign("GET", path, T))
    stat = r.json()

    if stat.get("success"):
        print("✅ Current status:")
        for s in stat["result"]:
            print(f"   {s['code']:30s} = {s['value']}")
    else:
        print(f"❌ Status fetch failed: {stat}")

    # Step 5: Test offline password API
    print("\n[5] Testing offline password generation...")
    path = f"/v1.1/devices/{DEVICE_ID}/door-lock/offline-temp-password"
    now  = int(time.time())
    body = json.dumps({"type": "once", "effective_time": now, "invalid_time": now + 3600})
    r    = requests.post(BASE_URL + path, headers=sign("POST", path, T, body), data=body)
    pwd  = r.json()

    if pwd.get("success"):
        code = pwd["result"]["offline_temp_password"]
        exp  = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pwd["result"]["invalid_time"]))
        print(f"✅ Offline password generated!")
        print(f"   Code      : {code}")
        print(f"   Valid until: {exp}")
        print(f"\n   Enter '{code}' on your lock keypad to test.")
    else:
        print(f"❌ Offline password failed: {pwd}")
        if pwd.get("code") == 28841101:
            print("   → Subscribe to 'Smart Lock Open Service' in Tuya IoT Platform")

    print("\n" + "=" * 60)
    print("Setup check complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
