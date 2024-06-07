from approach import Approach
from typing import overload
import random

class RandomAllocation(Approach):
    def __init__():
        pass

    @overload   
    def find_available_aoai(self):
        aoai = random(self.aoai_endpoints)
        return aoai