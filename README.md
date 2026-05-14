# 🔐 PALM Smart Lock — Node-RED Integration

> **PALM** — Smart Lock Access System  
> Full integration between a Tuya Smart Lock Pro (`jtmspro`) and Node-RED using Tuya Cloud OpenAPI + Local LAN connection.

---

## Features

| Feature | Status | Method |
|---|---|---|
| Real-time unlock events | ✅ | Local tuya-device node |
| Who unlocked + User ID | ✅ | Status polling + user name lookup |
| Offline keypad code generator | ✅ | Tuya Cloud API v1.1 |
| Calendar UI (PALM) | ✅ | Served via Node-RED HTTP |
| Unlock activity logs (24h) | ✅ | Tuya Cloud open-logs API |
| 7-day activity summary | ✅ | Tuya Cloud open-logs API |
| Battery / alarm monitoring | ✅ | Status polling |
| HTTP API (phone/browser) | ✅ | Node-RED HTTP nodes |
| Auto token refresh | ✅ | Every 2 hours |

---

## Architecture

```
Phone / Browser
      │
      ▼
┌─────────────────┐
│   Node-RED      │
│  (172.x.x.x:1880) │
│                 │
│  ┌───────────┐  │       Local LAN
│  │tuya-device│◄─┼──────────────────► Smart Lock
│  │   node    │  │       (192.168.x.x)
│  └───────────┘  │
│                 │       Tuya Cloud
│  ┌───────────┐  │       (openapi.tuyaeu.com)
│  │ HTTP nodes│◄─┼──────────────────► Offline Password
│  │  (Cloud)  │  │                    Activity Logs
│  └───────────┘  │                    User List
└─────────────────┘
```

---

## Requirements

### Hardware
- Tuya Smart Lock Pro (category: `jtmspro`)
- Linux/Raspberry Pi running Node-RED
- Lock and Node-RED on same local network

