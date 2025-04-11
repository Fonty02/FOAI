from domain.DomainTag import DomainTag
import typing

class Axiom(DomainTag):
    """
    Represents an axiom in a domain.
    """
    
    def __init__(self, name: str, formalism: str, expression: str, domain: str) -> None:
        """
        Constructs a new Axiom object with the specified name, formalism, expression, and domain.
        
        Args:
            name: the name of the axiom
            formalism: the formalism of the axiom
            expression: the expression of the axiom
            domain: the domain of the axiom
        """
        super().__init__()
        self.name = name
        self.formalism = formalism
        self.expression = expression
        self.domain = domain
    
    def getFormalism(self) -> str:
        """
        Returns the formalism of the axiom.
        
        Returns:
            The formalism of the axiom.
        """
        return self.formalism
    
    def setFormalism(self, formalism: str) -> None:
        """
        Sets the formalism of the axiom.
        
        Args:
            formalism: the formalism to set
        """
        self.formalism = formalism
    
    def getExpression(self) -> str:
        """
        Returns the expression of the axiom.
        
        Returns:
            The expression of the axiom.
        """
        return self.expression
    
    def setExpression(self, expression: str) -> None:
        """
        Sets the expression of the axiom.
        
        Args:
            expression: the expression to set
        """
        self.expression = expression
    
    def __eq__(self, other: object) -> bool:
        """
        Indicates whether some other object is "equal to" this one.
        
        Args:
            other: the reference object with which to compare
        
        Returns:
            True if the two Axioms have the same name; false otherwise
        """
        if self is other:
            return True
        if other is None or not isinstance(other, Axiom):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        """
        Returns the hash code value for this Axiom object.
        
        Returns:
            The hash code value for this Axiom object as the hash of the name attribute.
        """
        return hash(self.name)