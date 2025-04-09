from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING, Union  # Added Union

# Use TYPE_CHECKING to avoid circular imports for type hints
if TYPE_CHECKING:
    from .Attribute import Attribute
    from .TreeNode import TreeNode

from .DomainTag import DomainTag
from .DefaultTreeNode import DefaultTreeNode


class Entity(DomainTag):
    """
    Represents an entity in a domain, analogous to the Java Entity class.
    Entities can have attributes, children (sub-entities), and a parent.
    """
    universalClassName: str = "Entity"  # Used for checks like isTopClass

    def __init__(self, name: str, domain: Optional[str] = None):
        """
        Initializes a new Entity object.

        Args:
            name: The name of the entity.
            domain: The domain the entity belongs to (optional).
        """
        super().__init__()
        self._name: str = name
        if domain:
            self.setDomain(domain)
        self._values: List[str] = []
        self._graphBrainID: Optional[str] = None  # Renamed to match Java
        self._attributes: List[Attribute] = []
        self._children: List[Entity] = []
        self._parent: Optional[Entity] = None
        self._abstract: bool = False

    def get_domain_type(self) -> str:
        """
        Returns the type of this domain tag.

        Returns:
            str: The type, which is "Entity".
        """
        return "Entity"

    def isAbstract(self) -> bool:  # Renamed
        """
        Checks if the entity is abstract.

        Returns:
            bool: True if the entity is abstract, False otherwise.
        """
        return self._abstract

    def setAbstract(self, is_abstract: bool) -> None:  # Renamed
        """
        Sets the abstract status of the entity.

        Args:
            is_abstract: True to set the entity as abstract, False otherwise.
        """
        self._abstract = is_abstract

    def getAttributes(self) -> List[Attribute]:  # Renamed
        """
        Gets the direct attributes of this entity.

        Returns:
            List[Attribute]: A list of attributes directly associated with this entity.
        """
        return self._attributes

    def getTop(self) -> str:  # Renamed
        """
        Finds the name of the top-level ancestor entity in the hierarchy.
        The top-level is considered the one whose parent is named "Entity" or "Relationship".

        Returns:
            str: The name of the top-level entity.
        """
        if self._parent.getName() in ["Entity", "Relationship"]:  # Updated call
            return self.getName()  # Updated call
        return self._parent.getTop()  # Updated call

    def getAllAttributes(self) -> List[Attribute]:  # Renamed
        """
        Gets all attributes of this entity, including inherited attributes from its ancestors.

        Returns:
            List[Attribute]: A list of all attributes (inherited and direct).
        """
        pathAttributes: List[Attribute] = []  # Renamed variable
        if self._parent is not None:
            pathAttributes = self._parent.getAllAttributes()  # Updated call
        pathAttributes.extend(self.getAttributes())  # Updated call
        return pathAttributes

    def getAllAttributesToString(self) -> List[str]:  # Renamed
        """
        Gets the names of all attributes (inherited and direct) as a list of strings.

        Returns:
            List[str]: A list of attribute names.
        """
        return [attr.getName() for attr in self.getAllAttributes()]  # Updated call

    def getMandatoryAttributes(self) -> List[Attribute]:  # Renamed
        """
        Gets all mandatory attributes (inherited and direct) for this entity.

        Returns:
            List[Attribute]: A list of mandatory attributes.
        """
        mandatoryAttributes: List[Attribute] = []  # Renamed variable
        allAttributes = self.getAllAttributes()  # Updated call
        for attr in allAttributes:
            if attr.isMandatory():
                mandatoryAttributes.append(attr)
        return mandatoryAttributes

    def addChild(self, child: Entity) -> None:  # Renamed
        """
        Adds a child entity to this entity and sets its parent.

        Args:
            child: The child entity to add.
        """
        self._children.append(child)
        child.setParent(self)  # Updated call

    def removeAllAttributes(self, entity: Entity) -> None:  # Renamed
        """
        Removes all attributes from this entity that are also present in the given entity.

        Args:
            entity: The entity whose attributes should be removed from this entity.
        """
        attributesToRemove = {attr.getName() for attr in entity.getAttributes()}  # Renamed variable, updated calls
        self._attributes = [attr for attr in self._attributes if attr.getName() not in attributesToRemove]  # Updated call

    def getChild(self, name: str) -> Optional[Entity]:  # Renamed
        """
        Finds a direct child entity by its name (case-insensitive).

        Args:
            name: The name of the child entity to find.

        Returns:
            Optional[Entity]: The found child entity, or None if not found.
        """
        for e in self.getChildren():  # Updated call
            if e.getName().lower() == name.lower():  # Updated call
                return e
        return None

    def run(self) -> None:
        """
        Placeholder method, equivalent to the empty run() in Java.
        """
        pass

    def getChildren(self) -> List[Entity]:  # Renamed
        """
        Gets the direct children of this entity.

        Returns:
            List[Entity]: A list of direct child entities.
        """
        return self._children

    def getChildrenToString(self) -> List[str]:  # Renamed
        """
        Gets the names of the direct children as a list of strings.

        Returns:
            List[str]: A list of child entity names.
        """
        return [e.getName() for e in self.getChildren()]  # Updated calls

    def setChildren(self, children: List[Entity]) -> None:  # Renamed
        """
        Sets the list of direct children for this entity.
        Warning: This replaces the existing children and does not automatically update parent references.

        Args:
            children: The list of child entities to set.
        """
        self._children = children

    def getParent(self) -> Optional[Entity]:  # Renamed
        """
        Gets the parent entity of this entity.

        Returns:
            Optional[Entity]: The parent entity, or None if it's a top-level entity.
        """
        return self._parent

    def setParent(self, parent: Optional[Entity]) -> None:  # Renamed
        """
        Sets the parent entity of this entity.

        Args:
            parent: The entity to set as the parent.
        """
        self._parent = parent

    def getNewAttributes(self) -> List[Attribute]:  # Renamed
        """
        Gets attributes defined directly in this entity that are not present in its parent.

        Returns:
            List[Attribute]: A list of attributes unique to this entity compared to its parent.
                           Returns all direct attributes if there is no parent.
        """
        if self._parent is None:
            return self.getAttributes()  # Updated call

        parentAttributeNames = {attr.getName() for attr in self._parent.getAttributes()}  # Renamed variable, updated calls
        newAttributes = [
            attr for attr in self.getAttributes()  # Updated call
            if attr.getName() not in parentAttributeNames  # Updated call
        ]
        return newAttributes

    def getAttributesToString(self) -> List[str]:  # Renamed
        """
        Gets the names of the direct attributes of this entity as a list of strings.

        Returns:
            List[str]: A list of direct attribute names.
        """
        return [attr.getName() for attr in self._attributes if attr.getName()]  # Updated call

    def getAttribute(self, attributeName: str) -> Optional[Attribute]:  # Renamed, updated arg name
        """
        Finds a direct attribute of this entity by its name.

        Args:
            attributeName: The name of the attribute to find.

        Returns:
            Optional[Attribute]: The found attribute, or None if not found directly on this entity.
        """
        for a in self._attributes:
            if a.getName() == attributeName:  # Updated call
                return a
        return None

    def __eq__(self, other: object) -> bool:
        """
        Checks if this entity is equal to another object.
        Equality is based on name and domain.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if not isinstance(other, Entity):
            return NotImplemented
        if self.getName() != other.getName():  # Updated call
            return False
        selfDomain = self.getDomain()  # Updated call
        otherDomain = other.getDomain()  # Updated call
        if selfDomain is None:
            return otherDomain is None
        else:
            return selfDomain == otherDomain

    def __str__(self) -> str:
        """
        Returns the string representation of the entity, which is its name.

        Returns:
            str: The name of the entity.
        """
        return self.getName()  # Updated call

    def addAttribute(self, attr: Attribute) -> None:  # Renamed
        """
        Adds a single attribute to the entity's direct attributes.
        Does not check for duplicates.

        Args:
            attr: The attribute to add.
        """
        self._attributes.append(attr)

    def addAttributes(self, attrs: List[Attribute]) -> None:  # Renamed
        """
        Adds a list of attributes to the entity. If an attribute with the same name
        already exists, it is replaced by the new one.

        Args:
            attrs: A list of attributes to add or update.
        """
        existingAttrMap = {a.getName(): a for a in self._attributes if a.getName()}  # Renamed variable, updated call
        for newAttr in attrs:  # Renamed variable
            newAttrName = newAttr.getName()  # Renamed variable, updated call
            if newAttrName in existingAttrMap:
                self._attributes.remove(existingAttrMap[newAttrName])
            self._attributes.append(newAttr)
            existingAttrMap[newAttrName] = newAttr

    def removeAttribute(self, attributeName: str) -> None:  # Renamed, updated arg name
        """
        Removes a direct attribute from the entity by its name.
        If multiple attributes have the same name, only the first one found is removed.

        Args:
            attributeName: The name of the attribute to remove.
        """
        attributeToRemove = self.getAttribute(attributeName)  # Renamed variable, updated call
        if attributeToRemove:
            self._attributes.remove(attributeToRemove)

    def setAttributes(self, attributes: List[Attribute]) -> None:  # Renamed
        """
        Sets the list of direct attributes for this entity, replacing any existing ones.

        Args:
            attributes: The list of attributes to set.
        """
        self._attributes = attributes

    def findSubClass(self, nameSubClass: str) -> Optional[Entity]:  # Renamed, updated arg name
        """
        Recursively searches for a subclass (including self) with the given name.

        Args:
            nameSubClass: The name of the subclass to find.

        Returns:
            Optional[Entity]: The found entity, or None if not found in the subtree.
        """
        if self.getName() == nameSubClass:  # Updated call
            return self
        else:
            for e in self._children:
                subClass = e.findSubClass(nameSubClass)  # Renamed variable, updated call
                if subClass is not None:
                    return subClass
            return None

    def getClassPath(self) -> List[Entity]:  # Renamed
        """
        Gets the path from the root entity down to this entity.

        Returns:
            List[Entity]: A list of entities representing the path, starting from the root.
        """
        path: List[Entity] = []
        if self._parent is not None:
            path = self._parent.getClassPath()  # Updated call
        path.append(self)
        return path

    def getAllSubclassNames(self, subclassRestriction: bool) -> List[str]:  # Renamed, updated arg name
        """
        Gets the names of all subclasses in the hierarchy starting from this entity.

        Args:
            subclassRestriction: If True, only returns the name of the current entity.
                                  If False, returns names of all descendants (including self).

        Returns:
            List[str]: A list of subclass names based on the restriction.
        """
        if subclassRestriction:
            return [self.getName()]  # Updated call
        else:
            return self.getAllSubclassesToString()  # Updated call

    def getAllSubclasses(self) -> List[Entity]:  # Renamed
        """
        Recursively gets all descendant entities, including this entity itself.

        Returns:
            List[Entity]: A list containing this entity and all its descendants.
        """
        subclasses: List[Entity] = [self]
        for e in self._children:
            subclasses.extend(e.getAllSubclasses())  # Updated call
        return subclasses

    def getAllSubclassesToString(self) -> List[str]:  # Renamed
        """
        Recursively gets the names of all descendant entities, including this entity's name.

        Returns:
            List[str]: A list of names of this entity and all its descendants.
        """
        subclasses: List[str] = [self.getName()]  # Updated call
        for e in self._children:
            subclasses.extend(e.getAllSubclassesToString())  # Updated call
        return subclasses

    def getSubclassesTree(self) -> TreeNode:  # Renamed
        """
        Builds a tree structure (using DefaultTreeNode) representing the subclass hierarchy
        starting from this entity.

        Returns:
            TreeNode: The root node of the subclass tree.
        """
        from .TreeNode import TreeNode
        from .DefaultTreeNode import DefaultTreeNode

        rootClassNode: TreeNode = DefaultTreeNode(data=self)  # Renamed variable
        for e in self._children:
            childNode = e.getSubclassesTree()  # Renamed variable, updated call
            rootClassNode.getChildren().append(childNode)  # Manually append if constructor doesn't
            childNode.setParent(rootClassNode)  # Ensure parent is set
        return rootClassNode

    def existsSubclass(self, subclassName: str) -> Optional[Entity]:  # Renamed, updated arg name
        """
        Recursively checks if a subclass with the given name exists in the hierarchy
        starting from this entity (including self).

        Args:
            subclassName: The name of the subclass to check for.

        Returns:
            Optional[Entity]: The found entity, or None if not found.
        """
        if self.getName() == subclassName:  # Updated call
            return self
        else:
            for e in self._children:
                found = e.existsSubclass(subclassName)  # Updated call
                if found is not None:
                    return found
        return None

    def isTopClass(self) -> bool:  # Renamed
        """
        Checks if this entity is a top-level class (its parent is the universal root).
        Uses the universalClassName for the check.

        Returns:
            bool: True if it's a top-level class, False otherwise.
        """
        return self._parent is not None and self._parent.getName() == self.universalClassName  # Updated call

    def hasChild(self, entityName: str) -> bool:  # Renamed, updated arg name
        """
        Checks if this entity has a direct child with the given name (case-insensitive).

        Args:
            entityName: The name of the child entity to check for.

        Returns:
            bool: True if a direct child with that name exists, False otherwise.
        """
        for e in self.getChildren():  # Updated call
            if e.getName().lower() == entityName.lower():  # Updated call
                return True
        return False

    def hasAncestor(self, entityName: str) -> bool:  # Renamed, updated arg name
        """
        Checks if this entity has an ancestor with the given name.

        Args:
            entityName: The name of the ancestor to check for.

        Returns:
            bool: True if an ancestor with that name exists, False otherwise.
        """
        e = self._parent
        while e is not None and e.getName() != "Entity":  # Updated call
            if e.getName() == entityName:  # Updated call
                return True
            e = e.getParent()  # Updated call
        return False

    def _removeChild(self, childName: str) -> None:  # Renamed, updated arg name
        """
        Removes a direct child entity by its name (case-insensitive).
        Internal helper method.

        Args:
            childName: The name of the child to remove.
        """
        childToRemove = None  # Renamed variable
        for child in self._children:
            if child.getName().lower() == childName.lower():  # Updated call
                childToRemove = child
                break
        if childToRemove:
            self._children.remove(childToRemove)
            childToRemove.setParent(None)  # Updated call

    def detach(self) -> None:
        """
        Detaches this entity from its parent's list of children.
        """
        if self._parent:
            self._parent._removeChild(self.getName())  # Updated calls

    def getValues(self) -> List[str]:  # Renamed
        """
        Gets the list of values associated with this entity instance.

        Returns:
            List[str]: The list of values.
        """
        return self._values

    def setValues(self, values: List[str]) -> None:  # Renamed
        """
        Sets the list of values for this entity instance.

        Args:
            values: The list of values to set.
        """
        self._values = values

    def getGraphBrainID(self) -> Optional[str]:  # Renamed
        """
        Gets the GraphBrain ID associated with this entity.

        Returns:
            Optional[str]: The GraphBrain ID, or None if not set.
        """
        return self._graphBrainID

    def setGraphBrainID(self, graphBrainID: str) -> None:  # Renamed, updated arg name
        """
        Sets the GraphBrain ID for this entity.

        Args:
            graphBrainID: The GraphBrain ID to set.
        """
        self._graphBrainID = graphBrainID

