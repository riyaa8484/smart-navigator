"""
DSA Lab Module API Blueprint
Exposes independent interactive endpoints demonstrating all curriculum DSA topics:
- Arrays & Sparse Matrix
- Stacks (Infix to Postfix, Postfix Evaluation, Tower of Hanoi)
- Queues (Linear, Circular, Priority Queue, Deque)
- Linked Lists (Singly, Doubly, Circular, Reversal, Deduplication)
- Trees (BST construct, traversals, height, AVL rotations)
- Hashing (Chaining, Linear Probing, collision stats)
- Heaps (Min/Max Heap, Heapify, Heap Sort)
- Searching (Linear, Binary, BST Search with step traces)
- Sorting (All 6 algorithms with metrics)
- Complexity Analysis Database
"""

from flask import Blueprint, jsonify, request
from arrays import StaticArray, MatrixOperations, SparseMatrix
from stacks import ArrayStack, TwoStacks, ExpressionEvaluator, TowerOfHanoi
from queues import LinearQueue, CircularQueue, PriorityQueue, Deque
from linked_lists import SinglyLinkedList, DoublyLinkedList, CircularLinkedList, LinkedListAlgorithms
from trees import BinarySearchTree, AVLTreeDemo, TreeNode
from hashing import HashTableChaining, HashTableLinearProbing
from heaps import MinHeap, MaxHeap
from searching import SearchingAlgorithms
from sorting import SortingAlgorithms
from complexity import get_complexity, get_all_complexities

dsa_bp = Blueprint("dsa_bp", __name__)


def _get_payload():
    """Helper to get JSON body or fall back to query args."""
    return request.get_json(force=True, silent=True) or request.args.to_dict() or {}


# -------------------------------------------------------------
# 1. Stacks Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/stack", methods=["POST", "GET"])
def demo_stack():
    """
    Demonstrate stack operations: Infix-to-Postfix conversion, evaluation, or Tower of Hanoi.
    Example: { "expr": "(a+b)*c" } -> { "postfix": "ab+c*", "time_complexity": "O(n)" }
    """
    payload = _get_payload()
    expr = payload.get("expr")
    op = payload.get("op", "infix_to_postfix")
    disks = payload.get("disks")

    if op == "hanoi" or disks is not None:
        num_disks = int(disks or 3)
        return jsonify(TowerOfHanoi.solve(num_disks))

    if not expr:
        expr = "(a+b)*c"

    try:
        conversion = ExpressionEvaluator.infix_to_postfix(expr)
        # Check if expression contains only digits and operators to compute evaluation
        eval_result = None
        try:
            eval_result = ExpressionEvaluator.evaluate_postfix(conversion["postfix"])
        except Exception:
            pass
        conversion["result"] = eval_result
        return jsonify(conversion)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------------------------------------------------
# 2. Linear Queue Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/queue", methods=["POST", "GET"])
def demo_queue():
    """
    Linear Queue FIFO demonstration.
    Input: { "items": [1, 2, 3] }
    """
    payload = _get_payload()
    items = payload.get("items", [10, 20, 30])
    if isinstance(items, str):
        items = [x.strip() for x in items.split(",")]

    q = LinearQueue(capacity=max(10, len(items) + 5))
    for item in items:
        q.enqueue(item)

    processed = []
    while not q.is_empty():
        processed.append(q.dequeue())

    return jsonify({
        "enqueued": items,
        "processed": processed,
        "algorithm": "Linear Queue (FIFO)",
        "time_complexity": "Enqueue: O(1), Dequeue: O(1)",
        "space_complexity": "O(n)"
    })


# -------------------------------------------------------------
# 3. Circular Queue Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/circular-queue", methods=["POST", "GET"])
def demo_circular_queue():
    """
    Circular Queue demonstration.
    Input: { "capacity": 5, "items": [1, 2, 3, 4] }
    """
    payload = _get_payload()
    capacity = int(payload.get("capacity", 5))
    items = payload.get("items", [1, 2, 3, 4])
    if isinstance(items, str):
        items = [x.strip() for x in items.split(",")]

    cq = CircularQueue(capacity=capacity)
    enqueued = []
    errors = []

    for item in items:
        try:
            cq.enqueue(item)
            enqueued.append(item)
        except OverflowError as oe:
            errors.append(str(oe))

    state = cq.state_dict()
    state["queue"] = cq.to_list()
    state["status"] = "OK" if not errors else "PARTIAL_OVERFLOW"
    state["warnings"] = errors
    state["time_complexity"] = "O(1) Enqueue and Dequeue"
    state["space_complexity"] = f"O({capacity}) Fixed Circular Buffer"
    return jsonify(state)


