import re
import inspect
from pathlib import Path
from datetime import datetime
from typing import Optional,Union,Sequence
from playwright.sync_api import Page, Locator

from apps.omsd_automation.tests.conftest import TESTS_DIR, SCREENSHOTS_DIR


def _sanitize(name: str) -> str:
    """Sanitize a string to be filesystem-safe for use in filenames.

    This function replaces unsafe characters with underscores and trims
    excessive underscores to ensure the resulting string is suitable for
    use as part of a filename.

    Args:
        name: The input string to sanitize.

    Returns:
        A sanitized string safe for filenames.
    """
    # Replace any character that is not alphanumeric, a hyphen, or an underscore with an underscore
    sanitized = re.sub(r'[^a-zA-Z0-9-_]', '_', name)
    # Replace multiple consecutive underscores with a single underscore
    sanitized = re.sub(r'_+', '_', sanitized)
    # Trim leading and trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized

def _detect_context_from_stack():
    """Infer product/test_case from the test call stack inside tests/."""
    product, test_case, module_base = None, None, None
    try:
        tests_dir = (TESTS_DIR.resolve())
    except Exception:
        tests_dir = None

    current_util = Path(__file__).resolve()
    frames = inspect.stack()

    for fi in frames:
        try:
            fpath = Path(fi.filename).resolve()
            if fpath == current_util:
                continue
            if tests_dir and str(fpath).startswith(str(tests_dir)):
                func = inspect.getframeinfo(fi.frame).function
                mb = fpath.stem
                module_base = mb

                if func.startswith("test_"):
                    test_case = func[len("test_"):]
                elif mb.startswith("test_"):
                    test_case = mb[len("test_"):]
                else:
                    test_case = mb

                # Optional product extraction: test_ESG_410_login -> ESG-410
                parts = mb.split("_")
                if len(parts) >= 3 and parts[0] == "test" and parts[1].isalpha() and parts[2].isdigit():
                    product = f"{parts[1]}-{parts[2]}"

                return _sanitize(product or ""), _sanitize(test_case or ""), module_base
        except Exception:
            continue

    return product, test_case, module_base

def save_playwright_screenshot(
    page: Page,
    step_name: str,
    *,
    product: Optional[str] = None,
    test_case: Optional[str] = None,
    extra_subfolder: Optional[str] = None,
    full_page: bool = False,
    image_type: str = "png",
    quality: Optional[int] = None,
    mask: Optional[Sequence[Locator]] = None,
    mask_color: Optional[str] = None,
) -> str:
    """
    Save a Playwright screenshot organized by product/test_case/step.
    Example path:
        screenshots/ESG-410/login/login_step1_20250926_123000.png
    """
    # Normalize
    step = _sanitize(step_name)

    # Auto-detect context if not provided
    auto_product, auto_case, _ = _detect_context_from_stack()
    product = _sanitize(product) if product else (auto_product or "generic")
    test_case = _sanitize(test_case) if test_case else (auto_case or "default")

    # Build folder path
    folder_path = Path(SCREENSHOTS_DIR) / product / test_case
    if extra_subfolder:
        folder_path = folder_path / _sanitize(extra_subfolder)
    folder_path.mkdir(parents=True, exist_ok=True)

    # Filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{product}_{test_case}_{step}_{timestamp}.{image_type}"
    full_path = folder_path / filename

    # Capture screenshot
    page.screenshot(
        path=str(full_path),
        full_page=full_page,
        type=image_type,
        quality=quality,
        mask=mask,
        mask_color=mask_color,
    )

    print(f"📸 Screenshot saved: {full_path}")
    return str(full_path)