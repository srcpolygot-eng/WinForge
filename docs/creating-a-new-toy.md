# How to Create a New Toy

This document is the definitive guide for adding a new Toy to WinForge.
Follow it exactly and your Toy will appear in the Hub automatically.

---

## 1. Where does the new Toy go?

Create a new **package** (directory with `__init__.py`) under:

```
src/winforge/toys/
└── my_new_toy/          ← snake_case, descriptive
```

**Naming conventions**

| Item              | Convention                          | Example                |
|-------------------|-------------------------------------|------------------------|
| Package directory | snake_case                          | `dark_mode_toggle`     |
| Toy id (metadata) | same as package name                | `dark_mode_toggle`     |
| Class name        | PascalCase + `Toy`                  | `DarkModeToggleToy`    |
| Display name      | Title Case                          | `Dark Mode Toggle`     |

---

## 2. What files should a Toy contain?

Minimum viable set:

```
src/winforge/toys/my_new_toy/
├── __init__.py      # REQUIRED – exposes get_toy_class()
├── toy.py           # REQUIRED – BaseToy subclass + metadata
├── ui.py            # REQUIRED – tkinter settings panel
└── logic.py         # HIGHLY RECOMMENDED – Windows integration
```

### Purpose of each file

| File         | Responsibility |
|--------------|----------------|
| `__init__.py`| Must define `get_toy_class()` that returns your Toy class. This is how the registry discovers you. |
| `toy.py`     | Defines the `ToyMetadata`, inherits `BaseToy`, implements `create_ui()`, optional status helpers. |
| `ui.py`      | Builds the graphical interface (a `ttk.Frame` or subclass). Handles user interaction and shows success/error dialogs. |
| `logic.py`   | Contains the actual Windows operations (registry, filesystem, ctypes, etc.). Should raise `ToyError` on failure and stay free of UI code. |

Optional later additions:

- `config.py` – if the Toy has complex default configuration
- `tests/` – unit tests for logic
- `README.md` – Toy-specific notes

---

## 3. How do I implement the Toy UI?

### Location

Put the UI class in `ui.py`.

### Creating the window

You do **not** create a `Toplevel` yourself. The Hub does that.

Your job is to return a widget from `create_ui(parent)`:

```python
# toy.py
def create_ui(self, parent: tk.Misc) -> tk.Widget:
    self.check_compatibility()          # optional but recommended
    return MyNewToyUI(parent, self)     # your Frame
```

### Typical UI structure

```python
# ui.py
import tkinter as tk
from tkinter import ttk, messagebox

class MyNewToyUI(ttk.Frame):
    def __init__(self, parent, toy):
        super().__init__(parent, padding=16)
        self.toy = toy
        self._build()
        self.refresh_state()

    def _build(self):
        # Header
        ttk.Label(self, text="My New Toy", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        # Description
        # Status LabelFrame
        # Controls (checkboxes, radiobuttons, entries…)
        # Apply / Refresh / Reset buttons
        # Notes / requirements text

    def refresh_state(self):
        # Read current system state via logic.py and update controls

    def _on_apply(self):
        # 1. Read controls
        # 2. Backup current state
        # 3. Call logic
        # 4. Verify
        # 5. Save preference to toy config
        # 6. Show messagebox
```

### Communicating with logic

```python
from winforge.toys.my_new_toy import logic

# inside _on_apply
current = logic.get_something()
self.toy.backup_manager.create_backup(self.toy.metadata.id, "before_apply", {"value": current})
logic.set_something(desired)
if logic.verify(desired):
    messagebox.showinfo("Success", "…", parent=self)
else:
    messagebox.showwarning("Verification", "…", parent=self)
```

### Loading / saving settings

```python
# Load a previously saved preference
preferred = self.toy.get_setting("preferred_value", default=True)

# After successful apply
self.toy.set_setting("preferred_value", desired)
self.toy.save_user_config()
```

---

## 4. How do I implement the actual Windows customization?

Follow the three-layer flow:

```
UI  →  Toy logic  →  Windows integration
```

- **UI** (`ui.py`) – never import `winreg` or call Windows APIs directly.
- **Logic** (`logic.py`) – owns all registry / filesystem / ctypes code.
- **Toy class** – thin coordinator.

Example logic pattern:

```python
# logic.py
import sys
from winforge.core.errors import ToyError

def get_value() -> bool:
    if sys.platform != "win32":
        raise ToyError(toy_name="My Toy", message="Windows only.")
    import winreg
    # … read and return

def set_value(value: bool) -> None:
    # … write
    # optionally notify Explorer / restart process

def verify(expected: bool) -> bool:
    try:
        return get_value() == expected
    except Exception:
        return False
```

