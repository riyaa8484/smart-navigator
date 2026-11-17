"""
Hashing Module
Implements:
- Custom Polynomial Rolling Hash Function
- Hash Table with Separate Chaining (Buckets of Singly Linked List entries)
- Hash Table with Open Addressing (Linear Probing with Tombstone Deletion)
- Dynamic rehashing and load factor calculation
"""

from typing import List, Tuple, Any, Optional, Dict


class HashNode:
    """Linked list node for Chaining collision resolution."""
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.next: Optional["HashNode"] = None


class HashTableChaining:
    """
    Hash Table with Separate Chaining.
    Time Complexity:
    - Average: O(1) for insert, search, delete
    - Worst (all collisions): O(n)
    """

    def __init__(self, capacity: int = 11):
        self.capacity: int = capacity
        self.buckets: List[Optional[HashNode]] = [None] * capacity
        self.size: int = 0

    def _hash(self, key: Any) -> int:
        """Custom polynomial rolling hash function."""
        s = str(key)
        hash_val = 0
        p = 31
        m = self.capacity
        for char in s:
            hash_val = (hash_val * p + ord(char)) % m
        return hash_val

    def insert(self, key: Any, value: Any) -> None:
        """Insert or update key-value pair."""
        if (self.size + 1) / self.capacity > 0.75:
            self._rehash(self.capacity * 2 + 1)

        idx = self._hash(key)
        head = self.buckets[idx]

        # Check if key already exists to update
        curr = head
        while curr is not None:
            if curr.key == key:
                curr.value = value
                return
            curr = curr.next

        # Insert new node at head of bucket
        new_node = HashNode(key, value)
        new_node.next = self.buckets[idx]
        self.buckets[idx] = new_node
        self.size += 1

    def search(self, key: Any) -> Optional[Any]:
        """Search value by key."""
        idx = self._hash(key)
        curr = self.buckets[idx]
        while curr is not None:
            if curr.key == key:
                return curr.value
            curr = curr.next
        return None

    def delete(self, key: Any) -> bool:
        """Remove key from hash table."""
        idx = self._hash(key)
        curr = self.buckets[idx]
        prev = None

        while curr is not None:
            if curr.key == key:
                if prev is None:
                    self.buckets[idx] = curr.next
                else:
                    prev.next = curr.next
                self.size -= 1
                return True
            prev = curr
            curr = curr.next
        return False

    def load_factor(self) -> float:
        return round(self.size / self.capacity, 3)

    def _rehash(self, new_capacity: int) -> None:
        old_buckets = self.buckets
        self.capacity = new_capacity
        self.buckets = [None] * new_capacity
        self.size = 0

        for head in old_buckets:
            curr = head
            while curr is not None:
                self.insert(curr.key, curr.value)
                curr = curr.next

    def to_dict(self) -> Dict[str, Any]:
        bucket_dump = {}
        for i, head in enumerate(self.buckets):
            chain = []
            curr = head
            while curr is not None:
                chain.append({"key": str(curr.key), "value": curr.value})
                curr = curr.next
            if chain:
                bucket_dump[f"bucket_{i}"] = chain
        return {
            "capacity": self.capacity,
            "size": self.size,
            "load_factor": self.load_factor(),
            "buckets": bucket_dump
        }


class HashTableLinearProbing:
    """
    Open Addressing Hash Table with Linear Probing and Tombstone deletion.
    Formula: h(k, i) = (h(k) + i) % capacity
    """

    TOMBSTONE = object()

    def __init__(self, capacity: int = 11):
        self.capacity = capacity
        self.table: List[Optional[Tuple[Any, Any]]] = [None] * capacity
        self.size = 0

    def _hash(self, key: Any) -> int:
        s = str(key)
        h = 0
        for char in s:
            h = (h * 37 + ord(char)) % self.capacity
        return h

    def insert(self, key: Any, value: Any) -> bool:
        if (self.size + 1) / self.capacity > 0.70:
            self._rehash(self.capacity * 2 + 1)

        idx = self._hash(key)
        first_tombstone = -1

        for i in range(self.capacity):
            probe_idx = (idx + i) % self.capacity
            entry = self.table[probe_idx]

            if entry is None:
                target_idx = first_tombstone if first_tombstone != -1 else probe_idx
                self.table[target_idx] = (key, value)
                self.size += 1
                return True
            elif entry is self.TOMBSTONE:
                if first_tombstone == -1:
                    first_tombstone = probe_idx
            elif entry[0] == key:
                self.table[probe_idx] = (key, value)
                return True

        return False

    def search(self, key: Any) -> Optional[Any]:
        idx = self._hash(key)
        for i in range(self.capacity):
            probe_idx = (idx + i) % self.capacity
            entry = self.table[probe_idx]
            if entry is None:
                return None
            if entry is not self.TOMBSTONE and entry[0] == key:
                return entry[1]
        return None

    def delete(self, key: Any) -> bool:
        idx = self._hash(key)
        for i in range(self.capacity):
            probe_idx = (idx + i) % self.capacity
            entry = self.table[probe_idx]
            if entry is None:
                return False
            if entry is not self.TOMBSTONE and entry[0] == key:
                self.table[probe_idx] = self.TOMBSTONE
                self.size -= 1
                return True
        return False

    def _rehash(self, new_capacity: int) -> None:
        old_table = self.table
        self.capacity = new_capacity
        self.table = [None] * new_capacity
        self.size = 0
        for entry in old_table:
            if entry is not None and entry is not self.TOMBSTONE:
                self.insert(entry[0], entry[1])

    def to_list(self) -> List[Any]:
        return [
            "<TOMBSTONE>" if e is self.TOMBSTONE else (list(e) if e else None)
            for e in self.table
        ]

