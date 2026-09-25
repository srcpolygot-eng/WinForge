# Contributing to WinForge

Thank you for your interest in improving WinForge!

## Ways to Contribute

- **New Toys** – the most valuable contribution. See [docs/creating-a-new-toy.md](docs/creating-a-new-toy.md).
- Bug reports and fixes
- Documentation improvements
- UI/UX polish
- Tests

## Development Setup

```powershell
git clone https://github.com/yourusername/WinForge.git
cd WinForge
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Run the application:

```powershell
python -m winforge
```

## Code Style

- Python 3.10+ features are fine.
- Prefer clarity over cleverness.
- Keep Toys self-contained.
- Do not introduce hard dependencies on third-party packages in core or V1 Toys unless there is a strong reason (and document it).
- Use the existing logging, config, backup, and error helpers instead of reinventing them.

## Pull Request Guidelines

1. One logical change per PR when possible.
2. If you add a Toy, include:
   - Working implementation
   - Clear UI
   - Metadata
   - Basic documentation (docstring + short note in README if it is a major Toy)
3. Test on a real Windows 10/11 machine before submitting.
4. Do not commit:
   - `__pycache__`, `.venv`, logs, user config, backups
   - Secrets or machine-specific paths
5. Update documentation when you change architecture or the Toy creation process.

## Safety Rules for Toys

- Prefer `HKEY_CURRENT_USER` over `HKEY_LOCAL_MACHINE`.
- Always create a backup before writing settings that the user might want to revert.
- Verify the result of write operations when practical.
- Surface friendly error messages via `ToyError`.
- Never perform irreversible destructive actions without explicit confirmation and a clear restore path.
- Declare `requires_admin`, `requires_windows_11`, and `min_windows_build` accurately in metadata.

## Questions?

Open an issue with the `question` label. For Toy design discussions, the issue tracker is preferred over private channels so future contributors can learn from the conversation.
