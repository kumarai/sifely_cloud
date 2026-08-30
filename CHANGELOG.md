# 📝 Changelog

Notable changes to this project documented here.
---
## [1.3.0] - 2026-08-30
### Changed
- Migrated authentication and API calls to Sifely's Open API (`https://cus-openapi.sifely.com`).
- Login now POSTs JSON `{"account", "password"}` (MD5 hex) to `/system/smart/login` and accepts both wrapped `code/data` and unwrapped `clientToken` bodies.
- Open API `sk-` keys are sent as the raw `Authorization` value (no `Bearer` prefix). Legacy tokens still use `Bearer`.
- Config flow no longer uses legacy `loginByGuest` / form-urlencoded against `app-smart-server.sifely.com`.
- Domain remains `sifely_cloud` so existing Home Assistant entities keep working.

### Notes
- New Sifely accounts need the free Developer plan at https://connect.sifely.com.
- This fork keeps Ken Jensen's MIT license and credit from [kenster1965/sifely_cloud](https://github.com/kenster1965/sifely_cloud).

---
## [1.2.0] - 2025-09-18
### Bug Fix
- Ticket #23 / Fails to connect to server if the client id hasn't been previously generated.  Updated error message and help files.

---
## [1.1.1] - 2025-07-31
### Bug Fix
- During version updates the token did not re-fresh, Now performs force token re-fresh on HA reboots. 

---
## [1.1.0] - 2025-07-30
### Updated
- Simplified creation, now auto finds user clientId on install
- Updated translations, now easy for other to add languages
- Perform history pull up front, no more waiting
- Update all api Entities calls to be normilized for HA
### Added
- Added Diagnostics download, makes reporting a problem easier
- Added per Lock Revisions and versions sensor
### Note
- (Yes Sifely icons submitted, just waintg HA approval)

---
## [1.0.3] - 2025-07-27
### Added
- Setup git bug, ferature, issue reporting
- Added git LICENSE
- Adding git formats
- Updated directory structure for manual download in to HA
- Create CODEOWNERS
- Update readme
- Hacs integration
- Fixed manifest.json

---
## [1.0.0] – 2025-07-22
### Added
- Initial public release of `sifely_cloud`
- Lock discovery via `/v3/key/list`
- Entity setup for:
  - Battery sensor
  - Lock state and control
  - Open/closed sensor
  - Lock history with CSV persistence
  - Cloud error tracking
  - Privacy lock and tamper alert binary sensors
- Lock history auto-refresh every 5 minutes
- UI-friendly integration with diagnostics and YAML options





