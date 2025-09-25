"""Product Category Actions.

This module orchestrates ProductCategoryPage methods into reusable,
business-level workflows. It handles logging, sequencing, and error
management. Page objects remain clean of business logic and logging.
"""
from apps.omsd_automation.actions.base_actions import BaseActions
from apps.omsd_automation.pages.product_category_page import ProductCategoryPage


class ProductCategoryActions(BaseActions):
    """Business workflows for Product Category interactions."""

    def __init__(self, page: ProductCategoryPage, logger=None) -> None:

        """Initialize with a ProductCategoryPage instance."""
        super().__init__(logger)
        self.page = page
    # --- Medical Products ---

    def open_medical_product(self, product_name: str) -> None:
        """Open a medical product's software list."""
        self.logger.log_action(f"Opening Medical product: {product_name}")
        try:
            self.page.open_software(product_name)
            self.logger.log_info(f"Successfully opened Medical product '{product_name}'.")
        except Exception as e:
            self.logger.log_error(f"Failed to open Medical product '{product_name}': {e}")
            raise

    # --- Other Products ---

    def open_other_product(self, product_name: str) -> None:
        """Open an 'Other' product's software list."""
        self.logger.log_action(f"Opening Other product: {product_name}")
        try:
            self.page.open_other_product(product_name)
            self.logger.log_info(f"Successfully opened Other product '{product_name}'.")
        except Exception as e:
            self.logger.log_error(f"Failed to open Other product '{product_name}': {e}")
            raise

    # --- Navigation ---

    def go_back(self) -> None:
        """Return to the previous page."""
        self.logger.log_action("Clicking Back button")
        try:
            self.page.click_back()
            self.logger.log_info("Successfully navigated back.")
        except Exception as e:
            self.logger.log_error(f"Failed to click Back button: {e}")
            raise
