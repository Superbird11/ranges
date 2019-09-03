from collections import Iterable
from numbers import Number


def _is_iterable_non_string(arg):
    """
    A helper method to return True if the given argument appears to be iterable
    (like a list) but not able to be converted to a Range.

    In particular, checks for whether python would consider the argument to be
    iterable (it has either __iter__() or __getattr__() defined), and then
    checks that it isn't a string (in which case we don't want to iterate through
    it, we want to pass it in to Range() wholesale).
    """
    return (hasattr(arg, "__iter__") or hasattr(arg, "__getattr__")) and not isinstance(arg, str)


class _InfiniteValue(Number):
    """
    A class representing positive or negative infinity, mainly as a stand-in for float's version
    of infinity, able to represent an infinite value for other types.
    """
    def __init__(self, negative=False):
        self.negative = negative
        self.floatvalue = float('-inf' if self.negative else 'inf')

    def __lt__(self, other):
        """ -infinity is always less """
        if isinstance(other, float):
            return self.floatvalue < other
        else:
            return self.negative and not self == other

    def __gt__(self, other):
        """ +infinity is always more """
        if isinstance(other, float):
            return self.floatvalue > other
        else:
            return not self.negative and not self == other

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        """ for consistency, infinity is equal to itself """
        if isinstance(other, float):
            return self.floatvalue == other
        elif isinstance(other, _InfiniteValue):
            return self.negative == other.negative
        else:
            return False

    def __add__(self, other):
        return self.floatvalue + other

    def __radd__(self, other):
        return other + self.floatvalue

    def __sub__(self, other):
        return self.floatvalue - other

    def __rsub__(self, other):
        return other - self.floatvalue

    def __mul__(self, other):
        return self.floatvalue * other

    def __rmul__(self, other):
        return other * self.floatvalue

    def __truediv__(self, other):
        return self.floatvalue / other

    def __rtruediv__(self, other):
        return other / self.floatvalue

    def __floordiv__(self, other):
        return self.floatvalue // other

    def __rfloordiv__(self, other):
        return other // self.floatvalue

    def __mod__(self, other):
        return self.floatvalue % other

    def __rmod__(self, other):
        return other % self.floatvalue

    def __divmod__(self, other):
        return divmod(self.floatvalue, other)

    def __rdivmod__(self, other):
        return divmod(other, self.floatvalue)

    def __neg__(self):
        return _InfiniteValue(negative=not self.negative)

    def __int__(self):
        return int(self.floatvalue)

    def __float__(self):
        return self.floatvalue

    def __str__(self):
        return str(self.floatvalue)

    def __repr__(self):
        """ pretend to be float infinity """
        return repr(self.floatvalue)

    def __hash__(self):
        """ pretend to be float infinity """
        return hash(self.floatvalue)


