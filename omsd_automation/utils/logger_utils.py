"""Logger utilities for test automation.

This module provides a single, cohesive TestLogger implementation and a
factory helper, following SOLID, DRY, KISS, and OOP principles. It avoids
handler duplication, supports configurable log level and output directory,
and offers consistent, readable formatting for both console and file logs.

Security note: Do not log secrets (e.g., passwords, tokens). The logger does
not automatically mask values because context is required; callers should
ensure sensitive data are sanitized before logging.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional


class TestLogger:
    """Structured logger tailored for test automation.

    Features:
    - Console and per-test file logging
    - Configurable log level, output directory, and emoji usage
    - Consistent naming and message format

    Public API is intentionally small and stable to keep usage simple.

    This class follows SOLID principles:
    - Single Responsibility: Handles only test logging concerns
    - Open/Closed: Extensible through composition, not modification
    - Liskov Substitution: Can be used wherever a logger interface is expected
    - Interface Segregation: Small, focused public API
    - Dependency Inversion: Depends on logging abstractions, not concrete implementations
    """

    # Class-level constants for better maintainability (DRY principle)
    _EMOJI_MAPPINGS = {
        'step': '🔄',
        'action': '⚡',
        'verify_pass': '✅',
        'verify_fail': '❌',
        'magnifier': '🔍',
        'screenshot': '📸'
    }

    _DEFAULT_LOG_DIR = "logs"
    _DEFAULT_LOG_LEVEL = logging.INFO
    _LOGGER_NAMESPACE = "omsd"

    def __init__(
        self,
        test_name: str,
        log_dir: str = _DEFAULT_LOG_DIR,
        log_level: int = _DEFAULT_LOG_LEVEL,
        use_emojis: bool = True,
    ) -> None:
        """Initialize TestLogger with a specified configuration.

        Args:
            test_name: Unique identifier for the test case
            log_dir: Directory for log files (created if it doesn't exist)
            log_level: Standard Python logging level
            use_emojis: Whether to include emojis in log messages

        Raises:
            OSError: If log directory cannot be created
        """
        self.test_name: str = test_name
        self.log_dir: str = log_dir
        self.use_emojis: bool = use_emojis

        self._ensure_log_directory()
        self._logger = self._create_logger(log_level)

    def _ensure_log_directory(self) -> None:
        """Create a log directory if it doesn't exist."""
        os.makedirs(self.log_dir, exist_ok=True)

    def _create_logger(self, log_level: int) -> logging.Logger:
        """Create and configure the underlying logger instance."""
        log_file = self._generate_log_filename()
        logger_name = f"{self._LOGGER_NAMESPACE}.{self.test_name}"

        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.propagate = False  # Avoid duplicate logs via root logger

        self._configure_handlers(logger, log_level, log_file)
        return logger

    def _generate_log_filename(self) -> str:
        """Generate timestamped log filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.log_dir, f"{self.test_name}_{timestamp}.log")

    def _configure_handlers(self, logger: logging.Logger, log_level: int, log_file: str) -> None:
        """Configure console and file handlers for the logger."""
        # Ensure idempotent handler configuration
        self._clear_existing_handlers(logger)

        # Console handler for immediate feedback
        console_handler = self._create_console_handler(log_level)

        # File handler for persistent logging
        file_handler = self._create_file_handler(log_file, log_level)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    def _clear_existing_handlers(self, logger: logging.Logger) -> None:
        """Remove existing handlers to prevent duplication."""
        if logger.hasHandlers():
            for handler in list(logger.handlers):
                self._safe_close_handler(handler)
            logger.handlers.clear()

    def _create_console_handler(self, log_level: int) -> logging.StreamHandler:
        """Create a console handler with simple message formatting."""
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter("%(message)s"))
        return handler

    def _create_file_handler(self, log_file: str, log_level: int) -> logging.FileHandler:
        """Create a file handler with detailed formatting."""
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setLevel(log_level)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        return handler

    def _get_emoji(self, emoji_key: str) -> str:
        """Get emoji character if emojis are enabled, empty string otherwise."""
        return self._EMOJI_MAPPINGS.get(emoji_key, '') if self.use_emojis else ''

    def _format_message_with_prefix(self, prefix: str, message: str, emoji_key: str = '') -> str:
        """Format message with optional emoji prefix."""
        emoji = self._get_emoji(emoji_key)
        full_prefix = f"{emoji} {prefix}" if emoji else prefix
        return f"{full_prefix} {message}"

    # -----------------------------
    # Internal helpers
    # -----------------------------
    @staticmethod
    def _safe_close_handler(handler: logging.Handler) -> None:
        """Safely close handler without breaking test execution."""
        try:
            handler.close()
        except Exception:
            # Best effort: never let logging teardown break tests
            pass

    # -----------------------------
    # Generic logging wrappers (KISS principle - simple interface)
    # -----------------------------
    def log_info(self, message: str) -> None:
        """Log an informational message."""
        self._logger.info(message)

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self._logger.warning(message)

    def log_error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(message)

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)

    # -----------------------------
    # Test-specific convenience methods
    # -----------------------------
    def log_step(self, message: str) -> None:
        """Log a test step with appropriate formatting."""
        formatted_message = self._format_message_with_prefix("STEP:", message, 'step')
        self._logger.info(formatted_message)

    def log_action(self, message: str) -> None:
        """Log a test action with appropriate formatting."""
        formatted_message = self._format_message_with_prefix("ACTION:", message, 'action')
        self._logger.info(formatted_message)

    def log_verification(self, message: str, result: bool = True) -> None:
        """Log a verification result with a pass / fail indication."""
        status_emoji = 'verify_pass' if result else 'verify_fail'
        status_text = "PASSED" if result else "FAILED"

        magnifier = self._get_emoji('magnifier')
        status_indicator = f"{self._get_emoji(status_emoji)} {status_text}" if self.use_emojis else status_text

        verify_prefix = f"{magnifier}VERIFY:" if magnifier else "VERIFY:"
        formatted_message = f"{verify_prefix} {message} → {status_indicator}"
        self._logger.info(formatted_message)

    def log_screenshot(self, file_path: str) -> None:
        """Log screenshot capture with a file path."""
        formatted_message = self._format_message_with_prefix(
            "Screenshot saved:", file_path, 'screenshot'
        )
        self._logger.info(formatted_message)

    # -----------------------------
    # Lifecycle management
    # -----------------------------
    def close(self) -> None:
        """Close and detach logger handlers (optional cleanup)."""
        for handler in list(self._logger.handlers):
            self._safe_close_handler(handler)
        self._logger.handlers.clear()

    def __enter__(self) -> 'TestLogger':
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Automatically close the logger when exiting context."""
        self.close()

    # Expose the underlying logger for advanced scenarios (following Open/Closed principle)
    @property
    def logger(self) -> logging.Logger:
        """Access to the underlying logger instance for advanced use cases."""
        return self._logger

    # -----------------------------
    # Additional utility methods
    # -----------------------------
    def set_level(self, level: int) -> None:
        """Dynamically change logging level."""
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)

    def get_log_file_path(self) -> Optional[str]:
        """Get the path to the current log file."""
        for handler in self._logger.handlers:
            if isinstance(handler, logging.FileHandler):
                return handler.baseFilename
        return None

    @property
    def DEFAULT_LOG_DIR(self):
        return self._DEFAULT_LOG_DIR


# ----------------------------------------------------------------------
# Factory function (for test setup) - Maintains backward compatibility
# ----------------------------------------------------------------------

def setup_test_logger(
    test_name: str,
    log_dir: str = TestLogger._DEFAULT_LOG_DIR,
    log_level: Optional[int] = None,
    use_emojis: bool = True,
) -> TestLogger:
    """Create and return a TestLogger for the provided test name.

    Factory function that provides a convenient way to create TestLogger instances
    while maintaining backward compatibility with existing code.

    Args:
        test_name: A logical name or ID for the test case.
        log_dir: Directory to place the log file (created if missing).
        log_level: Standard logging level; defaults to logging.INFO.
        use_emojis: Whether to use emojis in console/file output.

    Returns:
        A configured TestLogger instance.

    Example:
        >>> logger = setup_test_logger("test_login", log_level=logging.DEBUG)
        >>> logger.log_step("Starting login test")
        >>> logger.log_action("Entering username")
        >>> logger.log_verification("Login successful", True)
        >>> logger.close()
    """
    return TestLogger(
        test_name=test_name,
        log_dir=log_dir,
        log_level=log_level or TestLogger._DEFAULT_LOG_LEVEL,
        use_emojis=use_emojis,
    )