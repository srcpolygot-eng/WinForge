# WinForge Architecture

## High-Level View

```
┌─────────────────────────────────────────────────────────────┐
│                      WinForge Hub                           │
│  (tkinter main window – discovery, filtering, launch)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     ToyRegistry                             │
│  Scans winforge.toys.* packages, loads metadata + classes   │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     ┌─────────┐     ┌─────────┐     ┌─────────┐
     │  Toy A  │     │  Toy B  │     │  Toy C  │
     │  ┌───┐  │     │  ┌───┐  │     │  ┌───┐  │
     │  │UI │  │     │  │UI │  │     │  │UI │  │
     │  └─┬─┘  │     │  └─┬─┘  │     │  └─┬─┘  │
     │    ▼    │     │    ▼    │     │    ▼    │
     │ Logic   │     │ Logic   │     │ Logic   │
     │    ▼    │     │    ▼    │     │    ▼    │
     │ Win API │     │ Win API │     │ Win API │
     └─────────┘     └─────────┘     └─────────┘
```

## Package Layout

```
src/winforge/
├── __init__.py
├── __main__.py          # python -m winforge
├── app.py
├── core/
│   ├── config.py        # ConfigManager – hub + per-toy JSON
│   ├── backup.py        # BackupManager – snapshot before changes
│   ├── windows.py       # WindowsEnvironment detection, admin check
│   ├── logging.py       # Centralized logging
│   ├── errors.py        # WinForgeError hierarchy
│   └── toy_registry.py  # Discovery + metadata
├── ui/
│   ├── hub.py           # Main window + ToyWindow host
│   └── styles.py        # ttk theming
└── toys/
    ├── base.py          # BaseToy abstract class
    ├── file_extensions/
    ├── hidden_files/
    ├── taskbar_alignment/
    ├── god_mode/
    └── clipboard_history/
```

## Responsibilities

### Hub (`ui/hub.py`)

- Display available Toys (cards with name, description, status)
- Filter / categorize
- Launch each Toy in its own `Toplevel` window
- Persist its own window geometry
- Never contain Toy-specific logic

### ToyRegistry (`core/toy_registry.py`)

- Dynamically discovers packages under `winforge.toys`
- Expects each package to expose `get_toy_class() -> Type[BaseToy]`
- Collects `ToyMetadata` from the class attribute
- Provides lookup by id and grouping by category

**Important:** Adding a new Toy does **not** require editing the registry or the Hub. Discovery is automatic.

### BaseToy (`toys/base.py`)

Contract every Toy must satisfy:

| Member              | Purpose                                      |
|---------------------|----------------------------------------------|
| `metadata`          | Class-level `ToyMetadata` instance           |
| `create_ui(parent)` | Build and return the settings widget         |
| `get_setting` / `set_setting` / `save_user_config` | Per-toy persistence |
| `check_compatibility()` | Raise if OS requirements not met       |
| `on_open` / `on_close` | Optional lifecycle hooks                  |
| `get_status_text()` | Optional short status for the Hub card       |

### Individual Toy Package

Recommended layout:

```
toys/my_toy/
├── __init__.py      # exposes get_toy_class()
├── toy.py           # subclass of BaseToy + metadata
├── ui.py            # tkinter UI (Frame)
└── logic.py         # Windows registry / API / filesystem code
```

Separation of concerns:

- **UI** – presentation, user input, showing errors via messagebox
- **Logic** – pure Windows operations, raises `ToyError` on failure
- **Toy class** – wires UI + logic, holds config/backup references

### Core Services

| Service            | Used by          | Notes |
|--------------------|------------------|-------|
| ConfigManager      | Hub + every Toy  | JSON under `~/.winforge/config/` |
| BackupManager      | Toys that mutate | Snapshots under `~/.winforge/backups/` |
| WindowsEnvironment | Hub + Toys       | Cached detection of version, build, admin |
| Logging            | Everything       | `~/.winforge/logs/winforge.log` |
| Error hierarchy    | Everything       | `ToyError.user_message()` for UI |

## Data Flow for a Typical Setting Change

```
User clicks Apply in Toy UI
        │
        ▼
UI reads control values
        │
        ▼
UI (or Toy) creates backup via BackupManager
        │
        ▼
UI calls logic.set_*(desired_value)
        │
        ▼
logic writes registry / filesystem
        │
        ▼
logic notifies Explorer (if needed)
        │
        ▼
UI calls logic.verify_*()
        │
        ▼
UI shows success or clear error (ToyError.user_message)
        │
        ▼
Toy saves preferred setting to its config JSON
```

## Extension Points

Future Toys can:

1. Live entirely inside their own package (preferred).
2. Reuse core services without modification.
3. Optionally add shared UI widgets under `ui/` if a pattern is repeated often.
4. Declare requirements in metadata so the Hub and the Toy itself can show accurate compatibility messages.

## Design Principles

1. **Independence** – one broken Toy must not crash the Hub or other Toys.
2. **Discoverability** – no central hardcoded list of Toys.
3. **Honesty** – never claim a change succeeded without verification.
4. **Minimal core** – core stays small; complexity lives in Toys.
5. **Windows-first** – clear errors on non-Windows platforms instead of silent no-ops.