class _LinkedList(Iterable):
    """
    A custom definition of a single, feature-poor, linked-list.
    """
    class Node:
        def __init__(self, value, prev=None, next=None, parent=None):
            self.value = value
            self.prev = prev
            self.next = next
            self.parent = parent

        def __eq__(self, other):
            return self.value.__eq__(other.value)

        def __lt__(self, other):
            return self.value.__lt__(other.value)

        def __gt__(self, other):
            return self.value.__gt__(other.value)

        def __ge__(self, other):
            return self.value.__ge__(other.value)

        def __le__(self, other):
            return self.value.__le__(other.value)

        def __str__(self):
            return f"Node({str(self.value)})"

        def __repr__(self):
            return str(self)

    def __init__(self, iterable=None):
        """
        Constructs a new Linked List based on the given iterable
        """
        if iterable is None:
            iterable = []
        self._length = 0
        if len(iterable) == 0:
            self.first = None
            self.last = None
        else:
            # iterate through iterable
            it = iter(iterable)
            # first element of iterable becomes self.first
            self.first = self.Node(next(it), parent=self)
            self.last = self.first
            self._length += 1
            # populate rest of list as long as iterable remains
            for elem in it:
                self.last.next = self.Node(elem, prev=self.last, parent=self)
                self.last = self.last.next
                self._length += 1
        # that should be all

    def node_at(self, index):
        if index < 0:
            index = self._length + index
        if index >= self._length:
            raise IndexError(f"List index {index} out of range")
        elif index <= self._length // 2:
            cur = self.first
            for _ in range(index - 1):
                cur = cur.next
            return cur
        else:
            cur = self.last
            for _ in range(self._length - index - 1):
                cur = cur.prev
            return cur

    def _insert_first(self, value):
        self.first = self.Node(value, parent=self)
        self.last = self.first
        self._length += 1

    def prepend(self, value):
        if self._length == 0:
            self._insert_first(value)
        else:
            self.first.prev = self.Node(value, next=self.first, parent=self)
            self.first = self.first.prev
            self._length += 1

    def append(self, value):
        if self._length == 0:
            self._insert_first(value)
        else:
            self.last.next = self.Node(value, prev=self.last, parent=self)
            self.last = self.last.next
            self._length += 1

    def insert_before(self, node, value):
        if node.parent != self:
            raise ValueError("Given node does not belong to this list")
        elif node == self.first:
            self.prepend(value)
        else:
            node.prev.next = self.Node(value, prev=node.prev, next=node, parent=self)
            node.prev = node.prev.next
            self._length += 1

    def insert_after(self, node, value):
        if node.parent != self:
            raise ValueError("Given node does not belong to this list")
        elif node == self.last:
            self.append(value)
        else:
            node.next.prev = self.Node(value, prev=node, next=node.next, parent=self)
            node.next = node.next.prev
            self._length += 1

    def insert(self, index, value):
        # accommodate negative indices
        if index < 0:
            index = self._length + index
        # account for front/back of list
        if index == 0:
            self.prepend(value)
        elif index == self._length:
            self.append(value)
        # count from front or back of list, depending on which is closer
        else:
            self.insert_after(self.node_at(index), value)

    def pop_node(self, node):
        if not (node.parent is self):
            raise ValueError("Given node does not belong to this list")
        if node is self.first:
            return self.pop(0)
        elif node is self.last:
            return self.pop()
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
            node.parent = None
            self._length -= 1
            return node.value

    def pop_after(self, node):
        if node.parent != self:
            raise ValueError("Given node does not belong to this list")
        if node is self.last:
            raise IndexError("Can't pop after last node")
        return self.pop_node(node.next)

    def pop_before(self, node):
        if node.parent != self:
            raise ValueError("Given node does not belong to this list")
        if node is self.first:
            raise IndexError("Can't pop before first node")
        return self.pop_node(node.prev)

    def pop(self, index=None):
        # accommodate negative indices
        if index is not None and index < 0:
            index = self._length + index
        # pop only element
        if self.first is self.last:
            if index:  # shorthand for checking if index in [None, 0] - just check if it's falsey
                raise IndexError(f"List index {index} out of range")
            else:
                self.first = None
                self.last = None
                self._length -= 1
        # pop at end
        elif index is None or index == self._length - 1:
            temp = self.last
            self.last.parent = None
            self.last.prev.next = self.last.next
            self.last = self.last.prev
            self._length -= 1
            return temp.value
        # pop from start
        elif index == 0:
            temp = self.first
            self.first.parent = None
            self.first.next.prev = self.first.prev
            self.first = self.first.next
            self._length -= 1
            return temp.value
        # otherwise, find index and pop it
        else:
            return self.pop_node(self.node_at(index))

    def remove(self, value):
        node = self.find_node(value)
        if node:
            self.pop_node(node)
        else:
            raise ValueError(f"{value} is not in list")

    def get(self, index):
        return self.node_at(index).value

    def set(self, index, value):
        self.node_at(index).value = value

    def find_node(self, value):
        """ Returns the node that contains the given value """
        cur = self.first
        while cur:
            if cur.value == value:
                return cur
            cur = cur.next
        return None

    def isempty(self):
        return len(self) == 0

    def gnomesort(self):
        """
        In-place gnome sort. Very efficient sort for bubbling just one out-of-place element.
        Technically insertion sort would be quicker but honestly this is much easier to implement
        and is the same complexity class - O(n) for just one element out-of-place
        """
        # nothing to do if we're empty or singleton
        if len(self) < 2:
            return
        # start with second element, and always compare to the element before
        current = self.first.next
        while current is not None:
            # thus current must have a .prev
            # If this element is unsorted with the element before it, then
            if current.prev and current.value < current.prev.value:
                # swap this element with the element before it
                # using insert_after and pop_before is an easy way to handle first/last identities
                self.insert_after(current, self.pop_before(current))
                # and then check the new previous-element.
            else:
                # advance to next node (or None if this is the last node in the list, in which case we terminate)
                current = current.next

    def copy(self):
        return _LinkedList(self)

    def __copy__(self):
        return self.copy()

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.pop(key)

    def __iter__(self):
        current_node = self.first
        while current_node:
            yield current_node.value
            current_node = current_node.next

    def __reversed__(self):
        current_node = self.last
        while current_node:
            yield current_node.value
            current_node = current_node.prev

    def __contains__(self, item):
        current_node = self.first
        while current_node:
            if current_node.value == item:
                return True
            current_node = current_node.next
        return False

    def __add__(self, other):
        return _LinkedList(list(iter(self)) + list(iter(other)))

    def __iadd__(self, other):
        for elem in other:
            self.append(elem)
        return self

    def __eq__(self, other):
        if not isinstance(other, _LinkedList):
            return False
        for a, b in zip(self, other):
            if a != b:
                return False
            return True

    def __len__(self):
        return self._length

    def __str__(self):
        return f"LinkedList{str(list(iter(self)))}"
