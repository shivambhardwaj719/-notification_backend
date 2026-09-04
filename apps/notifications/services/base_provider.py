from abc import ABC, abstractmethod

class BaseNotificationService(ABC):
    @abstractmethod
    def send(self, recipient: str, content: str, subject: str = None, title: str = None, context: dict = None) -> dict:
        pass
