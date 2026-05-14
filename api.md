# PALM Smart Lock — API Reference

Base URL: `http://YOUR-NODE-RED-IP:1880`

---

## Web Interface

### `GET /lock`
Opens the PALM access code generator UI in browser.

---

## REST API

### `POST /api/password`
Generate an offline keypad access code.

**Request body:**
```json
{ "hours": 4 }
```

| Field | Type | Default | Description |
|---|---|---|---|
| `hours` | number | `1` | How long the code is valid (0.25 to 720) |

**Response:**
```json
{
  "success": true,
  "password": "9969430812",
  "fromMs": 1746300000000,
  "toMs": 1746314400000
}
```

**Error response:**
```json
{
  "success": false,
  "error": "No token — wait and retry"
}
```

---

### `GET /api/logs`
Get last 24 hours of unlock activity.

**Response:**
```json
{
  "success": true,
  "totalLogs": 38,
  "latest": {
    "time": "03/05/2026, 20:06:00",
    "method": "🔑 Temp Code",
    "userName": "Arafath (ID:910)",
    "userId": "910"
  },
  "all": [
    {
      "time": "03/05/2026, 20:06:00",
      "method": "🔑 Temp Code",
      "userName": "Arafath (ID:910)",
      "userId": "910"
    }
  ]
}
```

---

### `GET /api/status`
Get current lock status.

**Response:**
```json
{
  "success": true,
  "battery": "50%",
  "armed": "DISARMED",
  "alarm": "wrong_finger",
  "passwords": 1,
  "fingerprints": 0,
  "unlock_counts": {
    "password": 1,
    "fingerprint": 0,
    "temporary": 910,
    "app": 0,
    "card": 0
  }
}
```

---

## Tuya Cloud APIs Used

| Purpose | Method | Endpoint |
|---|---|---|
| Get token | GET | `/v1.0/token?grant_type=1` |
| Get device info | GET | `/v2.0/cloud/thing/{device_id}` |
| Get functions | GET | `/v1.0/devices/{device_id}/functions` |
| Get status | GET | `/v1.0/devices/{device_id}/status` |
| Get temp users | GET | `/v1.0/devices/{device_id}/door-lock/temp-passwords` |
| Generate offline code | POST | `/v1.1/devices/{device_id}/door-lock/offline-temp-password` |
| Get unlock logs | GET | `/v1.0/devices/{device_id}/door-lock/open-logs` |

---

## Unlock Method Codes

| Code | Label |
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

## Alarm Codes

| Code | Meaning |
|---|---|
| `wrong_finger` | Wrong fingerprint attempt |
| `wrong_password` | Wrong password entered |
| `wrong_card` | Wrong card used |
| `pry` | Lock pried / forced |
| `low_battery` | Battery below 20% |
| `shock` | Shock/vibration detected |
| `defense` | Defense mode triggered |
| `tongue_bad` | Bolt mechanism error |
| `unclosed_time` | Door left open too long |
