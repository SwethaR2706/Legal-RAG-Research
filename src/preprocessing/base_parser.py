from abc import ABC ,abstractmethod 

from .document import LegalDocument 


class BaseParser (ABC ):

    @abstractmethod 
    def parse (
    self ,
    pages 
    )->LegalDocument :
        """
        Convert raw extracted pages or dataset
        content into a standardized LegalDocument.
        """
        pass 