import logging

from utils.logger_utils import setup_test_logger
from utils.screenshot_utils import save_playwright_screenshot


class BaseActions:
    def __init__(self,logger: logging.Logger = None ,page=None):
        class_name = self.__class__.__name__
        self.logger = logger or setup_test_logger(class_name)
        self.page = page

    def take_screenshot(self, step_name: str, *, product: str = None, test_case: str = None, extra_subfolder: str = None) -> str:
        """
        Capture a screenshot using Playwright and save it in an organized folder structure.
        Args:
            step_name: Name of the step will be part of the filename.
            product: Optional product name override.
            test_case: Optional test case name override.
            extra_subfolder: Optional extra folder.
        Returns:
            Absolute path to the screenshot file.
        """
        return save_playwright_screenshot(
            self.page,
            step_name,
            product=product,
            test_case=test_case,
            extra_subfolder=extra_subfolder
        )