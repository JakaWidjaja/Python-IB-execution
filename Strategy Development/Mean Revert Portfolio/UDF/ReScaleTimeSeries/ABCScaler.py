from abc import ABC, abstractmethod

class ABCScaler(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def Scale(self, timeSeries, **kwargs):
        pass