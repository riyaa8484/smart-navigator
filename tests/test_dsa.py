"""
Unit Tests for Manual Data Structures and Algorithms Modules.
Tests every custom DSA implementation to ensure correct behavior and edge cases.
"""

import unittest
from arrays import StaticArray, MatrixOperations, SparseMatrix
from stacks import ArrayStack, TwoStacks, ExpressionEvaluator, TowerOfHanoi
from queues import LinearQueue, CircularQueue, PriorityQueue, Deque
from linked_lists import SinglyLinkedList, DoublyLinkedList, CircularLinkedList, LinkedListAlgorithms
from trees import BinarySearchTree
from hashing import HashTableChaining, HashTableLinearProbing
from heaps import MinHeap, MaxHeap
from searching import SearchingAlgorithms
from sorting import SortingAlgorithms
from graph import CampusGraph


class TestArrays(unittest.TestCase):
    def test_static_array_insert_delete(self):
        arr = StaticArray(5)
        arr.insert(0, 10)
        arr.insert(1, 20)
        arr.insert(1, 15)  # [10, 15, 20]
        self.assertEqual(arr.to_list(), [10, 15, 20])
        val = arr.delete(1)
        self.assertEqual(val, 15)
        self.assertEqual(arr.to_list(), [10, 20])

    def test_sparse_matrix(self):
        dense = [
            [0, 5.0, 0],
            [0, 0, 0],
            [7.0, 0, 0]
        ]
        sm = SparseMatrix.from_dense(dense)
        self.assertEqual(len(sm.triplets), 2)
        reconstructed = sm.to_dense()
        self.assertEqual(reconstructed, dense)
        transposed = sm.transpose().to_dense()
        self.assertEqual(transposed[1][0], 5.0)
        self.assertEqual(transposed[0][2], 7.0)


class TestStacks(unittest.TestCase):
    def test_array_stack(self):
        s = ArrayStack(10)
        self.assertTrue(s.is_empty())
        s.push("A")
        s.push("B")
        self.assertEqual(s.peek(), "B")
        self.assertEqual(s.pop(), "B")
        self.assertEqual(s.pop(), "A")
        self.assertTrue(s.is_empty())

    def test_two_stacks(self):
        ts = TwoStacks(6)
        ts.push1(1)
        ts.push1(2)
        ts.push2(9)
        ts.push2(8)
        self.assertEqual(ts.pop1(), 2)
        self.assertEqual(ts.pop2(), 8)

    def test_infix_to_postfix(self):
        res = ExpressionEvaluator.infix_to_postfix("(A+B)*C")
        self.assertEqual(res["postfix"], "AB+C*")

        eval_res = ExpressionEvaluator.evaluate_postfix("34+2*")
        self.assertEqual(eval_res, 14.0)

    def test_tower_of_hanoi(self):
        hanoi = TowerOfHanoi.solve(3)
        self.assertEqual(hanoi["total_moves"], 7)
        self.assertEqual(hanoi["theoretical_min_moves"], 7)


class TestQueues(unittest.TestCase):
    def test_linear_queue(self):
        lq = LinearQueue(5)
        lq.enqueue(10)
        lq.enqueue(20)
        self.assertEqual(lq.dequeue(), 10)
        self.assertEqual(lq.dequeue(), 20)
        self.assertTrue(lq.is_empty())

    def test_circular_queue(self):
        cq = CircularQueue(3)
        cq.enqueue("A")
        cq.enqueue("B")
        self.assertEqual(cq.dequeue(), "A")
        cq.enqueue("C")
        cq.enqueue("D")
        self.assertTrue(cq.is_full())
        self.assertEqual(cq.dequeue(), "B")
        self.assertEqual(cq.dequeue(), "C")
        self.assertEqual(cq.dequeue(), "D")
        self.assertTrue(cq.is_empty())

    def test_priority_queue(self):
        pq = PriorityQueue()
        pq.enqueue("Med", 2)
        pq.enqueue("High", 1)
        pq.enqueue("Low", 3)
        pq.enqueue("Urgent", 0)
        self.assertEqual(pq.dequeue()["val"], "Urgent")
        self.assertEqual(pq.dequeue()["val"], "High")
        self.assertEqual(pq.dequeue()["val"], "Med")
        self.assertEqual(pq.dequeue()["val"], "Low")

    def test_deque(self):
        dq = Deque(10)
        dq.insert_rear(2)
        dq.insert_front(1)
        dq.insert_rear(3)
        self.assertEqual(dq.to_list(), [1, 2, 3])
        self.assertEqual(dq.delete_front(), 1)
        self.assertEqual(dq.delete_rear(), 3)
        self.assertEqual(dq.to_list(), [2])


class TestLinkedLists(unittest.TestCase):
    def test_singly_linked_list(self):
        sll = SinglyLinkedList.from_list([1, 2, 3, 4])
        sll.reverse()
        self.assertEqual(sll.to_list(), [4, 3, 2, 1])

        dup_list = SinglyLinkedList.from_list([1, 2, 2, 3, 1])
        dup_list.remove_duplicates()
        self.assertEqual(dup_list.to_list(), [1, 2, 3])

    def test_doubly_linked_list(self):
        dll = DoublyLinkedList()
        dll.append(10)
        dll.append(20)
        dll.prepend(5)
        self.assertEqual(dll.to_list_forward(), [5, 10, 20])
        self.assertEqual(dll.to_list_backward(), [20, 10, 5])


