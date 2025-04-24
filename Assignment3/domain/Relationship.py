from __future__ import annotations
from typing import List, Optional, Set, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular imports for type hints
if TYPE_CHECKING:
    from .Attribute import Attribute
    from .Reference import Reference
    # No need to import Entity again if it's in the same directory and imported below

from .Entity import Entity
from .Attribute import Attribute 

class Relationship(Entity):
    """
    Represents a relationship between entities in a domain, extending the Entity class.
    It includes properties like inverse name, symmetry, and references (instances of the relationship).
    """
    universalRelationshipName: str = "Relationship"
    inverse: str = None
    references: List[Reference] = []
    parent: Optional[Relationship] = None
    children: List[Relationship] = [] # List of child relationships
    

    def __init__(self, name: str, domain: Optional[str] = None, inverse: Optional[str] = None,
                 parent: Optional[Relationship] = None, symmetric: bool = False,
                 attributes: Optional[List[Attribute]] = None):
        """
        Initializes a new Relationship object.

        Args:
            name: The name of the relationship.
            domain: The domain the relationship belongs to (optional).
            inverse: The name of the inverse relationship (optional).
            parent: The parent relationship in a hierarchy (optional).
            symmetric: Boolean indicating if the relationship is symmetric (default: False).
            attributes: A list of attributes for the relationship (optional).
        """
        super().__init__(name, domain)
        self.inverse: Optional[str] = inverse
        self.references: List[Reference] = []
        self.parent: Optional[Relationship] = None # Overrides Entity's parent type hint
        self.symmetric: bool = symmetric

        if attributes:
            self.setAttributes(attributes) # Use inherited method

        if parent:
            self.setParentRelationship(parent) # Call specific method if provided

    def __str__(self) -> str:
        """
        Returns the string representation of the relationship, which is its name.

        Returns:
            str: The name of the relationship.
        """
        return self.name

    def setReferences(self, references: List[Reference]) -> None:
        """
        Sets the list of references (instances) for this relationship.

        Args:
            references: A list of Reference objects.
        """
        self.references = references

    def removeRef(self, ref: Reference) -> None:
        """
        Removes a specific reference from the list.

        Args:
            ref: The Reference object to remove.
        """
        if ref in self.references:
            self.references.remove(ref)

    def getReferences(self) -> List[Reference]:
        """
        Gets the list of references (instances) for this relationship.

        Returns:
            List[Reference]: The list of Reference objects.
        """
        return self.references

    def getSubjects(self) -> Set[str]:
        """
        Gets a unique, sorted set of subjects from all references.

        Returns:
            Set[str]: A sorted set of subject names.
        """
        subjects = {r.getSubject() for r in self.references}
        return set(sorted(subjects)) # Return a sorted set

    def getReference(self, subject: str, object_ref: str) -> Optional[Reference]:
        """
        Finds a reference based on the subject and object names (case-insensitive).

        Args:
            subject: The subject name to search for.
            object_ref: The object name to search for.

        Returns:
            Optional[Reference]: The found Reference object, or None if not found.
        """
        for r in self.references:
            # Assuming getSubject() and getObject() return strings
            if r.getSubject().lower() == subject.lower() and r.getObject().lower() == object_ref.lower():
                return r
        return None

    def getObjects(self) -> Set[str]:
        """
        Gets a unique, sorted set of objects from all references.

        Returns:
            Set[str]: A sorted set of object names.
        """
        objects = {r.getObject() for r in self.references}
        return set(sorted(objects)) # Return a sorted set

    def getSubj_Objs(self, subject: str) -> List[str]:
        """
        Gets all object names associated with a given subject name.

        Args:
            subject: The subject name.

        Returns:
            List[str]: A list of object names linked to the subject.
        """
        objects = [r.getObject() for r in self.references if r.getSubject() == subject]
        return objects

    def removeAll(self, refs: List[Reference]) -> None:
        """
        Removes multiple references from the list.

        Args:
            refs: A list of Reference objects to remove.
        """
        self.references = [r for r in self.references if r not in refs]

    def getObj_Subjs(self, object_ref: str) -> List[str]:
        """
        Gets all subject names associated with a given object name.

        Args:
            object_ref: The object name.

        Returns:
            List[str]: A list of subject names linked to the object.
        """
        subjects = [r.getSubject() for r in self.references if r.getObject() == object_ref]
        return subjects

    def getAllAttributes(self) -> List[Attribute]:
        """
        Gets all attributes of this relationship, including inherited ones and a default 'notes' attribute.
        Overrides the Entity.getAllAttributes method.

        Returns:
            List[Attribute]: A list of all attributes.
        """
        all_attributes = super().getAllAttributes() # Get attributes from Entity hierarchy
        # Ensure 'notes' attribute is added only once and is of the correct type
        has_notes = any(attr.getName() == "notes" for attr in all_attributes)
        if not has_notes:
             # Assuming a simple text attribute constructor exists or is handled
            notes_attr = Attribute(name="notes", data_type="text")
            all_attributes.append(notes_attr)
        return all_attributes

    # getName is inherited from Entity

    def set(self, name: str, inverse: str) -> None:
        """
        Sets the name and inverse name of the relationship.

        Args:
            name: The new name for the relationship.
            inverse: The new inverse name.
        """
        self.setName(name) # Use inherited method
        self.setInverse(inverse)

    def getInverse(self) -> Optional[str]:
        """
        Gets the inverse name of the relationship.

        Returns:
            Optional[str]: The inverse name, or None if not set.
        """
        return self.inverse

    def setInverse(self, inverse: str) -> None:
        """
        Sets the inverse name of the relationship.

        Args:
            inverse: The inverse name.
        """
        self.inverse = inverse

    def getSymmetric(self) -> bool:
        """
        Checks if the relationship is symmetric.

        Returns:
            bool: True if symmetric, False otherwise.
        """
        return self.symmetric

    def setSymmetric(self, symmetric: bool) -> None:
        """
        Sets the symmetric property of the relationship.

        Args:
            symmetric: True to set as symmetric, False otherwise.
        """
        self.symmetric = symmetric

    def addReference(self, ref: Reference) -> None:
        """
        Adds a reference to the list. If a reference with the same subject and object
        already exists, it is replaced by the new one.

        Args:
            ref: The Reference object to add.
        """
        existing_ref = self.getReference(ref.getSubject(), ref.getObject())
        if existing_ref:
            self.removeRef(existing_ref)
        self.references.append(ref)

    def getChildrenRelationships(self) -> List[Relationship]:
        """
        Gets the direct children (sub-relationships) of this relationship.
        Uses the children attribute inherited from Entity.

        Returns:
            List[Relationship]: A list of direct child relationships.
        """
        # Ensure children are Relationships, although Entity allows generic Entities
        # This might require runtime checks or careful usage if mixing is possible
        return [child for child in self.children if isinstance(child, Relationship)]


    def setChildrenRelationship(self, children: List[Relationship]) -> None:
        """
        Sets the list of direct children (sub-relationships) for this relationship.
        Warning: This replaces existing children and updates parent references.

        Args:
            children: The list of child relationships to set.
        """
        # Clear existing parent references for removed children
        for existing_child in self.getChildrenRelationships():
             if existing_child not in children:
                 existing_child.setParent(None) # Use Entity's setParent

        # Set new children and update their parent references
        self.children = [] # Clear existing children list first
        for child in children:
            self.addChild(child) # Use Entity's addChild which sets parent


    def addChildrenRelationship(self, relationship: Relationship) -> None:
        """
        Adds a single child relationship.
        Uses the addChild method inherited from Entity.

        Args:
            relationship: The child relationship to add.
        """
        self.addChild(relationship) # Inherited method handles adding to children and setting parent

    def addReferences(self, references: List[Reference]) -> None:
        """
        Adds multiple references using the addReference logic (handles duplicates).

        Args:
            references: A list of Reference objects to add.
        """
        for ref in references:
            self.addReference(ref)

    def setParentRelationship(self, parent: Relationship) -> None:
        """
        Sets the parent of this relationship and adds this relationship
        to the parent's children list.

        Args:
            parent: The Relationship object to set as the parent.
        """
        # Detach from previous parent if exists
        if self.parent and isinstance(self.parent, Relationship):
             # Use Entity's _removeChild if available and appropriate
             # Or manage the children list directly if _removeChild is not suitable
             if self in self.parent.children:
                 self.parent.children.remove(self)

        self.parent = parent
        if parent is not None:
             # Use parent's addChild method (inherited from Entity)
             # This ensures the child is added to the parent's children list
             # and the child's parent is set correctly by the addChild method.
             parent.addChild(self)


    def isTopRelationship(self) -> bool:
        """
        Checks if this relationship is a top-level relationship (its parent is the universal root).

        Returns:
            bool: True if it's a top-level relationship, False otherwise.
        """
        # Accessing parent's name safely
        parent = self.getParent() # Use inherited getter
        return parent is not None and parent.getName() == self.universalRelationshipName
