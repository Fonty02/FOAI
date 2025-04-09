class HallUser:
    def __init__(self, randomId: str, randomUsername: str, randomUsageStatistic: int, randomTrustIndex: float):
        self.id = randomId
        self.username = randomUsername
        self.usageStatistic = randomUsageStatistic
        self.trustIndex = randomTrustIndex

    def getId(self) -> str:
        return self.id

    def setId(self, id: str) -> None:
        self.id = id

    def getUsername(self) -> str:
        return self.username

    def setUsername(self, u: str) -> None:
        self.username = u

    def getTrustIndex(self) -> float:
        return self.trustIndex

    def setTrustIndex(self, t: float) -> None:
        self.trustIndex = t

    def getUsageStatistic(self) -> int:
        return self.usageStatistic

    def setUsageStatistic(self, s: int) -> None:
        self.usageStatistic = s


    """
    Note: The __lt__ and __eq__ methods are used for sorting and comparing HallUser objects. It is not necessary to declare a comparator class like in Java.
    """

    def __lt__(self, other) -> bool:
        if self.usageStatistic != other.usageStatistic:
            return self.usageStatistic > other.usageStatistic  
        return self.trustIndex > other.trustIndex

    def __eq__(self, other) -> bool:
        if not isinstance(other, HallUser):
            return False
        return self.usageStatistic == other.usageStatistic and self.trustIndex == other.trustIndex