# -------------------------------------------------------------
# 4. Priority Queue Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/priority-queue", methods=["POST", "GET"])
def demo_priority_queue():
    """
    Priority Queue (Linked-List based).
    Input: { "items": [ {"val": 5, "pri": 1}, {"val": 2, "pri": 0} ] }
    """
    payload = _get_payload()
    items = payload.get("items", [
        {"val": "Low Priority Task", "pri": 3},
        {"val": "Critical Medical Alarm", "pri": 0},
        {"val": "Standard Route Query", "pri": 2},
        {"val": "High Priority SOS", "pri": 1}
    ])

    pq = PriorityQueue()
    for item in items:
        pq.enqueue(item.get("val"), float(item.get("pri", 0)))

    dequeued = []
    while not pq.is_empty():
        dequeued.append(pq.dequeue())

    return jsonify({
        "input": items,
        "dequeued": dequeued,
        "algorithm": "Priority Queue (Min-Priority Order)",
        "time_complexity": "Enqueue: O(n), Dequeue: O(1)",
        "space_complexity": "O(n)"
    })


# -------------------------------------------------------------
# 5. Deque Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/deque", methods=["POST", "GET"])
def demo_deque():
    """
    Double-Ended Queue (Deque) demo.
    Input: { "operations": [ {"op": "insert_rear", "val": 10}, {"op": "insert_front", "val": 5} ] }
    """
    payload = _get_payload()
    items = payload.get("items", [1, 2, 3])
    dq = Deque(capacity=20)

    for item in items:
        dq.insert_rear(item)

    # Demo front and rear manipulations
    dq.insert_front(99)
    front_val = dq.delete_front()

    return jsonify({
        "result": dq.to_list(),
        "operations": [
            "insert_rear on initial items",
            "insert_front(99)",
            f"delete_front() -> returned {front_val}"
        ],
        "time_complexity": "O(1) for all four end operations",
        "space_complexity": "O(capacity)"
    })


# -------------------------------------------------------------
# 6. Linked Lists Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/linked-list", methods=["POST", "GET"])
def demo_linked_list():
    """
    Linked List operations: reverse, removeDup, traversal.
    Input: { "list": [1, 2, 3, 2, 4, 1], "op": "reverse" | "removeDup" }
    """
    payload = _get_payload()
    items = payload.get("list", [1, 2, 3, 2, 4, 1])
    if isinstance(items, str):
        items = [x.strip() for x in items.split(",")]

    op = payload.get("op", "reverse").lower()
    sll = SinglyLinkedList.from_list(items)

    initial_list = sll.to_list()
    if op == "reverse":
        sll.reverse()
        return jsonify({
            "initial": initial_list,
            "reversed": sll.to_list(),
            "operation": "In-place Reversal (3-pointer)",
            "time_complexity": "O(n)",
            "space_complexity": "O(1)"
        })
    elif op in ("removedup", "remove_duplicates", "dedup"):
        sll.remove_duplicates()
        return jsonify({
            "initial": initial_list,
            "deduplicated": sll.to_list(),
            "operation": "Remove Duplicates",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)"
        })
    else:
        return jsonify({
            "list": initial_list,
            "size": len(initial_list),
            "operations_supported": ["reverse", "removeDup"]
        })


# -------------------------------------------------------------
# 7. Trees Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/trees", methods=["POST", "GET"])
def demo_trees():
    """
    Tree traversals, BST construction, and AVL basics.
    Input: { "values": [50, 30, 70, 20, 40, 60, 80], "op": "inorder" | "construct" }
    """
    payload = _get_payload()
    raw_vals = payload.get("values", [50, 30, 70, 20, 40, 60, 80])
    if isinstance(raw_vals, str):
        raw_vals = [int(x.strip()) for x in raw_vals.split(",") if x.strip().isdigit()]

    bst = BinarySearchTree()
    for v in raw_vals:
        bst.insert(v)

    return jsonify({
        "values": raw_vals,
        "inorder": bst.inorder(),
        "preorder": bst.preorder(),
        "postorder": bst.postorder(),
        "level_order": bst.level_order(),
        "tree_height": bst.height(),
        "is_valid_bst": bst.is_valid_bst(),
        "avl_info": "Rotations implemented: Left-Rotate (RR), Right-Rotate (LL)",
        "time_complexity": "Traversals: O(n), Search/Insert: O(h)",
        "space_complexity": "O(h) recursion stack"
    })


# -------------------------------------------------------------
# 8. Hashing Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/hashing", methods=["POST", "GET"])
def demo_hashing():
    """
    Demonstrate Separate Chaining and Linear Probing Hash Tables.
    Input: { "keys": ["apple", "banana", "orange", "grape"], "op": "insert" }
    """
    payload = _get_payload()
    keys = payload.get("keys", ["Library", "Canteen", "Hostel", "Gate", "Admin", "Auditorium"])
    if isinstance(keys, str):
        keys = [k.strip() for k in keys.split(",")]

    ht_chain = HashTableChaining(capacity=7)
    ht_probe = HashTableLinearProbing(capacity=11)

    for i, k in enumerate(keys):
        ht_chain.insert(k, f"Loc_{i+1}")
        ht_probe.insert(k, f"Loc_{i+1}")

    return jsonify({
        "inserted_keys": keys,
        "separate_chaining": ht_chain.to_dict(),
        "linear_probing_table": ht_probe.to_list(),
        "time_complexity": "Average O(1), Worst O(n)",
        "space_complexity": "O(n)"
    })


