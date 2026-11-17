"""
Queues Module
Manual implementation of Queue variants:
- Linear Queue (array-based with front and rear pointers)
- Circular Queue (fixed capacity with modulo arithmetic index wrap)
- Priority Queue (node-based linked list ordered by priority)
- Deque (Double-Ended Queue supporting push/pop at both front and rear)
"""

from typing import List, Any, Optional, Dict


class LinearQueue:
    """Array-based Linear Queue with front and rear indices."""

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.data: List[Optional[Any]] = [None] * capacity
        self.front = 0
        self.rear = -1
        self.count = 0

    def enqueue(self, item: Any) -> None:
        """Enqueue item at rear: O(1)."""
        if self.count >= self.capacity or self.rear >= self.capacity - 1:
            raise OverflowError("Linear Queue Overflow.")
        self.rear += 1
        self.data[self.rear] = item
        self.count += 1

    def dequeue(self) -> Any:
        """Dequeue item from front: O(1)."""
        if self.is_empty():
            raise IndexError("Linear Queue Underflow.")
        val = self.data[self.front]
        self.data[self.front] = None
        self.front += 1
        self.count -= 1
        return val

    def peek(self) -> Optional[Any]:
        if self.is_empty():
            return None
        return self.data[self.front]

    def is_empty(self) -> bool:
        return self.count == 0

    def size(self) -> int:
        return self.count

    def to_list(self) -> List[Any]:
        return [self.data[i] for i in range(self.front, self.rear + 1) if self.data[i] is not None]


class CircularQueue:
    """
    Circular Queue using modulo arithmetic to prevent linear queue drift and reuse slots.
    Formula: rear = (rear + 1) % capacity
    """

    def __init__(self, capacity: int = 5):
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        self.capacity = capacity
        self.data: List[Optional[Any]] = [None] * capacity
        self.front = -1
        self.rear = -1

    def enqueue(self, item: Any) -> bool:
        """
        Insert item into circular queue.
        Condition for full: (rear + 1) % capacity == front
        """
        if (self.rear + 1) % self.capacity == self.front:
            raise OverflowError("Circular Queue is Full.")

        if self.front == -1:  # First element
            self.front = 0
            self.rear = 0
        else:
            self.rear = (self.rear + 1) % self.capacity

        self.data[self.rear] = item
        return True

    def dequeue(self) -> Any:
        """Remove item from circular queue."""
        if self.front == -1:
            raise IndexError("Circular Queue is Empty.")

        val = self.data[self.front]
        self.data[self.front] = None

        if self.front == self.rear:
            # Queue becomes empty
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.capacity

        return val

    def peek(self) -> Optional[Any]:
        if self.is_empty():
            return None
        return self.data[self.front]

    def is_empty(self) -> bool:
        return self.front == -1

    def is_full(self) -> bool:
        return (self.rear + 1) % self.capacity == self.front

    def to_list(self) -> List[Any]:
        if self.is_empty():
            return []
        items = []
        i = self.front
        while True:
            items.append(self.data[i])
            if i == self.rear:
                break
            i = (i + 1) % self.capacity
        return items

    def state_dict(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "front": self.front,
            "rear": self.rear,
            "is_full": self.is_full(),
            "is_empty": self.is_empty(),
            "items": self.to_list(),
            "raw_buffer": self.data
        }


class PQNode:
    """Linked list node for Priority Queue."""
    def __init__(self, value: Any, priority: float):
        self.value = value
        self.priority = priority  # Lower number = higher priority (Min-Priority convention)
        self.next: Optional["PQNode"] = None


class PriorityQueue:
    """
    Priority Queue implemented using an ordered Singly Linked List.
    Insertion: O(n) to maintain sorted order.
    Deletion (Dequeue): O(1) from head.
    """

    def __init__(self):
        self.head: Optional[PQNode] = None
        self._size = 0

    def enqueue(self, value: Any, priority: float) -> None:
        """Insert element maintaining sorted priority order: O(n)."""
        new_node = PQNode(value, priority)
        self._size += 1

        # Insert at head if list is empty or new node has strictly higher priority
        if self.head is None or priority < self.head.priority:
            new_node.next = self.head
            self.head = new_node
            return

        # Traverse to find proper insertion position
        curr = self.head
        while curr.next is not None and curr.next.priority <= priority:
            curr = curr.next

        new_node.next = curr.next
        curr.next = new_node

    def dequeue(self) -> Dict[str, Any]:
        """Remove highest priority element (lowest priority number): O(1)."""
        if self.head is None:
            raise IndexError("Priority Queue Underflow.")
        val = self.head.value
        pri = self.head.priority
        self.head = self.head.next
        self._size -= 1
        return {"val": val, "pri": pri}

    def peek(self) -> Optional[Dict[str, Any]]:
        if self.head is None:
            return None
        return {"val": self.head.value, "pri": self.head.priority}

    def is_empty(self) -> bool:
        return self.head is None

    def size(self) -> int:
        return self._size

    def to_list(self) -> List[Dict[str, Any]]:
        items = []
        curr = self.head
        while curr is not None:
            items.append({"val": curr.value, "pri": curr.priority})
            curr = curr.next
        return items


class Deque:
    """
    Double-Ended Queue (Deque) implemented manually using a dynamic circular list.
    Supports insert_front, insert_rear, delete_front, delete_rear in O(1).
    """

    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.arr: List[Optional[Any]] = [None] * capacity
        self.front = -1
        self.rear = 0
        self._size = 0

    def insert_front(self, item: Any) -> None:
        if self._size >= self.capacity:
            raise OverflowError("Deque Overflow.")

        if self.front == -1:
            self.front = 0
            self.rear = 0
        elif self.front == 0:
            self.front = self.capacity - 1
        else:
            self.front -= 1

        self.arr[self.front] = item
        self._size += 1

    def insert_rear(self, item: Any) -> None:
        if self._size >= self.capacity:
            raise OverflowError("Deque Overflow.")

        if self.front == -1:
            self.front = 0
            self.rear = 0
        elif self.rear == self.capacity - 1:
            self.rear = 0
        else:
            self.rear += 1

        self.arr[self.rear] = item
        self._size += 1

    def delete_front(self) -> Any:
        if self._size == 0:
            raise IndexError("Deque Underflow.")

        val = self.arr[self.front]
        self.arr[self.front] = None

        if self.front == self.rear:
            self.front = -1
            self.rear = -1
        elif self.front == self.capacity - 1:
            self.front = 0
        else:
            self.front += 1

        self._size -= 1
        return val

    def delete_rear(self) -> Any:
        if self._size == 0:
            raise IndexError("Deque Underflow.")

        val = self.arr[self.rear]
        self.arr[self.rear] = None

        if self.front == self.rear:
            self.front = -1
            self.rear = -1
        elif self.rear == 0:
            self.rear = self.capacity - 1
        else:
            self.rear -= 1

        self._size -= 1
        return val

    def to_list(self) -> List[Any]:
        if self._size == 0:
            return []
        items = []
        i = self.front
        for _ in range(self._size):
            items.append(self.arr[i])
            i = (i + 1) % self.capacity
        return items

