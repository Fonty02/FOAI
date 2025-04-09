class TreeNode:
    """
    Simple implementation of TreeNode to replace org.primefaces.model.TreeNode.
    """
    def __init__(self, data=None):
        self.data = data
        self.children = []
        self.parent = None
        self.expanded = False
        self.selected = False
    
    def add_child(self, child):
        child.parent = self
        self.children.append(child)
        
    def get_children(self):
        return self.children
    
    def get_parent(self):
        return self.parent
    
    def is_expanded(self):
        return self.expanded
    
    def set_expanded(self, expanded):
        self.expanded = expanded