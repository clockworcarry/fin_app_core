from abc import ABC, ABCMeta, abstractmethod

class Vendor(ABC):
    
    @abstractmethod
    def get_all_companies(**kwargs):
        """[summary]

        Raises:
            NotImplementedError: Base class method
        """
        raise NotImplementedError("get_all_companies not implemented in base class.")

