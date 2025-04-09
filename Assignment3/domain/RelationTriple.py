from .Instance import Instance

class RelationTriple:
    """Class representing a triple of subject-relation-object instances."""

    def __init__(self, subject: Instance = None, relation: Instance = None, object: Instance = None):
        """
        Initialize a RelationTriple object.
        
        Args:
            subject: The subject Instance
            relation: The relation Instance
            object: The object Instance
        """
        self.subject: Instance = subject
        self.relation: Instance = relation
        self.object: Instance = object
    
    def getSubject(self) -> Instance:
        """Get the subject instance."""
        return self.subject
    
    def setSubject(self, subject: Instance) -> None:
        """Set the subject instance."""
        self.subject = subject
    
    def getRelation(self) -> Instance:
        """Get the relation instance."""
        return self.relation
    
    def setRelation(self, relation: Instance) -> None:
        """Set the relation instance."""
        self.relation = relation
    
    def getObject(self) -> Instance:
        """Get the object instance."""
        return self.object
    
    def setObject(self, object: Instance) -> None:
        """Set the object instance."""
        self.object = object