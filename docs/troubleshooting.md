# Troubleshooting

## WinForge will not start

- Confirm Python 3.10+ is installed and on PATH.
- Confirm `tkinter` is available:
  ```powershell
  python -c "import tkinter; print(tkinter.TkVersion)"
  ```
  If this fails, reinstall Python from python.org and tick “tcl/tk”.

## A Toy does not appear in the Hub

1. Check that the package is under `src/winforge/toys/<name>/` and contains `__init__.py` with `get_toy_class()`.
2. Run discovery manually:
   ```powershell
   python -c "from winforge.core.toy_registry import ToyRegistry; r=ToyRegistry(); r.discover(); print(r.list_ids())"
   ```
3. Look at `~/.winforge/logs/winforge.log` for import errors.

## “Requires Windows 11” or version errors

The Toy’s metadata declares a minimum build or Windows 11 requirement. The message is intentional.

- **Taskbar Alignment** works only on Windows 11.
- **Clipboard History** requires Windows 10 version 1809 (build 17763) or later; it is not available on Windows 8.1.
- File Extensions, Hidden & System Files, and God Mode work on Windows 8.1, 10, and 11.

Use a different Toy or upgrade Windows if you need a restricted feature.

## Changes do not appear in File Explorer

- Press F5 in an open Explorer window.
- Open a new Explorer window.
- For taskbar changes, the Toy may restart Explorer automatically; if not, sign out and back in.

## Permission errors

Most V1 Toys use per-user registry keys and do **not** require administrator rights. If you see a permission error:

- Confirm you are not running under a restricted account.
- Avoid “Run as administrator” unless a future Toy explicitly asks for it.

## Corrupt configuration

Delete the offending file under:

```
%USERPROFILE%\.winforge\config\toys\<toy_id>.json
```

WinForge will recreate it with defaults on next use. A `.json.corrupt` backup is kept automatically when parse errors occur.

## Logs

```
%USERPROFILE%\.winforge\logs\winforge.log
```

Increase verbosity by calling `setup_logging(level=logging.DEBUG)` early if you are developing.
