# HaWake Alarm — Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![HA Min Version](https://img.shields.io/badge/HA-2024.1%2B-blue.svg)](https://www.home-assistant.io)

Control and monitor the **HaWake Alarm** iOS app from Home Assistant. Dismiss alarms, snooze, send full-screen alerts to your phone, automate alarm schedules, and expose alarm state as sensors — all over MQTT.

📖 **[Full documentation, entity reference, services, and example automations →](https://hawake.app/home-assistant.html)**

---

## ✅ Requirements

- [HaWake Alarm](https://apps.apple.com/app/hawake-alarm/id0000000000) iOS app (v2.0+)
- A running MQTT broker (e.g. Mosquitto via the HA add-on)
- The MQTT integration configured in Home Assistant
- The HaWake app connected to the same MQTT broker

## 📦 Installation

### Via HACS (recommended)

1. In Home Assistant, go to **HACS → Integrations → ⋮ → Custom repositories**
2. Add `https://github.com/domoretechnet/hawake-hacs` and select **Integration** as the category
3. Find **HaWake Alarm** in the HACS store and click **Download**
4. Restart Home Assistant

### Manual

1. Copy `custom_components/hawake/` into your HA `config/custom_components/` directory
2. Restart Home Assistant

## ⚡ Quick Setup

After installing, complete setup in four steps:

1. Create a dedicated MQTT user for the app in your Mosquitto broker
2. **Create an ACL file** restricting that user to `hawake/#` topics only — this is strongly recommended to keep the app isolated from the rest of your broker
3. Connect the HaWake iOS app (**Settings → MQTT Settings**) to your broker
4. Add the **HaWake Alarm** integration in **Settings → Devices & Services** and match the Device Name and Topic Prefix to what you set in the app

> **Defaults:** Device Name = `iPhone` · Topic Prefix = `hawake`

> ⚠️ **Skip the ACL at your own risk.** Without it, the HaWake app user has access to all topics on your broker. The full setup guide includes copy-ready Mosquitto config and ACL file contents.

**[Full setup guide with MQTT configuration, ACL setup, entity reference, services, and example automations →](https://hawake.app/home-assistant.html)**

## 🔗 Links

- [HaWake App](https://hawake.app)
- [Setup Guide & Documentation](https://hawake.app/home-assistant.html)
- [MQTT Payload Builder](https://hawake.app/mqtt-builder.html)
- [Report an issue](https://github.com/domoretechnet/hawake-hacs/issues)
