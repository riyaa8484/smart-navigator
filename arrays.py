"""
Arrays Module
Demonstrates fundamental array concepts:
- Static / Fixed-capacity array simulation with manual bounds checking
- Insertion at index, deletion from index, element rotation
- 2D Arrays and Matrix operations (transpose, addition)
- Sparse Matrix representation (Triplet / Coordinate COO format) and operations
"""

from typing import List, Tuple, Any, Optional, Dict


class StaticArray:
    """Simulates a fixed-capacity static array with manual boundary enforcement."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        self.capacity: int = capacity
        self.size: int = 0
        self.data: List[Optional[Any]] = [None] * capacity

    def insert(self, index: int, value: Any) -> None:
        """
        Insert value at specified index. Shifts elements right.
        Time Complexity: O(n)
        Space Complexity: O(1)
        """
        if self.size >= self.capacity:
            raise OverflowError("Array capacity reached. Cannot insert.")
        if index < 0 or index > self.size:
            raise IndexError("Index out of valid insertion range [0, size].")

        # Shift elements rightward from size-1 down to index
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i - 1]

        self.data[index] = value
        self.size += 1

    def delete(self, index: int) -> Any:
        """
        Delete value at specified index. Shifts elements left.
        Time Complexity: O(n)
        Space Complexity: O(1)
        """
        if self.size == 0:
            raise IndexError("Array is empty. Cannot delete.")
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds.")

        removed = self.data[index]
        # Shift elements leftward
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]

        self.data[self.size - 1] = None
        self.size -= 1
        return removed

    def get(self, index: int) -> Any:
        """Direct indexing: O(1)."""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds.")
        return self.data[index]

    def set(self, index: int, value: Any) -> None:
        """Direct update: O(1)."""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of bounds.")
        self.data[index] = value

    def to_list(self) -> List[Any]:
        """Convert populated elements to python list."""
        return [self.data[i] for i in range(self.size)]


class MatrixOperations:
    """Manual 2D Array / Matrix Operations."""

    @staticmethod
    def transpose(matrix: List[List[Any]]) -> List[List[Any]]:
        """
        Transpose an m x n matrix to an n x m matrix.
        Time Complexity: O(m * n)
        Space Complexity: O(m * n)
        """
        if not matrix or not matrix[0]:
            return []
        rows = len(matrix)
        cols = len(matrix[0])
        transposed: List[List[Any]] = [[matrix[r][c] for r in range(rows)] for c in range(cols)]
        return transposed

    @staticmethod
    def add(mat_a: List[List[float]], mat_b: List[List[float]]) -> List[List[float]]:
        """Matrix addition element-wise."""
        rows_a, cols_a = len(mat_a), len(mat_a[0])
        rows_b, cols_b = len(mat_b), len(mat_b[0])
        if rows_a != rows_b or cols_a != cols_b:
            raise ValueError("Matrices must have identical dimensions for addition.")

        result = [[0.0] * cols_a for _ in range(rows_a)]
        for r in range(rows_a):
            for c in range(cols_a):
                result[r][c] = mat_a[r][c] + mat_b[r][c]
        return result


class SparseMatrix:
    """
    Sparse Matrix representation using Triplet (Row, Col, Value) / Coordinate format (COO).
    Space efficient when matrix has mostly zero entries.
    """

    def __init__(self, rows: int, cols: int):
        self.rows: int = rows
        self.cols: int = cols
        self.triplets: List[Tuple[int, int, float]] = []  # (row, col, value)

    @classmethod
    def from_dense(cls, matrix: List[List[float]]) -> "SparseMatrix":
        """Convert dense 2D matrix to sparse triplet representation."""
        if not matrix:
            return cls(0, 0)
        rows = len(matrix)
        cols = len(matrix[0])
        sm = cls(rows, cols)
        for r in range(rows):
            for c in range(cols):
                val = matrix[r][c]
                if abs(val) > 1e-9:  # non-zero
                    sm.triplets.append((r, c, val))
        return sm

    def to_dense(self) -> List[List[float]]:
        """Reconstruct dense 2D matrix from sparse triplets."""
        dense = [[0.0] * self.cols for _ in range(self.rows)]
        for r, c, val in self.triplets:
            dense[r][c] = val
        return dense

    def transpose(self) -> "SparseMatrix":
        """
        Transpose sparse matrix by swapping row and col coordinates.
        Time Complexity: O(k log k) where k = number of non-zero entries.
        """
        transposed = SparseMatrix(self.cols, self.rows)
        for r, c, val in self.triplets:
            transposed.triplets.append((c, r, val))
        # Sort by row, then col
        transposed.triplets.sort(key=lambda t: (t[0], t[1]))
        return transposed

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API response."""
        return {
            "rows": self.rows,
            "cols": self.cols,
            "non_zero_count": len(self.triplets),
            "triplets": [{"row": r, "col": c, "value": v} for r, c, v in self.triplets],
            "sparsity_percentage": round(
                (1.0 - (len(self.triplets) / (self.rows * self.cols if self.rows * self.cols > 0 else 1))) * 100, 2
            )
        }

