from .TreeNode import TreeNode

class DefaultTreeNode(TreeNode):
    """
    Simple implementation of DefaultTreeNode inspired by org.primefaces.model.DefaultTreeNode.
    Inherits from TreeNode and provides convenient constructors.
    """

    def __init__(self, type_or_data=None, data_or_parent=None, parent=None):
        """
        Initializes a DefaultTreeNode. Mimics PrimeFaces constructors:
        - DefaultTreeNode()
        - DefaultTreeNode(data)
        - DefaultTreeNode(data, parent)
        - DefaultTreeNode(type, data, parent)
        """
        node_type = "default"
        node_data = None
        node_parent = None

        if parent is not None:
            # Corresponds to DefaultTreeNode(type, data, parent)
            node_type = type_or_data
            node_data = data_or_parent
            node_parent = parent
        elif data_or_parent is not None:
            if isinstance(data_or_parent, TreeNode):
                # Corresponds to DefaultTreeNode(data, parent)
                node_data = type_or_data
                node_parent = data_or_parent
            else:
                # Corresponds to DefaultTreeNode(data) - assuming type_or_data is data
                node_data = type_or_data
                # data_or_parent is likely None or unintended here based on signature patterns
        elif type_or_data is not None:
             # Corresponds to DefaultTreeNode(data) - type_or_data is the data
             node_data = type_or_data
        # Else corresponds to DefaultTreeNode()

        super().__init__(data=node_data, parent=node_parent)
        self.type = node_type

        # Ensure parent relationship is correctly established if parent is provided
        if node_parent:
            node_parent.addChild(self)

    # Inherits all other methods from TreeNode