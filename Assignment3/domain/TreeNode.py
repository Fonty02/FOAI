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

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_children(self):
        return self.children

    def get_parent(self):
        return self.parent

    def set_parent(self, parent_node):
        # Optional: Remove from previous parent's children list if exists
        if self.parent:
            self.parent.remove_child(self)
        self.parent = parent_node
        # Optional: Add to new parent's children list if not already there
        if parent_node is not None and self not in parent_node.children:
             parent_node.children.append(self)


    def add_child(self, child_node):
        """Adds a child node and sets its parent to this node."""
        child_node.set_parent(self) # Use set_parent to handle potential previous parent

    def remove_child(self, child_node):
        """Removes a child node."""
        if child_node in self.children:
            self.children.remove(child_node)
            child_node.parent = None # Clear the child's parent reference

    def get_child_count(self):
        return len(self.children)

    def is_leaf(self):
        return self.get_child_count() == 0

    def get_type(self):
        return self.type

    def set_type(self, node_type):
        self.type = node_type

    def is_expanded(self):
        return self.expanded

    def set_expanded(self, expanded):
        self.expanded = expanded

    def is_selected(self):
        return self.selected

    def set_selected(self, selected):
        self.selected = selected
        
    def get_row_key(self):
        return self.row_key

    def set_row_key(self, row_key):
        self.row_key = row_key

    # Optional: Method to clear parent relationship
    def clear_parent(self):
        self.parent = None

    # Optional: String representation for easier debugging
    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"TreeNode(data={self.data}, children={len(self.children)})"