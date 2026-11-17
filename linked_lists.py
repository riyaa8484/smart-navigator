"""
Linked Lists Module
Manual implementations:
- Singly Linked List (insertion, deletion, traversal, search)
- Doubly Linked List (bidirectional traversal, forward/backward operations)
- Circular Linked List (tail pointing back to head)
- In-place Reversal algorithm
- Remove Duplicates from list
- Cycle Detection (Floyd's Tortoise and Hare cycle finding algorithm)
"""

from typing import List, Any, Optional, Dict


class SNode:
    """Singly Linked List Node."""
    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["SNode"] = None


class SinglyLinkedList:
    """Manual Singly Linked List."""

    def __init__(self):
        self.head: Optional[SNode] = None
        self._size = 0

    def append(self, data: Any) -> None:
        """Insert at tail: O(n)."""
        new_node = SNode(data)
        if self.head is None:
            self.head = new_node
        else:
            curr = self.head
            while curr.next is not None:
                curr = curr.next
            curr.next = new_node
        self._size += 1

    def prepend(self, data: Any) -> None:
        """Insert at head: O(1)."""
        new_node = SNode(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def delete(self, key: Any) -> bool:
        """Delete first node containing key: O(n)."""
        curr = self.head
        prev = None
        while curr is not None:
            if curr.data == key:
                if prev is None:
                    self.head = curr.next
                else:
                    prev.next = curr.next
                self._size -= 1
                return True
            prev = curr
            curr = curr.next
        return False

    def reverse(self) -> None:
        """
        Reverse linked list in-place: O(n) time, O(1) space.
        Uses 3 pointers: prev, curr, next_node.
        """
        prev = None
        curr = self.head
        while curr is not None:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node
        self.head = prev

    def remove_duplicates(self) -> None:
        """
        Removes duplicate values: O(n) time, O(n) space using manual hash set.
        """
        if self.head is None:
            return
        seen = set()
        curr = self.head
        seen.add(curr.data)
        while curr.next is not None:
            if curr.next.data in seen:
                curr.next = curr.next.next
                self._size -= 1
            else:
                seen.add(curr.next.data)
                curr = curr.next

    def to_list(self) -> List[Any]:
        result = []
        curr = self.head
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    @classmethod
    def from_list(cls, items: List[Any]) -> "SinglyLinkedList":
        sll = cls()
        for item in items:
            sll.append(item)
        return sll


class DNode:
    """Doubly Linked List Node."""
    def __init__(self, data: Any):
        self.data: Any = data
        self.prev: Optional["DNode"] = None
        self.next: Optional["DNode"] = None


class DoublyLinkedList:
    """Manual Doubly Linked List with head and tail pointers."""

    def __init__(self):
        self.head: Optional[DNode] = None
        self.tail: Optional[DNode] = None
        self._size = 0

    def append(self, data: Any) -> None:
        """Insert at tail: O(1)."""
        new_node = DNode(data)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self._size += 1

    def prepend(self, data: Any) -> None:
        """Insert at head: O(1)."""
        new_node = DNode(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1

    def to_list_forward(self) -> List[Any]:
        items = []
        curr = self.head
        while curr is not None:
            items.append(curr.data)
            curr = curr.next
        return items

    def to_list_backward(self) -> List[Any]:
        items = []
        curr = self.tail
        while curr is not None:
            items.append(curr.data)
            curr = curr.prev
        return items


class CircularLinkedList:
    """Circular Singly Linked List where the last node points to the first."""

    def __init__(self):
        self.head: Optional[SNode] = None
        self._size = 0

    def append(self, data: Any) -> None:
        new_node = SNode(data)
        if self.head is None:
            self.head = new_node
            new_node.next = self.head
        else:
            curr = self.head
            while curr.next != self.head:
                curr = curr.next
            curr.next = new_node
            new_node.next = self.head
        self._size += 1

    def to_list(self) -> List[Any]:
        if self.head is None:
            return []
        items = []
        curr = self.head
        while True:
            items.append(curr.data)
            curr = curr.next
            if curr == self.head:
                break
        return items


class LinkedListAlgorithms:
    """Cycle detection and linked list utilities."""

    @staticmethod
    def has_cycle(head: Optional[SNode]) -> bool:
        """
        Floyd's Tortoise and Hare Cycle-Finding Algorithm.
        Time Complexity: O(n)
        Space Complexity: O(1)
        """
        slow = head
        fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            if slow == fast:
                return True
        return False

