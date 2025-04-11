from typing import Set
from domain.DomainTag import DomainTag

class Union(DomainTag):
    """
    Represents a Union domain tag.
    A Union is a type of DomainTag that contains a set of values.
    """

    def __init__(self, name: str, domain: str, values: Set[str]) -> None:
        """
        Constructs a Union object with the specified name, domain, and values.
        
        Args:
            name: the name of the Union
            domain: the domain of the Union
            values: the set of values in the Union
        """
        super().__init__()
        self.name = name
        self.domain=domain
        self.values = values

    def get_domain_type(self) -> str:
        """
        Returns the type of the domain tag.
        
        Returns:
            str: The type of this domain tag ("Union").
        """
        return "Union"

    def getValues(self) -> Set[str]:
        """
        Returns the set of values in the Union.
        
        Returns:
            the set of values
        """
        return self.values

    def setValues(self, values: Set[str]) -> None:
        """
        Sets the set of values in the Union.
        
        Args:
            values: the set of values to set
        """
        self.values = values

    def __eq__(self, obj: object) -> bool:
        """
        Indicates whether some other object is "equal to" this one.
        
        Args:
            obj: the reference object with which to compare
            
        Returns:
            True if the two Unions have the same name; False otherwise
        """
        if self is obj:
            return True
        if obj is None or type(self) != type(obj):
            return False
        union = obj  # type: Union
        return self.name == union.name

    def __hash__(self) -> int:
        """
        Returns the hash code value for this Union object.
        
        Returns:
            the hash code value for this Union object as the hash of the name attribute
        """
        return hash(self.name)