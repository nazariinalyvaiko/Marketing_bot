from __future__ import annotations

import logging
from rich.console import Console
from rich.logging import RichHandler

_console: Console | None = None


def get_logger(name: str = "marketing_bot", level: int = logging.INFO) -> logging.Logger:
	global _console
	if _console is None:
		_console = Console()

	logger = logging.getLogger(name)
	if not logger.handlers:
		logger.setLevel(level)
		handler = RichHandler(console=_console, show_path=False, markup=True, rich_tracebacks=True)
		handler.setLevel(level)
		formatter = logging.Formatter("%(message)s")
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		logger.propagate = False
	return logger
