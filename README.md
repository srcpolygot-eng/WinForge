# WinForge

**Modular Windows customization and utilities suite**

Inspired by the modular concept of Microsoft PowerToys, WinForge provides a central hub where every feature is an independent **Toy**.

Each Toy has:

- Its own purpose
- Its own graphical UI
- Its own settings
- Its own implementation
- Independent testability
- Clean integration with the WinForge ecosystem

---

## What is a Toy?

A Toy is a self-contained module. Think of it as a small focused application that lives inside WinForge.

```
WinForge Hub
├── File Extensions          → own window, own settings
├── Hidden & System Files    → own window, own settings
├── Taskbar Alignment        → own window, own settings
├── God Mode                 → own window, own settings
└── Clipboard History        → own window, own settings
```

You open only the Toys you need. Nothing is forced into a single giant settings page.

---

## V1 Features

### Core

- Central graphical Hub with Toy discovery
- Clean modular architecture for easy extension
- Per-Toy configuration that survives restarts
- Backup / restore support for settings changes
- Windows version and environment detection
- Clear, user-friendly error messages
- No third-party runtime dependencies (stdlib + tkinter only)

### Included Toys

| Toy                    | Category  | Description                                      | Admin? |
|------------------------|-----------|--------------------------------------------------|--------|
| **File Extensions**    | Explorer  | Show or hide known file extensions               | No     |
| **Hidden & System Files** | Explorer | Toggle hidden and protected OS files          | No     |
| **Taskbar Alignment**  | Taskbar   | Left or center taskbar icons (**Windows 11 only**) | No     |
| **God Mode**           | Utility   | Create the classic God Mode settings folder      | No     |
| **Clipboard History**  | Utility   | Enable / disable Clipboard History (Win+V) – **Win10 1809+** | No   |

All Toys perform real Windows operations (registry / filesystem) and verify results where possible.

### OS compatibility summary

| Toy                    | Windows 8.1 | Windows 10 | Windows 11 |
|------------------------|:-----------:|:----------:|:----------:|
| File Extensions        | ✅          | ✅         | ✅         |
| Hidden & System Files  | ✅          | ✅         | ✅         |
| God Mode               | ✅          | ✅         | ✅         |
| Clipboard History      | ❌          | ✅ (1809+) | ✅         |
| Taskbar Alignment      | ❌          | ❌         | ✅         |

---

## Requirements

- **Windows 8.1, Windows 10, or Windows 11**
- **Python 3.10+** (3.11 or 3.12 recommended)
- `tkinter` (included with official Python installers on Windows)

> **Note:** WinForge is designed exclusively for Windows. The code can be inspected on other platforms, but Toys will report clear compatibility errors. Individual Toys declare their own minimum OS requirements and show friendly messages when those requirements are not met.

---

## Installation

### From source (recommended for V1)

```powershell
git clone https://github.com/srcpolygot-eng/WinForge.git
cd WinForge
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### Run

```powershell
winforge
# or
python -m winforge
```

---

## Quick Start

1. Launch WinForge.
2. Browse the list of Toys in the Hub.
3. Click **Open** on any Toy.
4. Adjust settings and click **Apply**.
5. Changes are applied immediately (some may require a refresh of Explorer).

Configuration is stored under:

```
%USERPROFILE%\.winforge\
├── config\
│   ├── hub.json
│   └── toys\
│       └── <toy_id>.json
└── backups\
    └── <toy_id>\
```

---

## Architecture Overview

```
WinForge
├── Hub (UI)
│   └── discovers Toys via ToyRegistry
│
├── Core
│   ├── ConfigManager
│   ├── BackupManager
│   ├── WindowsEnvironment detection
│   ├── Logging
│   └── Error hierarchy
│
└── Toys (each is a package)
    ├── metadata
    ├── UI (tkinter)
    ├── logic (Windows integration)
    └── optional config / docs
```

See [docs/architecture.md](docs/architecture.md) for details.

---

## Adding a New Toy

This is a first-class V1 feature.

**Read:**

- [docs/creating-a-new-toy.md](docs/creating-a-new-toy.md) – complete step-by-step guide with example
- [docs/toy-development-quick-reference.md](docs/toy-development-quick-reference.md) – short cheat sheet

In almost all cases you only need to create a new package under `src/winforge/toys/` and implement the required interface. The Hub discovers it automatically.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/architecture.md](docs/architecture.md) | System design and responsibilities |
| [docs/creating-a-new-toy.md](docs/creating-a-new-toy.md) | How to add a new Toy (detailed) |
| [docs/toy-development-quick-reference.md](docs/toy-development-quick-reference.md) | Quick checklist |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Common issues |

---

## Safety Philosophy

- Prefer per-user registry keys over machine-wide changes
- Create backups before applying impactful changes
- Verify operations when feasible
- Never claim success without verification
- Surface clear error messages instead of silent failures
- Avoid destructive operations

---

## License

MIT License – see [LICENSE](LICENSE).

---

## Status

**WinForge V1** establishes the foundation:

- Real working Hub
- Real modular Toy architecture
- Five real Toys
- Discovery, configuration, backup, and documentation for future growth

The repository is intentionally designed so that new Toys can be added by contributors without rewriting the core.
