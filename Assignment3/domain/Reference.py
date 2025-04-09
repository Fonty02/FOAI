from typing import List, Optional
from .Attribute import Attribute

class Reference:
    """
    The Reference class represents an instance of a relationship, a link between two entities.
    It contains information about the subject, object, and attributes of the reference.
    """
    
    def __init__(self, subject: str, object: str, attributes: Optional[List[Attribute]] = None):
        """
        Constructs a Reference object with the given subject, object, and optionally attributes.
        
        Args:
            subject: the subject of the reference
            object: the object of the reference
            attributes: the attributes of the reference (optional)
        """
        self.subject: str = subject
        self.object: str = object
        self.attributes: Optional[List[Attribute]] = attributes
    
    def getSubject(self) -> str:
        """
        Returns the subject of the reference.
        
        Returns:
            the subject of the reference
        """
        return self.subject
    
    def setSubject(self, subject: str) -> None:
        """
        Sets the subject of the reference.
        
        Args:
            subject: the subject of the reference
        """
        self.subject = subject
    
    def getObject(self) -> str:
        """
        Returns the object of the reference.
        
        Returns:
            the object of the reference
        """
        return self.object
    
    def setObject(self, object: str) -> None:
        """
        Sets the object of the reference.
        
        Args:
            object: the object of the reference
        """
        self.object = object
    
    def getAttributes(self) -> Optional[List[Attribute]]:
        """
        Returns the attributes of the reference.
        
        Returns:
            the attributes of the reference
        """
        return self.attributes
    
    def setAttributes(self, attributes: List[Attribute]) -> None:
        """
        Sets the attributes of the reference.
        
        Args:
            attributes: the attributes of the reference
        """
        self.attributes = attributes
    
    def __str__(self) -> str:
        """
        Returns a string representation of the Reference object.
        
        Returns:
            a string representation of the Reference object as "Reference [subject=..., object=...]"
        """
        return f"Reference [subject={self.subject}, object={self.object}]"