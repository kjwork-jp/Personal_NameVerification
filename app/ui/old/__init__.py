"""Compatibility package for legacy UI modules.

Only modules that still exist should be imported explicitly by their consumers.
This package initializer must stay side-effect free so importing
`app.ui.old.title_subtitle_management_tab` does not try to load removed legacy UI files.
"""

__all__: list[str] = []
