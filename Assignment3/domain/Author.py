from datetime import datetime

class Author:
    def __init__(self):
        self.id: int = None
        self.graph_id: int = None
        self.type: str = None
        self.attribute_key: str = None
        self.attribute_value: str = None
        self.description: str = None
        self.creation_date: datetime = None
        self.username: str = None
        self.is_active: bool = None
    
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
        return self.attribute_key
        
    def setAttributeKey(self, attribute_key: str) -> None:
        self.attribute_key = attribute_key
        
    def getAttributeValue(self) -> str:
        return self.attribute_value
        
    def setAttributeValue(self, attribute_value: str) -> None:
        self.attribute_value = attribute_value
        
    def getDescription(self) -> str:
        return self.description
        
    def setDescription(self, description: str) -> None:
        self.description = description
        
    def getCreationDate(self) -> datetime:
        return self.creation_date
        
    def setCreationDate(self, creation_date: datetime) -> None:
        self.creation_date = creation_date
        
    def getUsername(self) -> str:
        return self.username
        
    def setUsername(self, username: str) -> None:
        self.username = username
        
    def getIsActive(self) -> bool:
        return self.is_active
        
    def setIsActive(self, is_active: bool) -> None:
        self.is_active = is_active
