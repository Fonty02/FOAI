class Attachment:
    def __init__(self, p: str, e: str, d: str, f: str):
        self._progr: str = p
        self._extension: str = e
        self._description: str = d
        self._fileName: str = f
    
    @property
    def progr(self) -> str:
        """
        Obtains the progressive number of the attachment.
        
        Returns:
            The progressive number of the attachment.
        """
        return self._progr
    
    @property
    def extension(self) -> str:
        """
        Obtains the file extension.
        
        Returns:
            The file extension.
        """
        return self._extension
    
    @property
    def description(self) -> str:
        """
        Obtains the description of the attachment.
        
        Returns:
            The description of the attachment.
        """
        return self._description
    
    @property
    def filename(self) -> str:
        """
        Obtains the file name with extension.
        
        Returns:
            The file name with extension.
        """
        return self._fileName + self._extension
