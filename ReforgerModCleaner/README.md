# Reforger Mod Cleaner

**[Türkçe](docs/README.tr.md)** · English

> **Unofficial fan-made tool.** Not affiliated with or authorized by Bohemia Interactive a.s. Arma, Arma Reforger, Bohemia Interactive and all associated logos and designs are trademarks or registered trademarks of Bohemia Interactive a.s.

A Windows desktop tool for the Arma Reforger **client** mod folder (`Documents\My Games\ArmaReforger\addons`). It lists your downloaded Workshop mods, lets you tag them by the server you play on, shows which mods other mods depend on, and sends the ones you no longer need to the Recycle Bin.

The interface is available in **English and Turkish**. It starts in your Windows language, and the **Language** button in the toolbar switches it at any time.

<!-- Add a screenshot before publishing: save it as docs/screenshot.png and remove this comment line.
![Screenshot](docs/screenshot.png)
-->

## Features

- **Mod list**: name, version, size, date and server tag. Click a column header to sort.
- **Server tags**:
  - Double-click a row to tag it, or tag several selected rows at once.
  - Paste a mod list or the in-game mod preset JSON to tag all matching mods.
  - Point the tool at a folder of server `config.json` files and it tags mods automatically on every start. On startup, tags you set by hand are never overwritten; when you first select the folder, you are asked whether to overwrite them.
- **Dependency tracking**: reads `dependencies` from each mod's `ServerData.json`. Mods that other mods need are marked ⛓, and deleting one triggers a warning.
- **Size map**: a treemap of disk usage, coloured by server.
- **Safe delete**: mods go to the Recycle Bin, not permanent deletion. You get a warning if the game is running.
- **Offline**: no network access, no telemetry.

## Requirements

- Windows 10 or 11
- Running the exe: nothing else
- Running from source or building the exe locally: Python 3.9 or newer

## Installation

### Option 1: prebuilt exe

Download `ReforgerModCleaner.exe` from [Releases](../../releases/latest) and double-click it. You don't need to install anything, not even Python: the exe bundles everything it needs. The exe is built automatically from this repository's source code by GitHub Actions; see [`.github/workflows/build.yml`](.github/workflows/build.yml).

**Windows SmartScreen / antivirus warning:** the exe is not code-signed and is packed with PyInstaller. Both of these commonly trigger "Windows protected your PC" or false-positive antivirus detections. To run it, click *More info → Run anyway*. If you don't trust the binary, use option 2 or 3; they produce the same program from this source code. Each release includes a `SHA256.txt` so you can verify the download:

```
certutil -hashfile ReforgerModCleaner.exe SHA256
```

### Option 2: build the exe yourself

Download the repository, then double-click `build.bat` inside it. The output is `dist\ReforgerModCleaner.exe`.

### Option 3: run from source

```
pip install -r requirements.txt
pythonw reforger_mod_cleaner.py
```

`pythonw` runs without a console window. Use `python` instead if you want to see errors in the console.

## Usage

1. The `addons` folder is detected automatically, including OneDrive-redirected Documents folders. If detection fails, pick the folder with **Folder**.
2. Tag the mods of the servers you play on:
   - In game, open the mod preset, copy its JSON, then use **Auto-Tag**: paste the JSON and enter a server name.
   - Or select the folder holding your server `config.json` files with **Server Config Folder**.
3. **Select Untagged** selects every mod that is untagged and that no other mod depends on. These rows are shown in red. Review the selection before going further.
4. **Delete Selected** sends the selection to the Recycle Bin. If you deleted something by mistake, restore it from there.

A red row does **not** mean the mod is safe to delete. It means you haven't tagged it yet, so tag your servers' mods first and only then clean up.

### How mods are identified

Every subfolder of `addons` holds a `ServerData.json` that contains the mod's `id`, `name`, `revision.version` and `revision.dependencies`. The tool reads these fields. Tag matching uses **exact** mod ID or **exact** mod name, never partial names: "ACE" will not match "Peace Keeper".

## Data and privacy

| What | Where |
|---|---|
| Tags and settings (language, background path, server config folder) | `%APPDATA%\ReforgerModCleaner\` |
| Error log | `%TEMP%\ReforgerModCleaner.log` |

Nothing else is written, and nothing is sent anywhere. The **Wipe Local Data** button deletes the tags and settings. It does not touch mod files.

**Uninstall:** delete the exe, the `%APPDATA%\ReforgerModCleaner\` folder, and the log file.

## Known limitations

- The window has a fixed size. It shrinks automatically to fit a 1366×768 screen, but smaller screens are cropped.
- At Windows display scaling of 125% or more, Windows upscales the window, so it may look slightly blurry.
- Only the client `addons` folder is supported. Dedicated server profile folders are not scanned.
- The Yes/No buttons of confirmation dialogs follow the Windows language, not the in-app language setting.

## Repository layout

| Path | Contents |
|---|---|
| `reforger_mod_cleaner.py` | The whole application (single file) |
| `assets/` | Background image and icon bundled into the exe |
| `tests/` | Automated tests (no window is opened) |
| `docs/` | Turkish README, changelog, third-party notices |
| `build.bat` | Builds the exe locally |
| `.github/workflows/build.yml` | Builds, smoke-tests and publishes the exe on GitHub |
| `requirements.txt`, `requirements-dev.txt` | Runtime and development dependencies |

## Development

```
pip install -r requirements.txt -r requirements-dev.txt
python -m pyflakes reforger_mod_cleaner.py tests
python -m pytest -q tests
```

The tests don't open a window. They cover the data functions, the scan and delete flows, both languages, and the whole window-building code using a fake Tk.

To add or change interface text, edit the `STRINGS` table in `reforger_mod_cleaner.py`. Both languages must have the same keys; a test enforces this.

### Publishing a release (no command line needed)

1. Update `APP_VERSION` in `reforger_mod_cleaner.py` and add an entry to `docs/CHANGELOG.md`, then commit.
2. On GitHub, go to **Releases → Draft a new release**, create the tag `v<APP_VERSION>` (for example `v1.0.0`) and click **Publish release**.
3. GitHub Actions then runs the tests, builds the exe, checks that it starts, and attaches `ReforgerModCleaner.exe` and `SHA256.txt` to the release, all within a few minutes. If the tag and `APP_VERSION` don't match, the build fails.

Every push to `main` is also built; download that exe from the run's **Artifacts** section on the **Actions** tab.

## Reporting a problem

Open an issue and attach `%TEMP%\ReforgerModCleaner.log`. The log contains only folder paths and mod names. Folder paths include your Windows user name (`C:\Users\<name>`), so redact it if you prefer.

## License

The code is released under the [MIT](LICENSE) license. The prebuilt exe bundles third-party components that remain under their own licenses; see [THIRD_PARTY_NOTICES.md](docs/THIRD_PARTY_NOTICES.md). The background and icon images were AI-generated by the author and are released under the same MIT license. See the [changelog](docs/CHANGELOG.md) for version history.
