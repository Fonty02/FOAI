from datetime import datetime

class Author:
    def __init__(self):
        self.id: int = None
        self.graph_id: int = None
        self.type: str = None
        self.attributeKey: str = None
        self.attributeValue: str = None
        self.description: str = None
        self. creationDate: datetime = None
        self.username: str = None
        self.isActive: bool = None
    
    def getId(self) -> int:
        return self.id
        
    def setId(self, id: int) -> None:
        self.id = id
        
    def getGraph_id(self) -> int:
        return self.graph_id
        
    def setGraph_id(self, graph_id: int) -> None:
        self.graph_id = graph_id
        
    def getType(self) -> str:
        return self.type
        
    def setType(self, type: str) -> None:
        self.type = type
        
    def getAttributeKey(self) -> str:
        return self.attributeKey
        
    def setAttributeKey(self, attribute_key: str) -> None:
        self.attributeKey = attribute_key
        
    def getAttributeValue(self) -> str:
        return self.attributeValue
        
    def setAttributeValue(self, attribute_value: str) -> None:
        self.attributeValue = attribute_value
        
    def getDescription(self) -> str:
        return self.description
        
    def setDescription(self, description: str) -> None:
        self.description = description
        
    def getCreationDate(self) -> datetime:
        return self.creationDate
        
    def setCreationDate(self, creation_date: datetime) -> None:
        self.creationDate = creation_date
        
    def getUsername(self) -> str:
        return self.username
        
    def setUsername(self, username: str) -> None:
        self.username = username
        
    def getIsActive(self) -> bool:
        return self.isActive
        
    def setIsActive(self, is_active: bool) -> None:
        self.isActive = is_active