### Software
- [Node-RED](https://nodered.org/) v3.x+
- Node-RED package: `node-red-contrib-tuya-devices` v1.5.5+
- Python 3 (for setup scripts only)
- `pycryptodome` Python package (for setup scripts)

### Tuya Platform
- Tuya IoT Platform account: [iot.tuya.com](https://iot.tuya.com)
- Project with these APIs subscribed:
  - ✅ IoT Core
  - ✅ Authorization Token Management
  - ✅ Smart Home Basic Service
  - ✅ Smart Lock Open Service
  - ✅ Device Status Notification

---

## Setup

### Step 1 — Get Your Credentials

From [Tuya IoT Platform](https://iot.tuya.com):

| Field | Where to find |
|---|---|
| `CLIENT_ID` | Cloud → your project → Overview |
| `CLIENT_SECRET` | Cloud → your project → Overview (click eye icon) |
| `DEVICE_ID` | Cloud → Devices → your lock → Device ID |
| `LOCAL_KEY` | Cloud → Devices → your lock → Local Key |
| `LOCK_IP` | Router admin → DHCP → find lock by MAC address |

### Step 2 — Run Setup Script

```bash
pip install pycryptodome requests
python3 scripts/setup_check.py
```

This verifies your credentials and shows your device's DPS (Data Points).

### Step 3 — Install Node-RED Package

In Node-RED:
```
Menu → Manage Palette → Install → node-red-contrib-tuya-devices
```

### Step 4 — Import the Flow

1. Open Node-RED (`http://YOUR-IP:1880`)
2. Menu → Import → select `flows/smartlock.json`
3. Open the **tuya-local-device** config node (pencil icon on Smart Lock node)
4. Fill in: `Device ID`, `Local Key`, `IP Address`
5. Go to **Advanced** tab → set `Tuya Version` to `3.3`

### Step 5 — Configure Cloud Credentials

In the flow, the following function nodes need your credentials. Search for `YOUR_CLIENT_ID` and replace:

```javascript
var C = 'YOUR_CLIENT_ID';      // ← replace
var S = 'YOUR_CLIENT_SECRET';  // ← replace
var D = 'YOUR_DEVICE_ID';      // ← replace
var B = 'https://openapi.tuyaeu.com';
```

> **Tip:** Use Node-RED's global environment variables instead of hardcoding. Set in `settings.js`:
> ```js
> envVarSchemas: { TUYA_CLIENT_ID: {}, TUYA_SECRET: {}, TUYA_DEVICE_ID: {} }
> ```

### Step 6 — Deploy

Click **Deploy**. Within 5 seconds:
- ✅ **Save Token** node shows green `Token OK HH:MM:SS`
- ✅ **Save User Map** shows `N users loaded`
- ✅ **Smart Lock** device node shows connected (no red dot)

---

## PALM UI — Access Code Generator

Open in any browser or phone:
```
http://YOUR-NODE-RED-IP:1880/lock
```

### Features
- Select duration: 1h / 2h / 4h / 8h / 1 day / 3 days
- Custom hours input
- Generates offline keypad code instantly
- Works even when lock has no internet
- Tap code to copy

### How It Works
1. Calls `POST /v1.1/devices/{id}/door-lock/offline-temp-password`
2. Tuya returns a unique numeric code
3. User enters code on physical keypad → lock opens

---

## HTTP API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/lock` | GET | Open PALM UI in browser |
| `/api/password` | POST | Generate offline keypad code |
| `/api/logs` | GET | Last 24h unlock activity |
| `/api/status` | GET | Current lock status + battery |

### POST `/api/password`

**Request:**
```json
{ "hours": 4 }
```

**Response:**
```json
{
  "success": true,
  "password": "9969430812",
  "fromMs": 1746300000000,
  "toMs":   1746314400000
}
```

### GET `/api/logs`

**Response:**
```json
{
  "success": true,
  "totalLogs": 38,
  "latest": {
    "time": "03/05/2026, 20:06:00",
    "method": "🔑 Temp Code",
    "userName": "Arafath (ID:910)"
  },
  "all": [...]
}
```

---

## Flow Sections

```
┌─────────────────────────────────────────────────────┐
│  1. AUTO TOKEN      — refreshes Tuya token every 2h  │
│  2. LOCAL EVENTS    — real-time lock/unlock from LAN  │
│  3. OFFLINE PWD     — generate keypad codes (cloud)   │
│  4. ACTIVITY LOGS   — last 24h unlock history         │
│  5. ALARM LOGS      — 7-day activity summary          │
│  6. HTTP API        — phone/browser endpoints         │
│  7. CALENDAR UI     — PALM web interface              │
└─────────────────────────────────────────────────────┘
```

---

## Unlock Methods Detected

| Code | Method |
|---|---|
| `unlock_fingerprint` | 👆 Fingerprint |
| `unlock_password` | 🔢 Password |
| `unlock_temporary` | 🔑 Temp Code |
| `unlock_card` | 💳 Card |
| `unlock_face` | 😊 Face ID |
| `unlock_key` | 🗝 Physical Key |
| `unlock_app` | 📱 App/Remote |
| `unlock_hand` | ✋ Hand |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Device not connected` | Check IP, Local Key, and set Tuya Version to `3.3` or `3.4` |
| `sign invalid (1004)` | Token expired — wait for auto-refresh or click Get Token |
| `command not support (2008)` | DPS code not writable for this device |
| `No permissions (28841101)` | Subscribe to Smart Lock Open Service in Tuya platform |
| UI shows `<!DOCTYPE` error | Missing tab node — re-import the flow |
| Code doesn't work on keypad | Effective time mismatch — always generate fresh code |

---

## Known Limitations

- **Physical remote unlock** is not possible via standard API — requires Tuya's proprietary encrypted SDK
- **Dynamic password** (`/v1.0/door-lock/dynamic-password`) not supported on this lock model
- **Alarm logs** API (`/v1.0/door-lock/alarm-logs`) returns param error — real-time alarms detected via local device events instead
- Local connection requires lock and Node-RED on same LAN

---

## Scripts

| Script | Purpose |
|---|---|
| `scripts/setup_check.py` | Verify credentials + get device spec |
| `scripts/get_users.py` | List all registered lock users |
| `scripts/get_logs.py` | Fetch raw activity logs |

---

## Security Notes

⚠️ **Never commit credentials to GitHub.**

- Add your credentials to `.env` or Node-RED environment variables
- The `flows/smartlock.json` in this repo has all credentials replaced with `YOUR_*` placeholders
- Rotate your `LOCAL_KEY` if it is ever exposed
- Restrict Node-RED access with a username/password (Settings → Security)

---

## License

MIT — free to use, modify, and distribute.

---

## Credits

Built with:
- [Node-RED](https://nodered.org/)
- [node-red-contrib-tuya-devices](https://www.npmjs.com/package/node-red-contrib-tuya-devices)
- [Tuya IoT Platform OpenAPI](https://developer.tuya.com/)
