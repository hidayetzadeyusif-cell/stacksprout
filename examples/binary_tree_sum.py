from stacksprout import trace, visualize_tree

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

@trace
def tree_sum(node):
    if node is None:
        return 0
    return node.value + tree_sum(node.left) + tree_sum(node.right)

tree = Node(1,
    Node(2, Node(4), Node(5)),
    Node(3)
)

tree_sum(tree)
visualize_tree(tree_sum)
