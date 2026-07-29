from abc import ABC, abstractmethod

class Observer(ABC):
    """Interface untuk Observer (Penerima Notifikasi)"""
    @abstractmethod
    def update(self, message: str):
        pass

class Subject(ABC):
    """Interface untuk Subject (Pengirim Notifikasi)"""
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, message: str):
        for observer in self._observers:
            observer.update(message)
