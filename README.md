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

## ⚙️ Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Nice MNCUT**
3. Enter IP address and PIN code

---

## 🖥️ Dashboard Examples

- Simple: `examples/dashboard_simple.yaml`
- Premium: `examples/dashboard_premium.yaml`

---

## 🤝 Contributing

Issues and contributions are welcome!

---

## ⚠️ Disclaimer

Not affiliated with Nice S.p.A.

---

## 📄 License

MIT License
