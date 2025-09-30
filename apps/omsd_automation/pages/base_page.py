"""Base UI interaction utilities for Playwright page objects.

This module provides a thin, log-free wrapper around Playwright's sync API to
standardize common UI interactions across Page Objects. It intentionally keeps
responsibilities narrow (Single Responsibility Principle) and leaves workflows,
assertions, and logging to higher layers (Actions/tests). The design supports
POM, SOLID, and DRY by centralizing interaction helpers while preserving the
encapsulation of individual Page Objects.
"""

from pathlib import Path
from typing import Literal, Optional, Union, Sequence

from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

# Type alias used for element state waits. Kept explicit for readability.
ElementState = Literal["attached", "detached", "visible", "hidden"]


class BasePage:
    """Shared base class for Page Objects.

    This class exposes small, composable helper methods that wrap Playwright
    primitives. It does not perform logging or embed business workflows, keeping
    concerns separated between the Page layer (low-level UI interactions) and
    the Actions/tests layers (workflows, logging, and assertions).
    """

    def __init__(self, page: Page) -> None:
        """Initialize the BasePage with a Playwright Page instance.

        Args:
            page: The Playwright Page used for all interactions.
        """
        self.page: Page = page

    # --- Navigation Methods ---

    def go_to(self, url: str) -> None:
        """Navigate the current page to the specified URL.

        Uses a generous timeout to accommodate redirects and heavy pages often
        seen in staging environments.

        Args:
            url: The absolute or relative URL to navigate to.
        """
        # Use a more forgiving wait strategy and higher timeout to accommodate
        # post-login redirects and heavy pages in staging environments.
        self.page.goto(url, timeout=60000)

    # --- Core Interaction Methods ---

    def do_click(self, selector: str) -> None:
        """Click an element identified by a selector.

        Args:
            selector: A Playwright-supported selector string.

        Raises:
            playwright.sync_api.Error: If the element cannot be found or clicked.
        """
        self.page.locator(selector).click()

    def do_fill(self, selector: str, text: str) -> None:
        """Fill an input field with the provided text.

        Args:
            selector: A Playwright-supported selector string targeting an input.
            text: The text to enter.

        Raises:
            playwright.sync_api.Error: If the element cannot be found or filled.
        """
        self.page.locator(selector).fill(text)

    def do_clear(self, selector: str) -> None:
        """Clear the content of an input element.

        Args:
            selector: A Playwright-supported selector string targeting an input.

        Raises:
            playwright.sync_api.Error: If the element cannot be found or cleared.
        """
        self.page.locator(selector).clear()

    def do_hover(self, selector: str) -> None:
        """Hover the mouse cursor over an element.

        Args:
            selector: A Playwright-supported selector string.

        Raises:
            playwright.sync_api.Error: If the element cannot be found or hovered.
        """
        self.page.locator(selector).hover()

    def do_press_key(self, selector: str, key: str) -> None:
        """Simulate a key press on an element.

        Common examples include "Enter" and "ArrowDown".

        Args:
            selector: A Playwright-supported selector string.
            key: The key to press (e.g., "Enter").

        Raises:
            playwright.sync_api.Error: If the element cannot be found or pressed.
        """
        self.page.locator(selector).press(key)

    # --- State & Data Retrieval Methods ---

    def do_get_text(self, selector: str) -> str:
        """Get the visible inner text of an element.

        Args:
            selector: A Playwright-supported selector string.

        Returns:
            str: The element's visible inner text.

        Raises:
            playwright.sync_api.Error: If the element cannot be found.
        """
        return self.page.locator(selector).inner_text()

    def do_get_input_value(self, selector: str) -> str:
        """Get the value attribute from an input element.

        Args:
            selector: A Playwright-supported selector string targeting an input.

        Returns:
            str: The current value of the input element.

        Raises:
            playwright.sync_api.Error: If the element cannot be found.
        """
        return self.page.locator(selector).input_value()

    def to_be_visible(self, selector: str) -> bool:
        """Check whether an element is currently visible on the page.

        Args:
            selector: A Playwright-supported selector string.

        Returns:
            bool: True if visible, otherwise False.
        """
        return self.page.locator(selector).is_visible()

    def to_be_enabled(self, selector: str) -> bool:
        """Check whether an element is enabled.

        Args:
            selector: A Playwright-supported selector string.

        Returns:
            bool: True if enabled (e.g., a button is clickable), otherwise False.
        """
        return self.page.locator(selector).is_enabled()

    def to_be_checked(self, selector: str) -> bool:
        """Check whether a checkbox or radio button is checked.

        Args:
            selector: A Playwright-supported selector string.

        Returns:
            bool: True if checked, otherwise False.
        """
        return self.page.locator(selector).is_checked()

    # --- Wait & Synchronization Methods ---

    def wait_for_element(
        self,
        selector: str,
        state: ElementState = "visible",
        timeout: int = 5000,
    ) -> bool:
        """Wait for an element to reach a specific state.

        Args:
            selector: A Playwright-supported selector string.
            state: Desired element state: "visible", "hidden", "attached", or "detached".
            timeout: Maximum time to wait, in milliseconds.

        Returns:
            bool: True if the state is reached within the timeout; False on timeout.
        """
        try:
            self.page.locator(selector).wait_for(state=state, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_for_selector_base(self, selector: str) -> bool:
        """Wait for a selector to appear in the DOM (any state).

        This is a thin wrapper over Page.wait_for_selector with the default timeout.

        Args:
            selector: A Playwright-supported selector string.

        Returns:
            bool: True if the selector appears before timing out; False otherwise.
        """
        try:
            self.page.wait_for_selector(selector)
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
        mask_color: Optional[str] = None,
    ) -> bytes:
        """Capture a screenshot with customizable options.

        Args:
            path: File path to save the screenshot. If None, returns bytes without saving.
            full_page: Whether to capture the full scrollable page.
            timeout: Maximum time in milliseconds. Defaults to 30,000 ms.
            image_type: Screenshot format - "png" or "jpeg".
            quality: Image quality 0-100 (only for jpeg).
            omit_background: Hide white background for transparency (png only).
            animations: Whether to allow or disable animations during capture.
            caret: Whether to hide or show text cursor.
            mask: Locators of elements to mask with colored overlay.
            mask_color: Color of the mask overlay (CSS color format).

        Returns:
            bytes: Screenshot bytes.
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
            mask_color=mask_color,
        )

    def get_locator(self, selector: str) -> Locator:
        """Return a Locator for advanced chaining or assertions.

        Prefer using the higher-level helpers when possible to preserve
        encapsulation and keep tests readable.

        Args:
            selector: A Playwright-supported selector string.

        Returns:
            Locator: The corresponding Playwright locator.
        """
        return self.page.locator(selector)