from pathlib import Path
from typing import Literal, Optional, Union, Sequence

from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

ElementState = Literal["attached", "detached", "visible", "hidden"]

class BasePage:
    """
    Provides a collection of reusable, log-free wrapper methods for Playwright.
    This class's single responsibility is to simplify and standardize UI interactions.
    """
    def __init__(self, page: Page):
        """Initializes the BasePage with a Playwright Page instance."""
        self.page: Page = page

    # --- Navigation Methods ---

    def go_to(self, url: str) -> None:
        """Navigates the current page to the specified URL with sensible defaults."""
        # Use a more forgiving wait strategy and higher timeout to accommodate
        # post-login redirects and heavy pages in staging environments.
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

    # --- Core Interaction Methods ---

    def do_click(self, selector: str):
        """Clicks an element identified by its selector."""
        self.page.locator(selector).click()

    def do_fill(self, selector: str, text: str):
        """Fills an input field with the provided text."""
        self.page.locator(selector).fill(text)

    def do_clear(self, selector: str):
        """Clears the content of an input element."""
        self.page.locator(selector).clear()

    def do_hover(self, selector: str):
        """Hovers the mouse cursor over an element."""
        self.page.locator(selector).hover()

    def do_press_key(self, selector: str, key: str):
        """Simulates a key press on an element (e.g., 'Enter', 'ArrowDown')."""
        self.page.locator(selector).press(key)

    # --- State & Data Retrieval Methods ---

    def do_get_text(self, selector: str) -> str:
        """Retrieves the visible inner text of an element."""
        return self.page.locator(selector).inner_text()

    def do_get_input_value(self, selector: str) -> str:
        """Retrieves the 'value' attribute from an input element."""
        return self.page.locator(selector).input_value()

    def is_visible(self, selector: str) -> bool:
        """Checks if an element is currently visible on the page."""
        return self.page.locator(selector).is_visible()

    def is_enabled(self, selector: str) -> bool:
        """Checks if an element is enabled (e.g., a button is clickable)."""
        return self.page.locator(selector).is_enabled()

    def is_checked(self, selector: str) -> bool:
        """Checks if a checkbox or radio button is checked."""
        return self.page.locator(selector).is_checked()

    # --- Wait & Synchronization Methods ---

    def wait_for_element(self, selector: str, state: ElementState = "visible", timeout: int = 5000) -> bool:
        """
        Waits for an element to reach a specific state ('visible', 'hidden', 'attached').
        Returns True if the state is reached, False on timeout.
        """
        try:
            self.page.locator(selector).wait_for(state=state, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    # --- Utility & Advanced Methods ---

    def take_screenshot(
            self,
            path: Optional[Union[Path, str]] = None,
            *,
            full_page: bool = False,
            timeout: Optional[float] = None,
            image_type: Literal["jpeg", "png"] = "png",
            quality: Optional[int] = None,
            omit_background: bool = False,
            animations: Literal["allow", "disabled"] = "disabled",
            caret: Literal["hide", "initial"] = "hide",
            mask: Optional[Sequence[Locator]] = None,
            mask_color: Optional[str] = None
    ) -> bytes:
        """
        Captures a screenshot with customizable options.

        Args:
            path: File path to save the screenshot. If None, returns bytes without saving.
            full_page: Whether to capture the full scrollable page.
            timeout: Maximum time in milliseconds. Defaults to 30000ms.
            image_type: Screenshot format - 'png' or 'jpeg'.
            quality: Image quality 0-100 (only for jpeg).
            omit_background: Hide white background for transparency (png only).
            animations: Whether to allow or disable animations during capture.
            caret: Whether to hide or show text cursor.
            mask: Locators of elements to mask with colored overlay.
            mask_color: Color of the mask overlay (CSS color format).

        Returns:
            Screenshot as bytes.
        """
        return self.page.screenshot(
            path=str(path) if path else None,
            full_page=full_page,
            timeout=timeout,
            type=image_type,
            quality=quality,
            omit_background=omit_background,
            animations=animations,
            caret=caret,
            mask=mask,
            mask_color=mask_color
        )

    def get_locator(self, selector: str) -> Locator:
        """
        Returns a Playwright Locator object for advanced chaining or assertions.
        Use sparingly to avoid breaking the encapsulation pattern.
        """
        return self.page.locator(selector)