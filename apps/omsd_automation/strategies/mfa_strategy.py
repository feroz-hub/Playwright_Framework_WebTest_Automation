from abc import ABC, abstractmethod

from apps.omsd_automation.pages.base_page import BasePage
from apps.omsd_automation.pages.mfa_page import MFAPage


class IMFAStrategy(ABC):
    @abstractmethod
    def complete_mfa(self, page: BasePage, code: str) -> None:
        pass