Always:

- Check `sys.platform == "win32"` early.
- Raise `ToyError` (with `details` and `suggestion`) instead of letting raw exceptions bubble to the user.
- Prefer `HKEY_CURRENT_USER` over machine-wide keys.

---

## 5. How do I register / discover the Toy?

**You don’t manually register anything.**

The `ToyRegistry` does this:

1. Scans every sub-package of `winforge.toys`.
2. Imports the package.
3. Calls `get_toy_class()`.
4. Reads the `metadata` attribute of the returned class.
5. Adds it to the internal maps.

Therefore the only required “registration” code is inside your `__init__.py`:

```python
# src/winforge/toys/my_new_toy/__init__.py
from winforge.toys.my_new_toy.toy import MyNewToy

def get_toy_class():
    return MyNewToy
```

---

## 6. What files must be changed elsewhere?

**None**, for a normal Toy.

| Location              | Need to edit? | Notes |
|-----------------------|---------------|-------|
| `core/toy_registry.py`| No            | Auto-discovery |
| `ui/hub.py`           | No            | Reads from registry |
| `core/config.py`      | No            | Per-toy files are created on demand |
| Build / pyproject     | No            | Package discovery is dynamic |
| README.md             | Optional      | Nice to list major new Toys |

If your Toy needs a new shared helper that many future Toys will use, you may add it under `core/`. That is the only time a core file changes.

---

## 7. How do I add settings?

Use the helpers inherited from `BaseToy`:

```python
self.set_setting("key", value)
self.save_user_config()          # writes ~/.winforge/config/toys/<id>.json

value = self.get_setting("key", default=None)
```

Defaults can live in the UI (hard-coded sensible defaults) or in a small `DEFAULTS` dict inside the Toy class. There is no global defaults file that every Toy must edit.

---

## 8. How do I add backup / restore?

When your Toy is about to change a system setting:

```python
current = logic.get_value()
self.toy.backup_manager.create_backup(
    self.toy.metadata.id,
    "before_apply",
    {"value": current},          # any JSON-serializable dict
)
# … then apply the change
```

Later you can list or restore:

```python
backups = self.toy.backup_manager.list_backups(self.toy.metadata.id)
data = self.toy.backup_manager.restore_latest(self.toy.metadata.id)
```

For simple Toys a “Reset to previous” button that loads the latest backup is enough. More advanced Toys can show a list of backups.

---

## 9. How do I test the Toy?

Concrete checklist:

1. **Import test** (any platform)
   ```powershell
   python -c "from winforge.toys.my_new_toy import get_toy_class; print(get_toy_class().metadata)"
   ```

2. **Discovery test**
   ```powershell
   python -c "from winforge.core.toy_registry import ToyRegistry; r=ToyRegistry(); print(r.list_ids())"
   ```
   Your id must appear.

3. **On a real Windows machine**
   - Launch `python -m winforge`
   - Confirm the Toy card appears with correct name / category / icon
   - Open the Toy
   - Verify current state is read correctly
   - Change a setting → Apply → confirm the system actually changed
   - Restart WinForge → confirm preference is remembered
   - Force an error (e.g. wrong Windows version) → confirm friendly message appears
   - If the Toy creates files, test Remove / cleanup

4. **Non-Windows smoke test** (optional)
   - Confirm the Hub still starts and shows a clear “Windows only” or compatibility message inside the Toy.

---

## 10. How do I add the Toy to the WinForge UI?

It happens **automatically** through discovery.

After you create the package and implement `get_toy_class()`, restart WinForge. The new card appears in the Hub. No code changes in the Hub are required.

---

## 11. How do I document the Toy?

Minimum:

- Clear `description` and `tags` inside `ToyMetadata`
- Docstrings on the Toy class and public logic functions
- If the Toy has non-obvious requirements or side-effects, mention them in the UI (a short note at the bottom of the panel is perfect)

Optional but appreciated:

- A short paragraph in the root `README.md` table of Toys
- A dedicated section in a future `docs/toys/` folder

---

## 12. Complete Example – ExampleToy

Below is a minimal but complete Toy that toggles a fictional setting. Copy the structure and replace the logic with real Windows code.

### Folder

```
src/winforge/toys/example_toy/
├── __init__.py
├── toy.py
├── ui.py
└── logic.py
```

### `__init__.py`

```python
"""Example Toy – demonstrates the minimal Toy structure."""

from winforge.toys.example_toy.toy import ExampleToy


def get_toy_class():
    return ExampleToy
```

