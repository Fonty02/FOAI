from __future__ import annotations
from typing import List, Optional, Set, TYPE_CHECKING, Union

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
        self._inverse: Optional[str] = inverse
        self._references: List[Reference] = []
        self._parent: Optional[Relationship] = None # Overrides Entity's _parent type hint
        self._symmetric: bool = symmetric

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
        self._references = references

    def removeRef(self, ref: Reference) -> None:
        """
        Removes a specific reference from the list.

        Args:
            ref: The Reference object to remove.
        """
        if ref in self._references:
            self._references.remove(ref)

    def getReferences(self) -> List[Reference]:
        """
        Gets the list of references (instances) for this relationship.

        Returns:
            List[Reference]: The list of Reference objects.
        """
        return self._references

    def getSubjects(self) -> Set[str]:
        """
        Gets a unique, sorted set of subjects from all references.

        Returns:
            Set[str]: A sorted set of subject names.
        """
        subjects = {r.getSubject() for r in self._references}
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
        for r in self._references:
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
        objects = {r.getObject() for r in self._references}
        return set(sorted(objects)) # Return a sorted set

    def getSubj_Objs(self, subject: str) -> List[str]:
        """
        Gets all object names associated with a given subject name.

        Args:
            subject: The subject name.

        Returns:
            List[str]: A list of object names linked to the subject.
        """
        objects = [r.getObject() for r in self._references if r.getSubject() == subject]
        return objects

    def removeAll(self, refs: List[Reference]) -> None:
        """
        Removes multiple references from the list.

        Args:
            refs: A list of Reference objects to remove.
        """
        self._references = [r for r in self._references if r not in refs]

    def getObj_Subjs(self, object_ref: str) -> List[str]:
        """
        Gets all subject names associated with a given object name.

        Args:
            object_ref: The object name.

        Returns:
            List[str]: A list of subject names linked to the object.
        """
        subjects = [r.getSubject() for r in self._references if r.getObject() == object_ref]
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
        return self._inverse

    def setInverse(self, inverse: str) -> None:
        """
        Sets the inverse name of the relationship.

        Args:
            inverse: The inverse name.
        """
        self._inverse = inverse

    def getSymmetric(self) -> bool:
        """
        Checks if the relationship is symmetric.

        Returns:
            bool: True if symmetric, False otherwise.
        """
        return self._symmetric

    def setSymmetric(self, symmetric: bool) -> None:
        """
        Sets the symmetric property of the relationship.

        Args:
            symmetric: True to set as symmetric, False otherwise.
        """
        self._symmetric = symmetric

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
        self._references.append(ref)

    def getChildrenRelationships(self) -> List[Relationship]:
        """
        Gets the direct children (sub-relationships) of this relationship.
        Uses the _children attribute inherited from Entity.

        Returns:
            List[Relationship]: A list of direct child relationships.
        """
        # Ensure children are Relationships, although Entity allows generic Entities
        # This might require runtime checks or careful usage if mixing is possible
        return [child for child in self._children if isinstance(child, Relationship)]


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
        self._children = [] # Clear existing children list first
        for child in children:
            self.addChild(child) # Use Entity's addChild which sets parent


    def addChildrenRelationship(self, relationship: Relationship) -> None:
        """
        Adds a single child relationship.
        Uses the addChild method inherited from Entity.

        Args:
            relationship: The child relationship to add.
        """
        self.addChild(relationship) # Inherited method handles adding to _children and setting parent

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
        if self._parent and isinstance(self._parent, Relationship):
             # Use Entity's _removeChild if available and appropriate
             # Or manage the _children list directly if _removeChild is not suitable
             if self in self._parent._children:
                 self._parent._children.remove(self)

        self._parent = parent
        if parent is not None:
             # Use parent's addChild method (inherited from Entity)
             # This ensures the child is added to the parent's _children list
             # and the child's _parent is set correctly by the addChild method.
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
"""
    # Override getParent to ensure type hint consistency if needed,
    # but Entity.getParent should work if Relationship is an Entity.
    def getParent(self) -> Optional[Relationship]:
        
        Gets the parent relationship of this relationship. Overrides Entity's getParent type hint.

        Returns:
            Optional[Relationship]: The parent relationship, or None.
        # The actual parent is stored in the inherited _parent attribute.
        # We just provide a more specific type hint here.
        parent = super().getParent()
        if parent is None or isinstance(parent, Relationship):
            return parent
        # Handle the case where the parent is an Entity but not a Relationship, if possible.
        # This might indicate a design issue if Relationships should only parent Relationships.
        # Returning None or raising an error might be options depending on desired behavior.
        # For now, assume parent will be None or a Relationship based on usage patterns.
        return None # Or raise TypeError("Parent is not a Relationship")

    # Override setParent for type consistency
    def setParent(self, parent: Optional[Union[Entity, Relationship]]) -> None:
        Sets the parent of this relationship. Ensures parent, if set, is a Relationship or None.

        Args:
            parent: The entity or relationship to set as the parent, or None.
        if parent is None or isinstance(parent, Relationship):
             # Call the original Entity setParent, which handles the _parent attribute
             super().setParent(parent)
        else:
             # Or handle differently if a non-Relationship Entity parent is invalid
             raise TypeError("Parent of a Relationship must be a Relationship or None.")

    # Override addChild for type consistency
    def addChild(self, child: Entity) -> None:
        Adds a child entity/relationship. Ensures added child's parent is set correctly.
        Overrides Entity.addChild to potentially enforce child type if needed,
        though current implementation relies on Entity's logic.

        Args:
            child: The child Entity or Relationship to add.
        # If we need to enforce that children of Relationships must be Relationships:
        # if not isinstance(child, Relationship):
        #    raise TypeError("Children of a Relationship must also be Relationships.")
        super().addChild(child) # Calls Entity's addChild
"""