# -------------------------------------------------------------
# 9. Heaps Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/heaps", methods=["POST", "GET"])
def demo_heaps():
    """
    Min Heap and Max Heap operations.
    Input: { "values": [12, 3, 17, 8, 25, 1], "op": "heapify" }
    """
    payload = _get_payload()
    raw_vals = payload.get("values", [12, 3, 17, 8, 25, 1, 9])
    if isinstance(raw_vals, str):
        raw_vals = [int(x.strip()) for x in raw_vals.split(",") if x.strip().lstrip('-').isdigit()]

    min_h = MinHeap()
    min_h.build_heap(raw_vals)

    max_h = MaxHeap()
    max_h.build_heap(raw_vals)

    return jsonify({
        "original_array": raw_vals,
        "min_heap_array": min_h.to_list(),
        "min_heap_root": min_h.peek(),
        "max_heap_array": max_h.to_list(),
        "max_heap_root": max_h.peek(),
        "time_complexity": "Build Heap: O(n), Insert/Extract: O(log n)",
        "space_complexity": "O(1) auxiliary"
    })


# -------------------------------------------------------------
# 10. Searching Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/search", methods=["POST", "GET"])
def demo_search():
    """
    Search algorithms: linear, binary, bst.
    Input: { "list": [10, 20, 30, 40, 50], "target": 30, "method": "binary" }
    """
    payload = _get_payload()
    arr = payload.get("list", [10, 20, 30, 40, 50, 60, 70])
    target = payload.get("target", 30)
    method = payload.get("method", "binary").lower()

    try:
        target = float(target) if str(target).replace('.', '', 1).lstrip('-').isdigit() else target
        arr = [float(x) if str(x).replace('.', '', 1).lstrip('-').isdigit() else x for x in arr]
    except Exception:
        pass

    if method == "linear":
        return jsonify(SearchingAlgorithms.linear_search(arr, target))
    elif method == "bst":
        return jsonify(SearchingAlgorithms.bst_search(arr, target))
    else:
        return jsonify(SearchingAlgorithms.binary_search(arr, target))


# -------------------------------------------------------------
# 11. Sorting Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/sort", methods=["POST", "GET"])
def demo_sort():
    """
    Sorting algorithms: bubble, selection, insertion, merge, quick, heap.
    Input: { "list": [64, 25, 12, 22, 11], "algorithm": "quick" }
    """
    payload = _get_payload()
    arr = payload.get("list", [64, 25, 12, 22, 11])
    algo = payload.get("algorithm", "quick").lower()

    if isinstance(arr, str):
        arr = [float(x.strip()) for x in arr.split(",") if x.strip().replace('.', '', 1).lstrip('-').isdigit()]

    if algo == "bubble":
        res = SortingAlgorithms.bubble_sort(arr)
    elif algo == "selection":
        res = SortingAlgorithms.selection_sort(arr)
    elif algo == "insertion":
        res = SortingAlgorithms.insertion_sort(arr)
    elif algo == "merge":
        res = SortingAlgorithms.merge_sort(arr)
    elif algo == "heap":
        res = SortingAlgorithms.heap_sort(arr)
    else:
        res = SortingAlgorithms.quick_sort(arr)

    return jsonify(res)


# -------------------------------------------------------------
# 12. Arrays & Sparse Matrix Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/arrays", methods=["POST", "GET"])
def demo_arrays():
    """
    Demonstrate Static Array insert/delete and Sparse Matrix representation.
    """
    payload = _get_payload()
    op = payload.get("op", "sparse")

    if op == "sparse":
        sample_matrix = payload.get("matrix", [
            [0, 0, 3.5, 0],
            [1.2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 4.8, 0, 0.9]
        ])
        sm = SparseMatrix.from_dense(sample_matrix)
        sm_transposed = sm.transpose()

        return jsonify({
            "dense_input": sample_matrix,
            "sparse_representation": sm.to_dict(),
            "transposed_sparse": sm_transposed.to_dict(),
            "time_complexity": "O(non_zero_elements)",
            "space_complexity": "O(non_zero_elements)"
        })
    else:
        arr = StaticArray(capacity=10)
        for i, val in enumerate([10, 20, 30, 40]):
            arr.insert(i, val)
        deleted = arr.delete(1)
        return jsonify({
            "operation": "Insert 4 elements and delete at index 1",
            "deleted_value": deleted,
            "resulting_array": arr.to_list(),
            "time_complexity": "Insert/Delete: O(n), Indexing: O(1)"
        })


# -------------------------------------------------------------
# 13. Complexity Analysis Endpoint
# -------------------------------------------------------------
@dsa_bp.route("/api/dsa/complexity", methods=["GET", "POST"])
def get_complexity_info():
    """
    Return time & space complexity for requested algorithm.
    Query or JSON: { "algorithm": "bfs" | "bubble" | "dijkstra" | ... }
    """
    payload = _get_payload()
    algo = payload.get("algorithm") or request.args.get("algorithm")

    if algo:
        data = get_complexity(algo)
        if data:
            return jsonify(data)
        return jsonify({"error": f"Algorithm '{algo}' not found in database.", "available": list(get_all_complexities().keys())}), 404

    return jsonify(get_all_complexities())

