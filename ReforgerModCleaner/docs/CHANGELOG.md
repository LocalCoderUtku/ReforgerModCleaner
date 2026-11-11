# Changelog

## [1.0.0] — 2026-11-11

First public release. / İlk açık sürüm.

- Turkish and English interface, switchable from the toolbar (defaults to the Windows language)
- Mod list with name, version, size, date and server tag; sortable columns
- Server tagging: manual, bulk, from pasted mod list / mod preset JSON, from server `config.json` folder
- Dependency tracking from `ServerData.json`; warning before deleting a mod other mods need
- Size treemap coloured by server
- Delete to Recycle Bin (send2trash), warning if the game is running
- Data stored in `%APPDATA%\ReforgerModCleaner\`, error log in `%TEMP%\ReforgerModCleaner.log`
- Exe built, smoke-tested and attached to releases automatically by GitHub Actions
