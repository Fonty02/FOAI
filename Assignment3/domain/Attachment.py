class Attachment:
    def __init__(self, p: str, e: str, d: str, f: str):
        self.progr: str = p
        self.extension: str = e
        self.description: str = d
        self.fileName: str = f
    
    
    def getProgr(self) -> str:
        """
        Obtains the progressive number of the attachment.
        
        Returns:
            The progressive number of the attachment.
        """
        return self.progr
    
    
    def getExtension(self) -> str:
        """
        Obtains the file extension.
        
        Returns:
            The file extension.
        """
        return self.extension
    
    
    def getDescription(self) -> str:
        """
        Obtains the description of the attachment.
        
        Returns:
            The description of the attachment.
        """
        return self.description
    
    
    def getFilename(self) -> str:
        """
        Obtains the file name with extension.
        
        Returns:
            The file name with extension.
        """
        return self.fileName + self.extension
