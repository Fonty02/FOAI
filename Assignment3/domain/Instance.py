from typing import Dict, List
from .Attribute import Attribute

class Instance:
    """Class representing an instance with its type, id and attributes."""
    
    def __init__(self, type: str, selectedInstanceId: str, attrVals: Dict[str, str], fields: List[Attribute]):
        """
        Initialize an Instance object.
        
        Args:
            type: The type of the instance
            selectedInstanceId: The ID of the instance
            attrVals: Dictionary of attribute values
            fields: List of Attribute objects
        """
        self.type: str = type
        self.selectedInstanceId: str = selectedInstanceId
        self.attributeValues: Dict[str, str] = attrVals
        self.shortDescription: str = self.buildShortDescription(selectedInstanceId, type, attrVals, fields)
    
    def buildShortDescription(self, id: str, type: str, myAttributeValues: Dict[str, str], 
                             fields: List[Attribute]) -> str:
        """
        Build a short description of the instance.
        
        Args:
            id: Instance ID
            type: Instance type
            myAttributeValues: Dictionary of attribute values
            fields: List of Attribute objects
        
        Returns:
            Short description string
        """
        shortDescription = ""
        for a in fields:
            if a.isDescriptive() and myAttributeValues.get(a.getName()) is not None:
                shortDescription += myAttributeValues.get(a.getName()) + " "
        
        shortDescription += f"  <{id}:{type}>"
        return shortDescription
    
    def setType(self, type: str) -> None:
        """Set the instance type."""
        self.type = type
    
    def getType(self) -> str:
        """Get the instance type."""
        return self.type
    
    def setSelectedInstanceId(self, selectedInstanceId: str) -> None:
        """Set the instance ID."""
        self.selectedInstanceId = selectedInstanceId
    
    def getSelectedInstanceId(self) -> str:
        """Get the instance ID."""
        return self.selectedInstanceId
    
    def getShortDescription(self) -> str:
        """Get the short description."""
        return self.shortDescription
    
    def setShortDescription(self, shortDescription: str) -> None:
        """Set the short description."""
        self.shortDescription = shortDescription
    
    def getAttributeValues(self) -> Dict[str, str]:
        """Get the attribute values dictionary."""
        return self.attributeValues
    
    def setAttributeValues(self, attributeValues: Dict[str, str]) -> None:
        """Set the attribute values dictionary."""
        self.attributeValues = attributeValues
    
    def __str__(self) -> str:
        """Return string representation of the instance."""
        return f"Instance [selectedInstanceId={self.selectedInstanceId}]"
    
    def __eq__(self, obj) -> bool:
        """
        Check if two instances are equal based on their ID.
        
        Args:
            obj: Another Instance object
        
        Returns:
            True if the instances have the same ID, False otherwise
        """
        if not isinstance(obj, Instance):
            return False
        return self.selectedInstanceId == obj.selectedInstanceId