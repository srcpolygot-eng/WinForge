# Toy Development Quick Reference

For developers who already understand WinForge architecture.

## 1. Create the package

```
src/winforge/toys/my_toy/
├── __init__.py
├── toy.py
├── ui.py
└── logic.py
```

## 2. `__init__.py`

```python
from winforge.toys.my_toy.toy import MyToy

def get_toy_class():
    return MyToy
```

## 3. Metadata (`toy.py`)

```python
metadata = ToyMetadata(
    id="my_toy",
    name="My Toy",
    description="…",
    category="Explorer",          # or Taskbar / Desktop / Utility / …
    version="1.0.0",
    requires_admin=False,
    requires_windows_11=False,
    min_windows_build=0,
    tags=("tag1", "tag2"),
    icon="🔧",
)
```

## 4. Implement UI (`ui.py`)

- Subclass `ttk.Frame`
- Accept `(parent, toy)`
- Provide Apply / Refresh
- Call `logic.*` and `toy.backup_manager` / `toy.set_setting`

## 5. Implement logic (`logic.py`)

- Guard with `sys.platform == "win32"`
- Raise `ToyError(toy_name=…, message=…, details=…, suggestion=…)`
- Provide `get_*`, `set_*`, `verify_*`

## 6. Wire it (`toy.py`)

```python
class MyToy(BaseToy):
    metadata = …
    def create_ui(self, parent):
        self.check_compatibility()
        return MyToyUI(parent, self)
```

## 7. Discovery

Automatic. No other files need editing.

## 8. Test

```powershell
python -c "from winforge.core.toy_registry import ToyRegistry; print(ToyRegistry().list_ids())"
python -m winforge
```

## 9. Document

Update `ToyMetadata.description` and optionally the root README table.

## Common imports

```python
from winforge.core.toy_registry import ToyMetadata
from winforge.toys.base import BaseToy
from winforge.core.errors import ToyError
```
