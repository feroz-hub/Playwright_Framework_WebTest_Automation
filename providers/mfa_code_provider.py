from abc import ABC, abstractmethod

class IMFACodeProvider(ABC):
    @abstractmethod
    def get_mfa_code(self, user:str = None) -> str:
        pass