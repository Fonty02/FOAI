from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

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
    values: List[str] = []  # List of values associated with this entity instance
    graphBrainID: Optional[str] = None  # GraphBrain ID for this entity
    attributes: List[Attribute] = []  # List of attributes directly associated with this entity
    children: List[Entity] = []  # List of child entities
    parent: Optional[Entity] = None  # Parent entity
    _abstract: bool = False  # Indicates if the entity is abstract
    name: str  # Name of the entity

    def __init__(self, name: str, domain: Optional[str] = None):
        """
        Initializes a new Entity object.

        Args:
            name: The name of the entity.
            domain: The domain the entity belongs to (optional).
        """
        super().__init__()
        self.name: str = name
        if domain:
            self.setDomain(domain)
        self.values: List[str] = []
        self.graphBrainID: Optional[str] = None   
        self.attributes: List[Attribute] = []
        self.children: List[Entity] = []
        self.parent: Optional[Entity] = None
        self._abstract: bool = False

    def get_domain_type(self) -> str:
        """
        Returns the type of this domain tag.

        Returns:
            str: The type, which is "Entity".
        """
        return "Entity"

    def isAbstract(self) -> bool:  
        """
        Checks if the entity is abstract.

        Returns:
            bool: True if the entity is abstract, False otherwise.
        """
        return self._abstract

    def setAbstract(self, is_abstract: bool) -> None:  
        """
        Sets the abstract status of the entity.

        Args:
            is_abstract: True to set the entity as abstract, False otherwise.
        """
        self._abstract = is_abstract

    def getAttributes(self) -> List[Attribute]:  
        """
        Gets the direct attributes of this entity.

        Returns:
            List[Attribute]: A list of attributes directly associated with this entity.
        """
        return self.attributes

    def getTop(self) -> str:  
        """
        Finds the name of the top-level ancestor entity in the hierarchy.
        The top-level is considered the one whose parent is named "Entity" or "Relationship".

        Returns:
            str: The name of the top-level entity.
        """
        if self.parent.getName() in ["Entity", "Relationship"]:  
            return self.getName()  
        return self.parent.getTop()  

    def getAllAttributes(self) -> List[Attribute]:  
        """
        Gets all attributes of this entity, including inherited attributes from its ancestors.

        Returns:
            List[Attribute]: A list of all attributes (inherited and direct).
        """
        pathAttributes: List[Attribute] = []  
        if self.parent is not None:
            pathAttributes = self.parent.getAllAttributes()  
        pathAttributes.extend(self.getAttributes())  
        return pathAttributes

    def getAllAttributesToString(self) -> List[str]:  
        """
        Gets the names of all attributes (inherited and direct) as a list of strings.

        Returns:
            List[str]: A list of attribute names.
        """
        return [attr.getName() for attr in self.getAllAttributes()]  

    def getMandatoryAttributes(self) -> List[Attribute]:  
        """
        Gets all mandatory attributes (inherited and direct) for this entity.

        Returns:
            List[Attribute]: A list of mandatory attributes.
        """
        mandatoryAttributes: List[Attribute] = []  
        allAttributes = self.getAllAttributes()  
        for attr in allAttributes:
            if attr.isMandatory():
                mandatoryAttributes.append(attr)
        return mandatoryAttributes

    def addChild(self, child: Entity) -> None:  
        """
        Adds a child entity to this entity and sets its parent.

        Args:
            child: The child entity to add.
        """
        self.children.append(child)
        child.setParent(self)  

    def removeAllAttributes(self, entity: Entity) -> None:  
        """
        Removes all attributes from this entity that are also present in the given entity.

        Args:
            entity: The entity whose attributes should be removed from this entity.
        """
        attributesToRemove = {attr.getName() for attr in entity.getAttributes()}
        self.attributes = [attr for attr in self.attributes if attr.getName() not in attributesToRemove]  

    def getChild(self, name: str) -> Optional[Entity]:  
        """
        Finds a direct child entity by its name (case-insensitive).

        Args:
            name: The name of the child entity to find.

        Returns:
            Optional[Entity]: The found child entity, or None if not found.
        """
        for e in self.getChildren():  
            if e.getName().lower() == name.lower():  
                return e
        return None

    def run(self) -> None:
        """
        Placeholder method, equivalent to the empty run() in Java.
        """
        pass

    def getChildren(self) -> List[Entity]:  
        """
        Gets the direct children of this entity.

        Returns:
            List[Entity]: A list of direct child entities.
        """
        return self.children

    def getChildrenToString(self) -> List[str]:  
        """
        Gets the names of the direct children as a list of strings.

        Returns:
            List[str]: A list of child entity names.
        """
        return [e.getName() for e in self.getChildren()]

    def setChildren(self, children: List[Entity]) -> None:  
        """
        Sets the list of direct children for this entity.
        Warning: This replaces the existing children and does not automatically update parent references.

        Args:
            children: The list of child entities to set.
        """
        self.children = children

    def getParent(self) -> Optional[Entity]:  
        """
        Gets the parent entity of this entity.

        Returns:
            Optional[Entity]: The parent entity, or None if it's a top-level entity.
        """
        return self.parent

    def setParent(self, parent: Optional[Entity]) -> None:  
        """
        Sets the parent entity of this entity.

        Args:
            parent: The entity to set as the parent.
        """
        self.parent = parent

    def getNewAttributes(self) -> List[Attribute]:  
        """
        Gets attributes defined directly in this entity that are not present in its parent.

        Returns:
            List[Attribute]: A list of attributes unique to this entity compared to its parent.
                           Returns all direct attributes if there is no parent.
        """ 
        parentAttributeNames = {attr.getName() for attr in self.parent.getAttributes()}
        newAttributes = [
            attr for attr in self.getAttributes()  
            if attr.getName() not in parentAttributeNames  
        ]
        return newAttributes

    def getAttributesToString(self) -> List[str]:  
        """
        Gets the names of the direct attributes of this entity as a list of strings.

        Returns:
            List[str]: A list of direct attribute names.
        """
        return [attr.getName() for attr in self.attributes if attr.getName()]  

    def getAttribute(self, attributeName: str) -> Optional[Attribute]:
        """
        Finds a direct attribute of this entity by its name.

        Args:
            attributeName: The name of the attribute to find.

        Returns:
            Optional[Attribute]: The found attribute, or None if not found directly on this entity.
        """
        for a in self.attributes:
            if a.getName() == attributeName:  
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
        if self.getName() != other.getName():  
            return False
        selfDomain = self.getDomain()  
        otherDomain = other.getDomain()  
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
        return self.getName()  

    def addAttribute(self, attr: Attribute) -> None:  
        """
        Adds a single attribute to the entity's direct attributes.
        Does not check for duplicates.

        Args:
            attr: The attribute to add.
        """
        self.attributes.append(attr)

    def addAttributes(self, attrs: List[Attribute]) -> None:  
        """
        Adds a list of attributes to the entity. If an attribute with the same name
        already exists, it is replaced by the new one.

        Args:
            attrs: A list of attributes to add or update.
        """
        existingAttrMap = {a.getName(): a for a in self.attributes if a.getName()}  
        for newAttr in attrs:  
            newAttrName = newAttr.getName()  
            if newAttrName in existingAttrMap:
                self.attributes.remove(existingAttrMap[newAttrName])
            self.attributes.append(newAttr)
            existingAttrMap[newAttrName] = newAttr

    def removeAttribute(self, attributeName: str) -> None:  
        """
        Removes a direct attribute from the entity by its name.
        If multiple attributes have the same name, only the first one found is removed.

        Args:
            attributeName: The name of the attribute to remove.
        """
        attributeToRemove = self.getAttribute(attributeName)  
        if attributeToRemove:
            self.attributes.remove(attributeToRemove)

    def setAttributes(self, attributes: List[Attribute]) -> None:  
        """
        Sets the list of direct attributes for this entity, replacing any existing ones.

        Args:
            attributes: The list of attributes to set.
        """
        self.attributes = attributes

    def findSubClass(self, nameSubClass: str) -> Optional[Entity]:  
        """
        Recursively searches for a subclass (including self) with the given name.

        Args:
            nameSubClass: The name of the subclass to find.

        Returns:
            Optional[Entity]: The found entity, or None if not found in the subtree.
        """
        if self.getName() == nameSubClass:  
            return self
        else:
            for e in self.children:
                subClass = e.findSubClass(nameSubClass)  
                if subClass is not None:
                    return subClass
            return None

    def getClassPath(self) -> List[Entity]:  
        """
        Gets the path from the root entity down to this entity.

        Returns:
            List[Entity]: A list of entities representing the path, starting from the root.
        """
        path: List[Entity] = []
        if self.parent is not None:
            path = self.parent.getClassPath()  
        path.append(self)
        return path

    def getAllSubclassNames(self, subclassRestriction: bool) -> List[str]:  
        """
        Gets the names of all subclasses in the hierarchy starting from this entity.

        Args:
            subclassRestriction: If True, only returns the name of the current entity.
                                  If False, returns names of all descendants (including self).

        Returns:
            List[str]: A list of subclass names based on the restriction.
        """
        if subclassRestriction:
            return [self.getName()]  
        else:
            return self.getAllSubclassesToString()  

    def getAllSubclasses(self) -> List[Entity]:  
        """
        Recursively gets all descendant entities, including this entity itself.

        Returns:
            List[Entity]: A list containing this entity and all its descendants.
        """
        subclasses: List[Entity] = [self]
        for e in self.children:
            subclasses.extend(e.getAllSubclasses())  
        return subclasses

    def getAllSubclassesToString(self) -> List[str]:  
        """
        Recursively gets the names of all descendant entities, including this entity's name.

        Returns:
            List[str]: A list of names of this entity and all its descendants.
        """
        subclasses: List[str] = [self.getName()]  
        for e in self.children:
            subclasses.extend(e.getAllSubclassesToString())  
        return subclasses

    def getSubclassesTree(self) -> TreeNode:  
        """
        Builds a tree structure (using DefaultTreeNode) representing the subclass hierarchy
        starting from this entity.

        Returns:
            TreeNode: The root node of the subclass tree.
        """
        from .TreeNode import TreeNode
        from .DefaultTreeNode import DefaultTreeNode

        rootClassNode: TreeNode = DefaultTreeNode(data=self)  
        for e in self.children:
            childNode = e.getSubclassesTree()  
            rootClassNode.getChildren().append(childNode)  # Manually append if constructor doesn't
            childNode.setParent(rootClassNode)  # Ensure parent is set
        return rootClassNode

    def existsSubclass(self, subclassName: str) -> Optional[Entity]:  
        """
        Recursively checks if a subclass with the given name exists in the hierarchy
        starting from this entity (including self).

        Args:
            subclassName: The name of the subclass to check for.

        Returns:
            Optional[Entity]: The found entity, or None if not found.
        """
        if self.getName() == subclassName:  
            return self
        else:
            for e in self.children:
                found = e.existsSubclass(subclassName)  
                if found is not None:
                    return found
        return None

    def isTopClass(self) -> bool:  
        """
        Checks if this entity is a top-level class (its parent is the universal root).
        Uses the universalClassName for the check.

        Returns:
            bool: True if it's a top-level class, False otherwise.
        """
        return self.parent.getName() == self.universalClassName  

    def hasChild(self, entityName: str) -> bool:  
        """
        Checks if this entity has a direct child with the given name (case-insensitive).

        Args:
            entityName: The name of the child entity to check for.

        Returns:
            bool: True if a direct child with that name exists, False otherwise.
        """
        for e in self.getChildren():  
            if e.getName().lower() == entityName.lower():  
                return True
        return False

    def hasAncestor(self, entityName: str) -> bool:  
        """
        Checks if this entity has an ancestor with the given name.

        Args:
            entityName: The name of the ancestor to check for.

        Returns:
            bool: True if an ancestor with that name exists, False otherwise.
        """
        e = self.parent
        while e is not None and e.getName() != "Entity":  
            if e.getName() == entityName:  
                return True
            e = e.getParent()  
        return False

    def removeChild(self, childName: str) -> None:  
        """
        Removes a direct child entity by its name (case-insensitive).
        Internal helper method.

        Args:
            childName: The name of the child to remove.
        """
        childToRemove = None  
        for child in self.children:
            if child.getName().lower() == childName.lower():  
                childToRemove = child
                break
        if childToRemove:
            self.children.remove(childToRemove)
            childToRemove.setParent(None)  

    def detach(self) -> None:
        """
        Detaches this entity from its parent's list of children.
        """
        if self.parent:
            self.parent.removeChild(self.getName())

    def getValues(self) -> List[str]:  
        """
        Gets the list of values associated with this entity instance.

        Returns:
            List[str]: The list of values.
        """
        return self.values

    def setValues(self, values: List[str]) -> None:  
        """
        Sets the list of values for this entity instance.

        Args:
            values: The list of values to set.
        """
        self.values = values

    def getGraphBrainID(self) -> Optional[str]:  
        """
        Gets the GraphBrain ID associated with this entity.

        Returns:
            Optional[str]: The GraphBrain ID, or None if not set.
        """
        return self.graphBrainID

    def setGraphBrainID(self, graphBrainID: str) -> None:  
        """
        Sets the GraphBrain ID for this entity.

        Args:
            graphBrainID: The GraphBrain ID to set.
        """
        self.graphBrainID = graphBrainID

