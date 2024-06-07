from abc import ABC, abstractmethod
from typing import List

class LoadBalancingApproach(ABC):
    
    def __init__(
            self,
            aoai_endpoints: List[str]
    ):
        self.aoai_endpoints = aoai_endpoints
    
    @abstractmethod
    def find_available_aoai(self):
        pass