class TestTrees(unittest.TestCase):
    def test_bst_traversals(self):
        bst = BinarySearchTree()
        for v in [50, 30, 70, 20, 40, 60, 80]:
            bst.insert(v)

        self.assertEqual(bst.inorder(), [20, 30, 40, 50, 60, 70, 80])
        self.assertEqual(bst.preorder(), [50, 30, 20, 40, 70, 60, 80])
        self.assertEqual(bst.level_order(), [50, 30, 70, 20, 40, 60, 80])
        self.assertTrue(bst.is_valid_bst())
        self.assertEqual(bst.height(), 3)

        # Search & Delete
        self.assertIsNotNone(bst.search(40))
        bst.delete(30)
        self.assertEqual(bst.inorder(), [20, 40, 50, 60, 70, 80])


class TestHashing(unittest.TestCase):
    def test_chaining(self):
        ht = HashTableChaining(5)
        ht.insert("apple", 100)
        ht.insert("banana", 200)
        self.assertEqual(ht.search("apple"), 100)
        self.assertEqual(ht.search("banana"), 200)
        self.assertTrue(ht.delete("apple"))
        self.assertIsNone(ht.search("apple"))

    def test_linear_probing(self):
        ht = HashTableLinearProbing(7)
        ht.insert("cat", 1)
        ht.insert("dog", 2)
        self.assertEqual(ht.search("cat"), 1)
        self.assertEqual(ht.search("dog"), 2)
        self.assertTrue(ht.delete("cat"))
        self.assertIsNone(ht.search("cat"))


class TestHeaps(unittest.TestCase):
    def test_min_heap(self):
        mh = MinHeap()
        mh.build_heap([20, 15, 2, 8, 1])
        self.assertEqual(mh.peek(), 1)
        sorted_vals = []
        while mh.size() > 0:
            sorted_vals.append(mh.extract_min())
        self.assertEqual(sorted_vals, [1, 2, 8, 15, 20])

    def test_max_heap(self):
        max_h = MaxHeap()
        max_h.build_heap([20, 15, 2, 8, 1])
        self.assertEqual(max_h.peek(), 20)
        sorted_desc = []
        while max_h.size() > 0:
            sorted_desc.append(max_h.extract_max())
        self.assertEqual(sorted_desc, [20, 15, 8, 2, 1])


class TestSearchingSorting(unittest.TestCase):
    def test_searching(self):
        arr = [10, 20, 30, 40, 50]
        self.assertTrue(SearchingAlgorithms.linear_search(arr, 30)["found"])
        self.assertTrue(SearchingAlgorithms.binary_search(arr, 40)["found"])
        self.assertFalse(SearchingAlgorithms.binary_search(arr, 99)["found"])

    def test_all_sorting(self):
        data = [64, 34, 25, 12, 22, 11, 90]
        expected = [11, 12, 22, 25, 34, 64, 90]

        self.assertEqual(SortingAlgorithms.bubble_sort(data)["sorted"], expected)
        self.assertEqual(SortingAlgorithms.selection_sort(data)["sorted"], expected)
        self.assertEqual(SortingAlgorithms.insertion_sort(data)["sorted"], expected)
        self.assertEqual(SortingAlgorithms.merge_sort(data)["sorted"], expected)
        self.assertEqual(SortingAlgorithms.quick_sort(data)["sorted"], expected)
        self.assertEqual(SortingAlgorithms.heap_sort(data)["sorted"], expected)


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = CampusGraph()
        self.graph.add_edge("A", "B", 1.0)
        self.graph.add_edge("B", "C", 2.0)
        self.graph.add_edge("A", "C", 4.0)
        self.graph.add_edge("C", "D", 1.0)

    def test_bfs_dfs(self):
        bfs_res = self.graph.bfs_shortest_path("A", "D")
        self.assertTrue(bfs_res["found"])
        self.assertEqual(bfs_res["path"], ["A", "C", "D"])  # 2 hops vs 3 hops

        dfs_res = self.graph.dfs_path("A", "D")
        self.assertTrue(dfs_res["found"])

    def test_dijkstra(self):
        dijk_res = self.graph.dijkstra_shortest_path("A", "D")
        self.assertTrue(dijk_res["found"])
        self.assertEqual(dijk_res["path"], ["A", "B", "C", "D"])  # weight 1+2+1 = 4.0 vs 4+1 = 5.0
        self.assertEqual(dijk_res["distance"], 4.0)

    def test_mst(self):
        prim = self.graph.prim_mst()
        kruskal = self.graph.kruskal_mst()
        self.assertEqual(prim["total_weight"], 4.0)
        self.assertEqual(kruskal["total_weight"], 4.0)


if __name__ == "__main__":
    unittest.main()

