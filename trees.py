"""
Trees Module
Implements:
- Binary Tree Node
- Binary Search Tree (BST) with insert, search, delete, min, max
- Traversals: Inorder, Preorder, Postorder, Level-Order (BFS)
- Tree metrics: height, node count, BST validity check
- AVL Tree basics: Balance factor calculations and rotations (Left, Right)
"""

from typing import List, Any, Optional, Dict


class TreeNode:
    """Node for Binary Tree / BST / AVL."""
    def __init__(self, key: Any):
        self.key: Any = key
        self.left: Optional["TreeNode"] = None
        self.right: Optional["TreeNode"] = None
        self.height: int = 1  # For AVL balancing


class BinarySearchTree:
    """Manual Binary Search Tree implementation."""

    def __init__(self):
        self.root: Optional[TreeNode] = None

    def insert(self, key: Any) -> None:
        """
        Insert key into BST: O(h) where h = height of tree.
        O(log n) average, O(n) worst-case.
        """
        if self.root is None:
            self.root = TreeNode(key)
        else:
            self._insert_rec(self.root, key)

    def _insert_rec(self, node: TreeNode, key: Any) -> TreeNode:
        if key < node.key:
            if node.left is None:
                node.left = TreeNode(key)
            else:
                self._insert_rec(node.left, key)
        elif key > node.key:
            if node.right is None:
                node.right = TreeNode(key)
            else:
                self._insert_rec(node.right, key)
        # Duplicate keys ignored
        return node

    def search(self, key: Any) -> Optional[TreeNode]:
        """Search key: O(h)."""
        curr = self.root
        while curr is not None:
            if key == curr.key:
                return curr
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def delete(self, key: Any) -> None:
        """Delete key from BST handling 0, 1, or 2 children."""
        self.root = self._delete_rec(self.root, key)

    def _delete_rec(self, node: Optional[TreeNode], key: Any) -> Optional[TreeNode]:
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_rec(node.left, key)
        elif key > node.key:
            node.right = self._delete_rec(node.right, key)
        else:
            # Case 1 & 2: 0 or 1 child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Case 3: 2 children - get inorder successor (smallest in right subtree)
            successor = self._min_value_node(node.right)
            node.key = successor.key
            node.right = self._delete_rec(node.right, successor.key)

        return node

    def _min_value_node(self, node: TreeNode) -> TreeNode:
        curr = node
        while curr.left is not None:
            curr = curr.left
        return curr

    def inorder(self) -> List[Any]:
        """Inorder traversal (Left, Root, Right): yields keys in sorted order."""
        result: List[Any] = []
        def _inorder(node: Optional[TreeNode]):
            if node:
                _inorder(node.left)
                result.append(node.key)
                _inorder(node.right)
        _inorder(self.root)
        return result

    def preorder(self) -> List[Any]:
        """Preorder traversal (Root, Left, Right)."""
        result: List[Any] = []
        def _preorder(node: Optional[TreeNode]):
            if node:
                result.append(node.key)
                _preorder(node.left)
                _preorder(node.right)
        _preorder(self.root)
        return result

    def postorder(self) -> List[Any]:
        """Postorder traversal (Left, Right, Root)."""
        result: List[Any] = []
        def _postorder(node: Optional[TreeNode]):
            if node:
                _postorder(node.left)
                _postorder(node.right)
                result.append(node.key)
        _postorder(self.root)
        return result

    def level_order(self) -> List[Any]:
        """Breadth-First / Level-Order traversal using queue."""
        if not self.root:
            return []
        result: List[Any] = []
        queue: List[TreeNode] = [self.root]
        idx = 0
        while idx < len(queue):
            curr = queue[idx]
            idx += 1
            result.append(curr.key)
            if curr.left:
                queue.append(curr.left)
            if curr.right:
                queue.append(curr.right)
        return result

    def height(self) -> int:
        """Calculate max tree depth: O(n)."""
        def _h(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            return 1 + max(_h(node.left), _h(node.right))
        return _h(self.root)

    def is_valid_bst(self) -> bool:
        """Validates BST property."""
        def _validate(node: Optional[TreeNode], min_val: Any, max_val: Any) -> bool:
            if not node:
                return True
            if (min_val is not None and node.key <= min_val) or (max_val is not None and node.key >= max_val):
                return False
            return _validate(node.left, min_val, node.key) and _validate(node.right, node.key, max_val)
        return _validate(self.root, None, None)


class AVLTreeDemo:
    """
    Self-balancing AVL Tree demonstrating rotations:
    - Left Rotation (RR Imbalance)
    - Right Rotation (LL Imbalance)
    - Left-Right Rotation (LR Imbalance)
    - Right-Left Rotation (RL Imbalance)
    """

    @staticmethod
    def get_height(node: Optional[TreeNode]) -> int:
        return node.height if node else 0

    @staticmethod
    def get_balance(node: Optional[TreeNode]) -> int:
        if not node:
            return 0
        return AVLTreeDemo.get_height(node.left) - AVLTreeDemo.get_height(node.right)

    @staticmethod
    def right_rotate(y: TreeNode) -> TreeNode:
        """Right rotate on y (LL case)."""
        x = y.left
        assert x is not None
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.height = 1 + max(AVLTreeDemo.get_height(y.left), AVLTreeDemo.get_height(y.right))
        x.height = 1 + max(AVLTreeDemo.get_height(x.left), AVLTreeDemo.get_height(x.right))
        return x

    @staticmethod
    def left_rotate(x: TreeNode) -> TreeNode:
        """Left rotate on x (RR case)."""
        y = x.right
        assert y is not None
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = 1 + max(AVLTreeDemo.get_height(x.left), AVLTreeDemo.get_height(x.right))
        y.height = 1 + max(AVLTreeDemo.get_height(y.left), AVLTreeDemo.get_height(y.right))
        return y

