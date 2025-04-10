from abc import ABC, abstractmethod
from typing import Optional

class Tag(ABC):
    """Abstract class that represents a tag."""

    def __init__(self):
        """Initializes the Tag class."""
        self.name = None
        self.description = None
        self.notes = None
    

    def getName(self) -> Optional[str]:
        """
        Gets the name of the tag.
        
        Returns:
            The name of the tag.
        """
        return self.name

    def setName(self, name: str) -> None:
        """
        Sets the name of the tag.
        
        Args:
            name: The name of the tag.
        """
        self.name = name

    def getDescription(self) -> Optional[str]:
        """
        Gets the description of the tag.
        
        Returns:
            The description of the tag.
        """
        return self.description

    def setDescription(self, description: str) -> None:
        """
        Sets the description of the tag.
        
        Args:
            description: The description of the tag.
        """
        self.description = description

    def getNotes(self) -> Optional[str]:
        """
        Gets the notes of the tag.
        
        Returns:
            The notes of the tag.
        """
        return self.notes

    def setNotes(self, notes: str) -> None:
        """
        Sets the notes of the tag.
        
        Args:
            notes: The notes of the tag.
        """
        self.notes = notes