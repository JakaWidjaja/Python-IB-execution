from abc import ABC, abstractmethod

class ABCTechnicalIndicator(ABC):
    def __init__():
        pass
    
    @abstractmethod
    def Calculate(self, timeSeries):
        pass
