from abc import ABC, ABCMeta, abstractmethod

class Vendor(ABC):
    
    @abstractmethod
    def get_all_companies(**kwargs):
        """ 
            Retrieves all companies supported by registered data vendors

        Raises:
            NotImplementedError: this method is implemented in concrete classes
        """
        raise NotImplementedError("get_all_companies not implemented in base class.")

    @abstractmethod
    def get_fundamental_data(**kwargs):
        """
            Retrieves all fundamental data for all the companies supported by registered data vendors

        Raises:
            NotImplementedError: this method is implemented in concrete classes
        """
        raise NotImplementedError("get_fundamental_data not implemented in base class.")

