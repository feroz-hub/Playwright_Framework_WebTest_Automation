import os
import logging
from datetime import datetime
from typing import Optional


class TestLogger:
    """
    Structured test logger with emoji-based formatting.
    Handles both console and file logging per test case.
    """

    def __init__(self, test_name: str, log_dir: str = "logs", log_level: int = logging.INFO):
        self.test_name = test_name
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        # Create a log file with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"{self.test_name}_{timestamp}.log")

        # Initialize logger
        self.logger = logging.getLogger(test_name)
        self.logger.setLevel(log_level)

        # Prevent duplicate handlers if reused
        if not self.logger.handlers:
            self._configure_handlers(log_file)

    # ----------------------------------------------------------------------
    # Internal helper to configure handlers
    # ----------------------------------------------------------------------
    def _configure_handlers(self, log_file: str):
        """Attach console and file handlers with proper formatters."""
        # Console Handler (simple)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        # File Handler (detailed)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    # ----------------------------------------------------------------------
    # Public Logging Methods
    # ----------------------------------------------------------------------
    def log_step(self, message: str):
        """Log a test step in human-readable format."""
        self.logger.info(f"📝 STEP: {message}")

    def log_action(self, message: str):
        """Log an action performed."""
        self.logger.info(f"⚡ ACTION: {message}")

    def log_verification(self, message: str, result: bool = True):
        """Log a verification outcome."""
        status = "✅ PASSED" if result else "❌ FAILED"
        self.logger.info(f"🔍 VERIFY: {message} → {status}")

    def log_error(self, message: str):
        """Log an error explicitly."""
        self.logger.error(f"❌ ERROR: {message}")

    def log_screenshot(self, file_path: str):
        """Log screenshot capture."""
        self.logger.info(f"📸 Screenshot saved: {file_path}")


# ----------------------------------------------------------------------
# Factory function (for test setup)
# ----------------------------------------------------------------------
def setup_test_logger(test_name: str, log_dir: str = "logs", log_level: Optional[int] = None) -> TestLogger:
    """
    Factory function to create a new TestLogger instance.
    Ensures each test has its own structured logger.

    Example:
        logger = setup_test_logger("login_flow")
        logger.log_step("Starting login test")
    """
    return TestLogger(test_name, log_dir, log_level or logging.INFO)
import os
import logging
from datetime import datetime
class TestLogger:
   """
   Structured logger for test automation.
   Provides step/action/verification-level logging
   with console + file output.
   """
   def __init__(self, test_name: str, log_dir: str = "logs", use_emojis: bool = True):
       self.test_name = test_name
       self.log_dir = log_dir
       self.use_emojis = use_emojis
       os.makedirs(self.log_dir, exist_ok=True)
       timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
       log_file = os.path.join(self.log_dir, f"{self.test_name}_{timestamp}.log")
       # Configure logger
       self.logger = logging.getLogger(test_name)
       self.logger.setLevel(logging.INFO)
       # Remove old handlers (avoid duplicates)
       if self.logger.hasHandlers():
           self.logger.handlers.clear()
       # Console handler
       console_handler = logging.StreamHandler()
       console_handler.setFormatter(logging.Formatter("%(message)s"))
       # File handler
       file_handler = logging.FileHandler(log_file, encoding="utf-8")
       file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
       self.logger.addHandler(console_handler)
       self.logger.addHandler(file_handler)
   # ---------- Generic wrappers ----------
   def log_info(self, message: str):
       self.logger.info(message)
   def log_error(self, message: str):
       self.logger.error(message)
   def log_debug(self, message: str):
       self.logger.debug(message)
   def log_warning(self, message: str):
       self.logger.warning(message)
   # ---------- Test-specific logging ----------
   def log_step(self, message: str):
       prefix = "📝 STEP:" if self.use_emojis else "STEP:"
       self.logger.info(f"{prefix} {message}")
   def log_action(self, message: str):
       prefix = "⚡ ACTION:" if self.use_emojis else "ACTION:"
       self.logger.info(f"{prefix} {message}")
   def log_verification(self, message: str, result: bool = True):
       if result:
           status = "✅ PASSED" if self.use_emojis else "PASSED"
       else:
           status = "❌ FAILED" if self.use_emojis else "FAILED"
       self.logger.info(f"🔍 VERIFY: {message} → {status}")
   def log_screenshot(self, file_path: str):
       prefix = "📸 Screenshot saved:" if self.use_emojis else "Screenshot saved:"
       self.logger.info(f"{prefix} {file_path}")

# ---------- Helper function ----------
def setup_test_logging(test_name: str, use_emojis: bool = True) -> TestLogger:
   """
   Create a new TestLogger instance for a given test case.
   """
   return TestLogger(test_name, use_emojis=use_emojis)