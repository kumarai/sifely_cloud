# Sifely Cloud — Home Assistant Integration (Open API fork)

A **custom HACS integration** for Home Assistant that connects to **Sifely smart locks** using Sifely's current Open API (`https://cus-openapi.sifely.com`).

This repository is a **fork** of [kenster1965/sifely_cloud](https://github.com/kenster1965/sifely_cloud) by Ken Jensen (MIT). The Home Assistant domain remains **`sifely_cloud`** so existing entities keep working.

Sifely closed **new-user** access on the legacy `app-smart-server.sifely.com` API on **2026-06-17**. This fork talks to the [Sifely Open API](https://apidocs.sifely.com) instead.

![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)
[![GitHub release](https://img.shields.io/github/v/tag/kumarai/sifely_cloud?label=version)](https://github.com/kumarai/sifely_cloud/tags)
[![License](https://img.shields.io/github/license/kumarai/sifely_cloud)](https://github.com/kumarai/sifely_cloud/blob/main/LICENSE)
[![Report Issue](https://img.shields.io/badge/Report-Issue-blue)](https://github.com/kumarai/sifely_cloud/issues/new/choose)

- [API Documentation](#-api-documentation)
- [Requirements](#-requirements)
- [Features](#-features)
- [UI Screenshots](#-ui-screenshots)
- [Installation](#-installation)
- [Configuration Options](#-configuration-options)
- [Developer Configuration via `const.py`](#-developer-configuration-via-constpy)
- [Entities Created](#-entities-created)
- [File Persistence](#-file-persistence)
- [Roadmap](#-roadmap)
- [Contributing / Issues](#-contributing--issues)
- [Credits](#-credits)
- [Disclaimer](#-disclaimer)
- [License](#-license)

## 📚 API Documentation

This integration uses the official Open API:

- Docs: [https://apidocs.sifely.com](https://apidocs.sifely.com)
- Base URL: `https://cus-openapi.sifely.com`
- Login: `POST /system/smart/login` with JSON `{"account", "password"}` (password is MD5-hex of the plaintext password)

Open API keys start with `sk-` and must be sent as the raw `Authorization` header value (**no `Bearer` prefix**). Legacy tokens still use `Bearer`. You do **not** put API keys in this git repository — Home Assistant stores credentials in its config entry / `.storage` (gitignored).

---

## ✅ Requirements

1. A Sifely lock-owner account (the same **email and password** you use in the Sifely app).
2. A subscription to the **free Developer plan** at [https://connect.sifely.com](https://connect.sifely.com). Without an active plan, Open API calls return `402`.
3. Home Assistant with [HACS](https://hacs.xyz/) (or a manual `custom_components` install).

Do **not** commit `sk-` keys, passwords, emails, HA `.storage`, or logs to git.

---

## 📦 Features
- 🔐 **Lock/Unlock support**
- 🔋 **Battery level monitoring**
- 📖 **Historical event logging** (username, method, success/fail)
- 🚨 **Cloud error diagnostics**
- 🧠 **Open/closed state polling**
- 👁 **Privacy Lock** and **Tamper Alert** binary sensors
- 💾 **Persisted history** with CSV logging
- 🕓 **Automatic background polling**
- 🧰 Compatible with **Entity Category Diagnostics** for advanced insights
- 🧪 **Unified Diagnostic Sensor** for firmware/hardware details and lock flags
- 🗂 **Diagnostics file download** for better troubleshooting via GitHub

---

## 🖼️ UI Screenshots
Below are examples of how entities appear in the Home Assistant UI. These include:

- Integration setup screen  
  <img src="images/config_options.jpg" alt="config_options" width="300px">

- Lock Control, Battery, Privacy Lock, Tamper Alert sensors, ...  
  <img src="images/panel.jpg" alt="panel" width="300px">  
  <img src="images/show_locked.jpg" alt="show_locked" width="300px">
  <img src="images/logbook.jpg" alt="logbook" width="300px">  
  <img src="images/diagnostic_sensor.jpg" alt="diagnostic_sensor" width="300px">

- Lock history sensor with structured entries  
  <img src="images/history.jpg" alt="history" width="300px">
  <img src="images/access_history.jpg" alt="access_history" width="300px">

---

## 🔧 Installation

### Via HACS (custom repository)

1. Subscribe to the free Developer plan at [https://connect.sifely.com](https://connect.sifely.com).
2. In HACS, add this repo as a **custom repository** (category: Integration): `https://github.com/kumarai/sifely_cloud`
3. Install **Sifely Cloud**, then restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and search for **Sifely Cloud**.
5. Sign in with your Sifely app / lock-owner **email and password**.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kumarai&repository=sifely_cloud&category=integration)

### Manual Installation

1. Subscribe to the free Developer plan at [https://connect.sifely.com](https://connect.sifely.com).
2. Open the directory for your HA configuration (where you find `configuration.yaml`).
3. If you do not have a `custom_components` directory there, create it.
4. In `custom_components` create a folder called `sifely_cloud`.
5. Copy the files from this repository's `custom_components/sifely_cloud/` directory into that folder.
6. Restart Home Assistant.
7. Navigate to **Settings → Devices & Services → Integrations**.
   Click ➕ Add Integration → Search for **Sifely Cloud**.
8. Enter your Sifely app / lock-owner email and password.

The integration domain is `sifely_cloud`. After a HACS/manual update, existing lock entities keep the same unique IDs.

---

## 🛠 Configuration Options
- **Email / Password** – Sifely app / lock-owner credentials (not a key pasted into git)
  - The integration logs in to the Open API and stores the returned token in the Home Assistant config entry
  - After setup, **Configure** still shows the Client ID field for advanced/legacy options
- **Number of Locks (APX)** – Approximate number of locks to query
- **Number of History Entries** – Maximum recent events to retain (default: `20`)

---

## 🛠 Developer Configuration via `const.py`
Advanced users and developers can override default settings by editing the `const.py` file directly. This includes:
- Polling intervals
- Maximum number of retries
- History record type labels
- Default limits for entities and diagnostics
- Error thresholds before token refresh
- 🔧 View all current const values through diagnostics

---

## 🧪 Entities Created
| Entity Type      | Description                            | Notes                                                    |
|------------------|----------------------------------------|----------------------------------------------------------|
| `lock`           | Lock/unlock control for Sifely lock    |                                                          |
| `sensor`         | Battery level sensor                   |                                                          |
| `sensor`         | Recent lock/unlock history             | Usernames from online entries are trimmed removing hash. |
| `sensor`         | Diagnostic sensor                      | Shows firmware/hardware versions + lock state flags      |
| `binary_sensor`  | Privacy Lock status sensor             |                                                          |
| `binary_sensor`  | Tamper Alert status sensor             |                                                          |
| `sensor`         | Cloud error diagnostics (connectivity) | Shows error info for cloud token or API issues.          |

---

## 📄 Diagnostics File Download
When reporting bugs, please include a diagnostic file:

### 📥 How to Download Diagnostics
1. Go to **Settings → Devices & Services**
2. Locate the **Sifely Cloud** integration
3. Click the **⋮ (three-dot menu)** and select **Download Diagnostics**
4. Save the file and attach it to your GitHub bug report

This file includes:
- Lock metadata (firmware/hardware versions)
- API response codes
- Entity states
- Configuration flags from `const.py`

> 🔐 Sensitive information such as passwords and tokens are automatically redacted.

---

## 📁 File Persistence
- Historical records are saved to:

`config/custom_components/sifely_cloud/history/history_<lockId>.csv`

- Only *new* records are appended; existing entries are deduplicated based on `recordId`.

---

## 🚧 Roadmap
See the [ROADMAP.md](./ROADMAP.md) for upcoming features and ideas.

---

## 🧑‍💻 Contributing / Issues
Got a feature request, bug report, or enhancement idea?

- 🐞 [Open an issue](https://github.com/kumarai/sifely_cloud/issues) on this fork
- Upstream project: [kenster1965/sifely_cloud](https://github.com/kenster1965/sifely_cloud)
- Pull requests are welcome
- Follow Home Assistant [developer documentation](https://developers.home-assistant.io/) when contributing code

---

## 🙏 Credits
- **Ken Jensen ([kenster1965](https://github.com/kenster1965))** — original `sifely_cloud` integration, MIT License
- This fork maintains Ken's code, domain, and license, and adds Open API support for accounts created after the legacy API closed to new users.

---

## 📜 Disclaimer
- This is an independent project and is **not affiliated with Sifely**.
- Use at your own risk. API behavior may change without notice.
- Sifely and its trademarks and registered trademarks including the images in this repository, are property of their respective owners. All images in this repository are used by the Home Assistant project for identification purposes only.

---

## 📄 License
[MIT License](LICENSE) — Copyright (c) 2025 Ken Jensen. This fork is distributed under the same MIT terms.
