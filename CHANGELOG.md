# Changelog

## 0.2.0

- Support Python 3.11–3.15 with pygame-ce, installed automatically as a dependency.
- Use uv for dependency management, Python installation, builds, and publishing; use Ruff for linting and formatting.
- Ship a runnable `pygameuikit-demo` command with all required assets.
- Fix text inputs receiving events through `Group`, Unicode input, editing-key repeat, and scrolling to the cursor.
- Fix slider positions for nonzero and negative ranges, step alignment, clamping, and click-to-seek.
- Fix image-button hover, optional callbacks, toggle state, and thread-status reset behavior.
- Fix dropdown sizing, selection callbacks, and clicks passing through open menus.
- Handle empty and all-zero charts without Seaborn or division errors.
- Create fonts lazily so importing the package doesn't initialize Pygame.
- Add headless regression tests, cross-platform CI, and tag-based releases.

### Upgrading from 0.1

Use a fresh virtual environment: pygame-ce and classic pygame share the `pygame` import name and must not be installed together. Python 3.7–3.10 are no longer supported.

Continue using `import pygame` and `from PygameUIKit import ...`. Forward every Pygame event once through `Group.handle_event`; text inputs now receive characters from `TEXTINPUT`, not `KEYDOWN.unicode`. Call `Group.update(dt)` with elapsed seconds for editing-key repeat and chart animation. Default fonts are created per widget; pass your own `pygame.font.Font` when you need to share one.
