# Nice MNCUT — Home Assistant Integration

🇫🇷 [Lire en français](README.fr.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![HA Version](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue)

Home Assistant integration for the **Nice MNCUT** alarm control panel, using a local WebSocket connection (no cloud required).

---

## ✨ Features

- 🔒 Arm / Disarm / Arm Home via Home Assistant
- 📡 Real-time state updates via WebSocket (`local_push`)
- 🔋 Battery level monitoring (%)
- ⚡ Mains power status
- 🚨 Sabotage, open contact, triggered sensor detection
- ⏱️ Exit delay countdown
- 🛠️ Anomaly acknowledgement service (`clear_anomalies`)
- 🌐 Multi-language: English & French

---

## 📋 Requirements

- Home Assistant **2023.1 or newer**
- Nice MNCUT alarm panel accessible on your local network
- WebSocket port **4012** reachable from Home Assistant

---

## 📦 Installation

### Via HACS (recommended)

1. Open **HACS → Integrations**
2. Click the three dots (top right) → **Custom repositories**
3. Add this repository URL and select category **Integration**
4. Search for **Nice MNCUT** and install
5. Restart Home Assistant

### Manual

Copy `custom_components/nice_mncut` into `/config/custom_components/` and restart Home Assistant.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Nice MNCUT**
3. Enter:
   - **IP address** of your MNCUT panel
   - **PIN code**

---

## 🖥️ Dashboard Examples

- Simple: `examples/dashboard_simple.yaml`
- Premium: `examples/dashboard_premium.yaml`

---

## Entities

| Entity                                          | Type          | Description               |
| ----------------------------------------------- | ------------- | ------------------------- |
| `alarm_control_panel.nice_mncut`                | Alarm panel   | Main arm/disarm control   |
| `binary_sensor.nice_mncut_batterie_faible`      | Binary sensor | Low battery warning       |
| `binary_sensor.nice_mncut_alimentation_secteur` | Binary sensor | Mains power OK            |
| `binary_sensor.nice_mncut_sabotage`             | Binary sensor | Tamper / sabotage alert   |
| `binary_sensor.nice_mncut_contact_ouvert`       | Binary sensor | Open contact detected     |
| `binary_sensor.nice_mncut_capteur_declenche`    | Binary sensor | Motion sensor triggered   |
| `binary_sensor.nice_mncut_panique`              | Binary sensor | Panic alarm               |
| `binary_sensor.nice_mncut_mode_maintenance`     | Binary sensor | Maintenance mode          |
| `sensor.nice_mncut_etat_brut`                   | Sensor        | Raw state code from panel |
| `sensor.nice_mncut_zones_armees`                | Sensor        | Number of armed zones     |
| `sensor.nice_mncut_niveau_batterie`             | Sensor        | Battery level (%)         |
| `sensor.nice_mncut_delai_de_sortie`             | Sensor        | Exit delay countdown (s)  |

---

## Services

### `nice_mncut.clear_anomalies`

Acknowledges anomalies (tamper, open contact, etc.) to allow re-arming.

| Field   | Required | Default  | Description             |
| ------- | -------- | -------- | ----------------------- |
| `areas` | No       | `123456` | Zone IDs to acknowledge |

Example:

```yaml
service: nice_mncut.clear_anomalies
data:
  areas: "123456"
```

---

## Supported States

| HA State      | Description                 |
| ------------- | --------------------------- |
| `disarmed`    | Panel disarmed              |
| `arming`      | Exit delay in progress      |
| `armed_away`  | Fully armed (all zones)     |
| `armed_home`  | Partially armed (home mode) |
| `disarming`   | Disarm in progress          |
| `unavailable` | Panel unreachable           |

---

## Troubleshooting

**Integration not connecting:**

- Verify the IP address and that port 4012 is open
- Check HA logs: `Settings → System → Logs`, filter by `nice_mncut`

**Cannot re-arm after anomaly:**

- Use the `nice_mncut.clear_anomalies` service first

---

## 🤝 Contributing

Issues and contributions are welcome!

---

## ⚠️ Disclaimer

Not affiliated with Nice S.p.A.

---

## 📄 License

MIT License
