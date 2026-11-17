"""
Stacks Module
Implements:
- Array-based Stack with push, pop, peek, is_empty, size
- Two Stacks in a Single Array (space-efficient dual stack)
- Infix-to-Postfix conversion (Shunting-Yard algorithm)
- Postfix Expression Evaluation
- Tower of Hanoi recursive solver demonstrating call-stack frames
"""

from typing import List, Any, Optional, Dict


class ArrayStack:
    """Manual Array-based LIFO Stack."""

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self._data: List[Any] = []

    def push(self, item: Any) -> None:
        """Push item onto stack: O(1)."""
        if len(self._data) >= self.capacity:
            raise OverflowError("Stack Overflow: Capacity limit reached.")
        self._data.append(item)

    def pop(self) -> Any:
        """Pop item from stack: O(1)."""
        if self.is_empty():
            raise IndexError("Stack Underflow: Cannot pop from an empty stack.")
        return self._data.pop()

    def peek(self) -> Optional[Any]:
        """Inspect top item without removing: O(1)."""
        if self.is_empty():
            return None
        return self._data[-1]

    def is_empty(self) -> bool:
        """Check if stack is empty: O(1)."""
        return len(self._data) == 0

    def size(self) -> int:
        """Return number of elements: O(1)."""
        return len(self._data)

    def to_list(self) -> List[Any]:
        """Return list representation (bottom to top)."""
        return list(self._data)


class TwoStacks:
    """
    Two Stacks in a single array:
    Stack 1 grows from left to right (index 0 upward).
    Stack 2 grows from right to left (index capacity-1 downward).
    Prevents overflow until both stacks meet.
    """

    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.arr: List[Optional[Any]] = [None] * capacity
        self.top1 = -1
        self.top2 = capacity

    def push1(self, item: Any) -> None:
        if self.top1 < self.top2 - 1:
            self.top1 += 1
            self.arr[self.top1] = item
        else:
            raise OverflowError("Stack 1 Overflow: No shared memory remaining.")

    def push2(self, item: Any) -> None:
        if self.top1 < self.top2 - 1:
            self.top2 -= 1
            self.arr[self.top2] = item
        else:
            raise OverflowError("Stack 2 Overflow: No shared memory remaining.")

    def pop1(self) -> Any:
        if self.top1 >= 0:
            val = self.arr[self.top1]
            self.arr[self.top1] = None
            self.top1 -= 1
            return val
        raise IndexError("Stack 1 Underflow.")

    def pop2(self) -> Any:
        if self.top2 < self.capacity:
            val = self.arr[self.top2]
            self.arr[self.top2] = None
            self.top2 += 1
            return val
        raise IndexError("Stack 2 Underflow.")

    def get_stack1(self) -> List[Any]:
        return [self.arr[i] for i in range(self.top1 + 1)]

    def get_stack2(self) -> List[Any]:
        return [self.arr[i] for i in range(self.capacity - 1, self.top2 - 1, -1)]


class ExpressionEvaluator:
    """Infix to Postfix converter and Postfix arithmetic evaluator."""

    PRECEDENCE = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '^': 3
    }

    @staticmethod
    def infix_to_postfix(expression: str) -> Dict[str, Any]:
        """
        Converts an infix mathematical expression to postfix notation.
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        stack = ArrayStack()
        output: List[str] = []
        tokens = ExpressionEvaluator._tokenize(expression)

        steps: List[Dict[str, str]] = []

        for token in tokens:
            if token.isalnum():  # Operands
                output.append(token)
            elif token == '(':
                stack.push(token)
            elif token == ')':
                while not stack.is_empty() and stack.peek() != '(':
                    output.append(stack.pop())
                if not stack.is_empty() and stack.peek() == '(':
                    stack.pop()  # Discard '('
                else:
                    raise ValueError("Mismatched parentheses in expression.")
            elif token in ExpressionEvaluator.PRECEDENCE:
                while (not stack.is_empty() and
                       stack.peek() != '(' and
                       ExpressionEvaluator.PRECEDENCE.get(stack.peek(), 0) >= ExpressionEvaluator.PRECEDENCE[token]):
                    output.append(stack.pop())
                stack.push(token)

            steps.append({
                "token": token,
                "stack": str(stack.to_list()),
                "output": "".join(output)
            })

        while not stack.is_empty():
            top = stack.pop()
            if top == '(':
                raise ValueError("Mismatched parentheses in expression.")
            output.append(top)

        postfix = "".join(output)
        return {
            "infix": expression,
            "postfix": postfix,
            "steps": steps,
            "time_complexity": "O(n)",
            "space_complexity": "O(n)"
        }

    @staticmethod
    def evaluate_postfix(postfix: str) -> Optional[float]:
        """Evaluates a postfix expression with numerical operands."""
        stack = ArrayStack()
        tokens = postfix.split() if " " in postfix else list(postfix)

        for token in tokens:
            if token.replace('.', '', 1).lstrip('-').isdigit():
                stack.push(float(token))
            elif token in ('+', '-', '*', '/', '^'):
                if stack.size() < 2:
                    return None
                val2 = stack.pop()
                val1 = stack.pop()
                if token == '+':
                    res = val1 + val2
                elif token == '-':
                    res = val1 - val2
                elif token == '*':
                    res = val1 * val2
                elif token == '/':
                    if abs(val2) < 1e-9:
                        raise ZeroDivisionError("Division by zero in postfix evaluation.")
                    res = val1 / val2
                elif token == '^':
                    res = val1 ** val2
                else:
                    return None
                stack.push(res)

        return stack.pop() if stack.size() == 1 else None

    @staticmethod
    def _tokenize(expr: str) -> List[str]:
        """Tokenize expression ignoring whitespaces."""
        clean = expr.replace(" ", "")
        tokens: List[str] = []
        i = 0
        while i < len(clean):
            char = clean[i]
            if char.isalnum():
                buf = [char]
                while i + 1 < len(clean) and clean[i + 1].isalnum():
                    i += 1
                    buf.append(clean[i])
                tokens.append("".join(buf))
            else:
                tokens.append(char)
            i += 1
        return tokens


class TowerOfHanoi:
    """Solves Tower of Hanoi problem using recursion (simulating stack frames)."""

    @staticmethod
    def solve(num_disks: int, source: str = "A", auxiliary: str = "B", destination: str = "C") -> Dict[str, Any]:
        """
        Calculates moves to transfer n disks from source to destination.
        Total moves: 2^n - 1.
        Time Complexity: O(2^n)
        Space Complexity: O(n) (recursion depth)
        """
        moves: List[Dict[str, Any]] = []

        def _hanoi(n: int, src: str, aux: str, dst: str):
            if n == 1:
                moves.append({"disk": 1, "from": src, "to": dst})
                return
            _hanoi(n - 1, src, dst, aux)
            moves.append({"disk": n, "from": src, "to": dst})
            _hanoi(n - 1, aux, src, dst)

        _hanoi(num_disks, source, auxiliary, destination)

        return {
            "disks": num_disks,
            "total_moves": len(moves),
            "theoretical_min_moves": (2 ** num_disks) - 1,
            "moves": moves,
            "time_complexity": "O(2^n)",
            "space_complexity": "O(n)"
        }

