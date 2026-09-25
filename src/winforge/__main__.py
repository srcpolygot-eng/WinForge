"""Entry point: python -m winforge"""

from __future__ import annotations

import sys


def main() -> int:
    # Guard early for non-Windows (still allow import for development)
    if sys.platform != "win32":
        print(
            "WinForge is designed for Microsoft Windows.\n"
            "You can still inspect the code and run unit tests on other platforms,\n"
            "but the GUI and Toys require Windows.",
            file=sys.stderr,
        )
        # Continue anyway so developers can see the UI skeleton on Linux/macOS
        # (registry calls will raise clear errors inside Toys).

    from winforge.ui.hub import WinForgeHub

    app = WinForgeHub()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
