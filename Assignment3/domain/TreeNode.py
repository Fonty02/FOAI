class TreeNode:
    """
    Simple implementation of TreeNode inspired by org.primefaces.model.TreeNode.
    Uses Pythonic conventions (snake_case).
    """
    def __init__(self, data=None, parent=None):
        self.data = data
        self.children = []
        self.parent = parent
        self.expanded = False
        self.selected = False
        # PrimeFaces TreeNode often includes a 'type' attribute
        self.type = "default" 
        # Optional: Row key for UI identification
        self.row_key = None 

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data

    def getChildren(self):
        return self.children

    def getParent(self):
        return self.parent

    def setParent(self, parent_node):
        # Optional: Remove from previous parent's children list if exists
        if self.parent:
            self.parent.removeChild(self)
        self.parent = parent_node
        # Optional: Add to new parent's children list if not already there
        if parent_node is not None and self not in parent_node.children:
             parent_node.children.append(self)


    def addChild(self, child_node):
        """Adds a child node and sets its parent to this node."""
        child_node.setParent(self) # Use set_parent to handle potential previous parent

    def removeChild(self, child_node):
        """Removes a child node."""
        if child_node in self.children:
            self.children.remove(child_node)
            child_node.parent = None # Clear the child's parent reference

    def getChild_count(self):
        return len(self.children)

    def isLeaf(self):
        return self.get_child_count() == 0

    def getType(self):
        return self.type

    def setType(self, node_type):
        self.type = node_type

    def isExpanded(self):
        return self.expanded

    def setExpanded(self, expanded):
        self.expanded = expanded

    def isSelected(self):
        return self.selected

    def setSelected(self, selected):
        self.selected = selected
        
    def getRowKey(self):
        return self.row_key

    def setRowKey(self, row_key):
        self.row_key = row_key

    # Optional: Method to clear parent relationship
    def clearParent(self):
        self.parent = None

    # Optional: String representation for easier debugging
    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"TreeNode(data={self.data}, children={len(self.children)})"