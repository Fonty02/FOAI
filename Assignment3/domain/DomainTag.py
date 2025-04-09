from abc import ABC, abstractmethod
from domain.Tag import Tag

class DomainTag(Tag, ABC):
    """
    The abstract class DomainTag represents a tag associated with a specific domain.
    It extends the Tag class and provides methods to get and set the domain.
    """

    def __init__(self) -> None:
        super().__init__()
        self._domain: str = "" 

    @abstractmethod
    def get_domain_type(self) -> str:
        """
        This abstract method ensures this class cannot be instantiated directly.
        It must be implemented by all subclasses.
        
        Returns:
            str: The type of the domain tag.
        """
        pass
    
    def getDomain(self) -> str:
        """
        Returns the domain associated with this tag.

        Returns:
            str: the domain associated with this tag
        """
        return self._domain

    def setDomain(self, domain: str) -> None:
        """
        Sets the domain associated with this tag.

        Args:
            domain (str): the domain to be set
        """
        self._domain = domain