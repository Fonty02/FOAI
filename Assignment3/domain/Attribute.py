from .Tag import Tag
from .TreeNode import TreeNode
from copy import copy
from typing import List, Optional

class Attribute(Tag):
    """
    Represents an attribute in a domain.
    An attribute can have various properties such as mandatory, distinguishing, display, data type, and values.
    """

    def __init__(self, name: str | None = None, data_type: str | None = None,
                 mandatory: bool | str | None = None, distinguishing: bool = False,
                 display: bool = False, values: List[str] | TreeNode | None = None):
        """
        Initializes a new Attribute object with flexible parameters to handle all constructor variants.

        Args:
            name: The name of the attribute.
            data_type: The data type of the attribute.
            mandatory: Boolean or string indicating if the attribute is mandatory.
            distinguishing: Boolean indicating if the attribute is distinguishing.
            display: Boolean indicating if the attribute is displayable.
            values: List of strings or TreeNode containing values/sub-classes.
        """
        super().__init__()
        self._name: str | None = name
        self.distinguishing: bool = distinguishing
        self.display: bool = display
        self._target: str | None = None
        self._sub_classes: TreeNode | None = None
        self._sub_classes_select: TreeNode | None = None
        self.values: List[str] = []
        self.data_type: str | None = None
        self.mandatory: bool = False

        # Handle mandatory parameter which can be bool or string
        if isinstance(mandatory, str):
            self.mandatory = mandatory.lower() == "true"
        else:
            self.mandatory = bool(mandatory) if mandatory is not None else False

        # Handle values based on their type
        if isinstance(values, TreeNode):
            self._sub_classes = values
            self.values = []
            self.data_type = "taxonomy"
        else:
            self.values = values if values is not None else []
            if data_type is None:
                if values is not None:
                    self.data_type = "select"
                else:
                    self.data_type = None
            else:
                self.data_type = data_type

    def isDescriptive(self) -> bool:
        """
        Checks if the attribute is descriptive.
        An attribute is descriptive if it is mandatory or distinguishing.
        
        Returns:
            bool: True if the attribute is descriptive, False otherwise.
        """
        return self.mandatory or self.distinguishing

    def getMandatory(self) -> bool:
        """
        Gets the mandatory flag of the attribute.
        
        Returns:
            bool: True if the attribute is mandatory, False otherwise.
        """
        return self.mandatory
        
    def isMandatory(self) -> bool:
        """
        Checks if the attribute is mandatory.
        
        Returns:
            bool: True if the attribute is mandatory, False otherwise.
        """
        return self.mandatory
        
    def setMandatory(self, mandatory: bool) -> None:
        """
        Sets the mandatory flag of the attribute.
        
        Args:
            mandatory: True if the attribute is mandatory, False otherwise.
        """
        self.mandatory = mandatory

    def isDistinguishing(self) -> bool:
        """
        Checks if the attribute is distinguishing.
        
        Returns:
            bool: True if the attribute is distinguishing, False otherwise.
        """
        return self.distinguishing
        
    def setDistinguishing(self, distinguishing: bool) -> None:
        """
        Sets the distinguishing flag of the attribute.
        
        Args:
            distinguishing: True if the attribute is distinguishing, False otherwise.
        """
        self.distinguishing = distinguishing

    def getDataType(self) -> Optional[str]:
        """
        Gets the data type of the attribute.
        
        Returns:
            str: The data type of the attribute.
        """
        return self.data_type
        
    def setDataType(self, dataType: str) -> None:
        """
        Sets the data type of the attribute.
        
        Args:
            dataType: The data type of the attribute.
        """
        self.data_type = dataType
    
    def setTarget(self, target: str) -> None:
        """
        Sets the target of the attribute.
        
        Args:
            target: The target of the attribute.
        """
        self._target = target
    
    def getValues(self) -> List[str]:
        """
        Gets the values of the attribute.
        
        Returns:
            List[str]: The values of the attribute.
        """
        return self.values
    
    def getValuesToStringToLower(self) -> List[str]:
        """
        Gets the values of the attribute as a list of lowercase strings.
        
        Returns:
            List[str]: The values of the attribute as lowercase strings.
        """
        return [v.lower() for v in self.values]
    
    def setValues(self, values: List[str]) -> None:
        """
        Sets the values of the attribute.
        
        Args:
            values: The values of the attribute.
        """
        self.values = values

    def removeValues(self) -> None:
        """
        Removes all values from the attribute.
        """
        self.values = []

    def setValuesString(self, values: List[str]) -> None:
        """
        Sets the values of the attribute from a string.
        
        Args:
            values: List of strings 
        """
        self.setValues(values)

    def addValue(self, value: str) -> None:
        """
        Adds a value to the attribute.
        
        Args:
            value: The value to add.
        """
        self.values.append(value)

    def removeValue(self, value: str) -> None:
        """
        Removes a value from the attribute.
        
        Args:
            value: The value to remove.
        """
        self.values.remove(value)

    def getSubClasses(self) -> Optional[TreeNode]:
        """
        Gets the sub-classes of the attribute.
        
        Returns:
            TreeNode: The sub-classes of the attribute.
        """
        return self._sub_classes
    
    def setSubClasses(self, sub_classes: TreeNode) -> None:
        """
        Sets the sub-classes of the attribute.
        
        Args:
            sub_classes: The sub-classes of the attribute.
        """
        self._sub_classes = sub_classes

    def isDisplay(self) -> bool:
        """
        Checks if the attribute is displayable.
        
        Returns:
            bool: True if the attribute is displayable, False otherwise.
        """
        return self.display
    
    def setDisplay(self, display: bool) -> None:
        """
        Sets the display flag of the attribute.
        
        Args:
            display: True if the attribute is displayable, False otherwise.
        """
        self.display = display

    def getDisplay(self) -> bool:
        """
        Gets the display flag of the attribute.
        
        Returns:
            bool: True if the attribute is displayable, False otherwise.
        """
        return self.display
    
    def getTarget(self) -> Optional[str]:
        """
        Gets the target of the attribute.
        
        Returns:
            The target of the attribute.
        """
        return self._target
    
    def getSubClassesSelect(self) -> Optional[TreeNode]:
        """
        Gets the sub-classes select of the attribute.
        
        Returns:
            TreeNode: The sub-classes select of the attribute.
        """
        return self._sub_classes_select
    
    def setSubClassesSelect(self, sub_classes_select: TreeNode) -> None:
        """
        Sets the sub-classes select of the attribute.
        
        Args:
            sub_classes_select: The sub-classes select of the attribute.
        """
        self._sub_classes_select = sub_classes_select

    def getValuesToString(self) -> Optional[str]:
        """
        Gets the values of the attribute as a string.
        
        Returns:
            str: The values of the attribute as a string.
        """
        return ', '.join(self.values) if self.values else None
    
    def __str__(self) -> str:
        return self.name

    def clone(self) -> 'Attribute':
        """
        Creates a shallow copy of the Attribute object.
        
        Returns:
            Attribute: A shallow copy of the Attribute object.
        """
        return copy(self)