### `toy.py`

```python
from __future__ import annotations

import tkinter as tk

from winforge.core.toy_registry import ToyMetadata
from winforge.toys.base import BaseToy
from winforge.toys.example_toy.ui import ExampleToyUI


class ExampleToy(BaseToy):
    metadata = ToyMetadata(
        id="example_toy",
        name="Example Toy",
        description="A minimal example that shows how to structure a new Toy.",
        category="Utility",
        version="1.0.0",
        requires_admin=False,
        tags=("example", "demo"),
        icon="🧪",
    )

    def create_ui(self, parent: tk.Misc) -> tk.Widget:
        self.check_compatibility()
        return ExampleToyUI(parent, self)

    def get_status_text(self) -> str:
        return "Demo"
```

### `logic.py`

```python
"""Simulated logic for the Example Toy.

In a real Toy this file would contain winreg / ctypes / filesystem code.
"""

from __future__ import annotations

import sys
from winforge.core.errors import ToyError

# In-memory fake state for demonstration
_state = {"enabled": False}


def is_enabled() -> bool:
    if sys.platform != "win32":
        # Still allow the demo to run for documentation screenshots
        return _state["enabled"]
    return _state["enabled"]


def set_enabled(value: bool) -> None:
    _state["enabled"] = value


def verify(expected: bool) -> bool:
    return is_enabled() == expected
```

### `ui.py`

```python
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from winforge.toys.example_toy import logic

if TYPE_CHECKING:
    from winforge.toys.example_toy.toy import ExampleToy


class ExampleToyUI(ttk.Frame):
    def __init__(self, parent: tk.Misc, toy: "ExampleToy") -> None:
        super().__init__(parent, padding=16)
        self.toy = toy
        self._build()
        self.refresh_state()

    def _build(self) -> None:
        ttk.Label(self, text="Example Toy", font=("Segoe UI", 16, "bold")).pack(
            anchor="w", pady=(0, 4)
        )
        ttk.Label(
            self,
            text="This is a minimal demonstration Toy. Replace the logic with real Windows code.",
            wraplength=460,
        ).pack(anchor="w", pady=(0, 16))

        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var).pack(anchor="w", pady=(0, 12))

        self.enabled_var = tk.BooleanVar()
        ttk.Checkbutton(
            self, text="Enable example feature", variable=self.enabled_var
        ).pack(anchor="w", pady=(0, 16))

        btn = ttk.Frame(self)
        btn.pack(fill="x")
        ttk.Button(btn, text="Apply", command=self._on_apply).pack(side="left", padx=(0, 8))
        ttk.Button(btn, text="Refresh", command=self.refresh_state).pack(side="left")

    def refresh_state(self) -> None:
        enabled = logic.is_enabled()
        self.enabled_var.set(enabled)
        self.status_var.set("Currently: " + ("Enabled" if enabled else "Disabled"))

    def _on_apply(self) -> None:
        desired = self.enabled_var.get()
        try:
            current = logic.is_enabled()
            self.toy.backup_manager.create_backup(
                self.toy.metadata.id, "before_apply", {"enabled": current}
            )
            logic.set_enabled(desired)
            if logic.verify(desired):
                messagebox.showinfo("Success", "Example setting updated.", parent=self)
            else:
                messagebox.showwarning("Verification", "Could not verify.", parent=self)
            self.toy.set_setting("preferred", desired)
            self.toy.save_user_config()
            self.refresh_state()
        except Exception as exc:
            from winforge.core.errors import ToyError
            msg = exc.user_message() if isinstance(exc, ToyError) else str(exc)
            messagebox.showerror("Error", msg, parent=self)
```

### After creating the files

1. Restart WinForge (or re-run discovery).
2. The card “Example Toy” appears under the Utility category.
3. Open it, toggle the checkbox, click Apply.

You have successfully added a Toy without touching any core or Hub files.

---

## Summary Checklist

- [ ] Created `src/winforge/toys/<snake_name>/`
- [ ] Added `__init__.py` with `get_toy_class()`
- [ ] Implemented `toy.py` with `ToyMetadata` and `create_ui`
- [ ] Implemented `ui.py` with a `ttk.Frame` subclass
- [ ] Implemented `logic.py` with real Windows code (or a safe simulation)
- [ ] Used `backup_manager` before changing system state
- [ ] Used `ToyError` for user-facing failures
- [ ] Verified the Toy appears in the Hub after restart
- [ ] Tested apply / refresh / config persistence on Windows

You are done. Welcome to the WinForge contributor list!
