import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Page, Locator

from omsd_automation.utils.logger_utils import setup_test_logger


def _sanitize(name: str) -> str:
    """Sanitize strings for safe filenames: allow alnum, dash, underscore, dot."""
    name = name.strip()
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:255]


class BasePage:
    """
    BasePage provides reusable Playwright wrapper methods.
    All page objects must inherit from this to enforce consistency.
    """

    def __init__(self, page: Page, logger_name: str = "base_page"):
        self.page: Page = page
        self.logger = setup_test_logger(logger_name)

    # ----------------------------------------------------------------------
    # Generic Action Methods (do_*)
    # ----------------------------------------------------------------------
    def do_click(self, selector: str):
        """Click an element by selector."""
        self.logger.log_action(f"Clicking element: {selector}")
        self.page.locator(selector).click()

    def do_fill(self, selector: str, text: str):
        """Fill text into an input field."""
        self.logger.log_action(f"Filling '{text}' into element: {selector}")
        self.page.locator(selector).fill(text)

    def do_get_text(self, selector: str) -> str:
        """Retrieve visible inner text of an element."""
        text = self.page.locator(selector).inner_text()
        self.logger.log_action(f"Retrieved text from {selector}: {text}")
        return text

    def verify_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        is_visible = self.page.locator(selector).is_visible()
        self.logger.log_verification(f"Element {selector} is visible", is_visible)
        return is_visible

    # ----------------------------------------------------------------------
    # Utility Helpers
    # ----------------------------------------------------------------------
    def take_screenshot(self, step_name: str, test_case: str = None) -> str:
        """
        Capture and save a screenshot.
        Path format: screenshots/<test_case>/<step_name>_<timestamp>.png
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        step_sanitized = _sanitize(step_name)
        test_case_sanitized = _sanitize(test_case) if test_case else "general"

        folder = Path("screenshots") / test_case_sanitized
        folder.mkdir(parents=True, exist_ok=True)

        file_path = folder / f"{step_sanitized}_{timestamp}.png"
        self.page.screenshot(path=str(file_path))
        self.logger.log_action(f"Screenshot saved: {file_path}")
        return str(file_path)

    # ----------------------------------------------------------------------
    # Advanced Helpers
    # ----------------------------------------------------------------------
    def get_locator(self, selector: str) -> Locator:
        """Return a Playwright Locator object (for advanced use cases)."""
        return self.page.locator(selector)

    def do_hover(self, selector: str):
        """Hover over an element."""
        self.logger.log_action(f"Hovering over element: {selector}")
        self.page.locator(selector).hover()

    def do_press_key(self, selector: str, key: str):
        """Press a key inside an input field."""
        self.logger.log_action(f"Pressing key '{key}' on {selector}")
        self.page.locator(selector).press(key)
