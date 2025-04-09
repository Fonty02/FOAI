from typing import List
from .Attribute import Attribute
from .Reference import Reference

class RelationshipSite:
    """
    Represents a relationship site that stores information about relationships between subjects and objects.
    """

    def __init__(self, name: str, inverse: str, symmetric: bool, attributes: List[Attribute]):
        """
        Constructs a RelationshipSite with the specified name, inverse, symmetric flag, and attributes.
        
        Args:
            name: The name of the relationship
            inverse: The inverse name of the relationship
            symmetric: Flag indicating if the relationship is symmetric
            attributes: List of attributes for the relationship
        """
        self.name: str = name
        self.inverse: str = inverse
        self.symmetric: bool = symmetric
        self.attributes: List[Attribute] = attributes
        self.relationships: List[Reference] = []
    
    def getSubjects(self) -> List[str]:
        """
        Returns a sorted list of all subjects in the relationships.
        
        Returns:
            A sorted list of all subjects
        """
        subjects: List[str] = []
        for r in self.relationships:
            subjects.append(r.getSubject())
        subjects.sort()
        return subjects

    def getObjects(self) -> List[str]:
        """
        Returns a sorted list of all objects in the relationships.
        
        Returns:
            A sorted list of all objects
        """
        objects: List[str] = []
        for r in self.relationships:
            objects.append(r.getObject())
        objects.sort()
        return objects

    def getSubj_Objs(self, subject: str) -> List[str]:
        """
        Returns a list of objects related to the given subject.
        
        Args:
            subject: The subject to find related objects for
            
        Returns:
            A list of objects related to the subject
        """
        objects: List[str] = []
        for r in self.relationships:
            if r.getSubject() == subject:
                objects.append(r.getObject())
        return objects
    
    def getObj_Subjs(self, object: str) -> List[str]:
        """
        Returns a list of subjects related to the given object.
        
        Args:
            object: The object to find related subjects for
            
        Returns:
            A list of subjects related to the object
        """
        subjects: List[str] = []
        for r in self.relationships:
            if r.getObject() == object:
                subjects.append(r.getSubject())
        return subjects
    
    def getName(self) -> str:
        """
        Returns the name of the relationship.
        
        Returns:
            The name of the relationship
        """
        return self.name
    
    def setName(self, name: str) -> None:
        """
        Sets the name of the relationship.
        
        Args:
            name: The new name for the relationship
        """
        self.name = name
    
    def getInverse(self) -> str:
        """
        Returns the inverse name of the relationship.
        
        Returns:
            The inverse name of the relationship
        """
        return self.inverse
    
    def setInverse(self, inverse: str) -> None:
        """
        Sets the inverse name of the relationship.
        
        Args:
            inverse: The new inverse name for the relationship
        """
        self.inverse = inverse
    
    def getSymmetric(self) -> bool:
        """
        Returns whether the relationship is symmetric.
        
        Returns:
            True if the relationship is symmetric, False otherwise
        """
        return self.symmetric
    
    def setSymmetric(self, symmetric: bool) -> None:
        """
        Sets whether the relationship is symmetric.
        
        Args:
            symmetric: True if the relationship should be symmetric, False otherwise
        """
        self.symmetric = symmetric
    
    def getAttributes(self) -> List[Attribute]:
        """
        Returns the attributes of the relationship.
        
        Returns:
            The attributes of the relationship
        """
        return self.attributes
    
    def setAttributes(self, attributes: List[Attribute]) -> None:
        """
        Sets the attributes of the relationship.
        
        Args:
            attributes: The new attributes for the relationship
        """
        self.attributes = attributes