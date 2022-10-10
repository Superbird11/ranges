from contextlib import suppress
from .Range import Range
from ._helper import _is_iterable_non_string, _LinkedList, Inf, Rangelike
from typing import TypeVar, Iterable, Iterator, Union, Any, List


T = TypeVar('T', bound=Any)


class RangeSet(Iterable):
    """
    A class to represent a mutable set of Ranges that may or may not overlap.
    A RangeSet will generally interface cleanly with a Range or another
    RangeSet. In general, most methods called on a RangeSet will try to
    coerce its argument to a RangeSet if it isn't one already (so, a
    list of Ranges is a valid argument for many methods).

    A RangeSet can be constructed from any number of Range-like objects
    or iterables containing Range-like objects, all given as positional
    arguments. Any iterables will be flattened by one later before having
    their contents added to this RangeSet.

    Examples of valid RangeSets include:

    >>> a = RangeSet()  # empty RangeSet
    >>> b = RangeSet([Range(0, 1), Range(2, 3), Range(4, 5)])  # single iterable as a positional argument
    >>> c = RangeSet(Range(0, 1), Range(2, 3), Range(4, 5))   # multiple Ranges as positional arguments
    >>> d = RangeSet("[0, 1)", ["[1.5, 2)", "[2.5, 3)"], "[4, 5]")  # multiple positional arguments, one is an iterable

    Nested iterables are not supported, and will raise a ValueError:

    >>> e = RangeSet([[Range(0, 1), Range(2, 3)], [Range(4, 5), Range(6, 7)]])

    Internally, Ranges are stored ordered from least to greatest.
    Overlapping ranges will be combined into a single Range. For example:

    >>> f = RangeSet("[0, 3]", "[2, 4)", "[5, 6]")
    >>> str(f) == "{[0, 4), [5, 6]}"

    All Ranges in a given RangeSet must be comparable to each other, or
    else errors may occur. The Range type is by default comparable with
    itself, but this functions by comparing the start and end values -
    if two Ranges have non-mutually-comparable start/end values, then
    they cannot be compared, which breaks this data structure's internal
    organization. This is an intentional design decision.

    RangeSets are hashable, meaning they can be used as keys in dicts.
    """
    def __init__(self, *args: Union[Rangelike, Iterable[Rangelike]]):
        """
        Constructs a new RangeSet containing the given sub-ranges.
        :param args: For each positional argument, if the argument is Rangelike, it is added to this RangeSet,
            or if it is an iterable containing Rangelikes, all contained Rangelikes are added to this RangeSet.
        """
        # flatten args
        temp_list = []
        for arg in args:
            if _is_iterable_non_string(arg):
                temp_list.extend(Range(x) for x in arg)
            else:
                temp_list.append(Range(arg))
        # assign own Ranges
        self._ranges = RangeSet._merge_ranges(temp_list)

    def add(self, rng: Rangelike) -> None:
        """
        Adds a copy of the given range or RangeSet to this RangeSet.

        If the argument is not Range-like and is not a RangeSet, then
        a `ValueError` will be raised. If the argument is not comparable
        to other Ranges contained in this RangeSet, then a `TypeError`
        will be raised. If an iterable is given as the
        argument, it will be submitted to the `Range()` constructor.

        To add all ranges in an iterable containing multiple ranges,
        use `.extend()` instead.

        :param rng: A single Rangelike object to add to this RangeSet
        """
        # if it's a RangeSet, then do extend instead
        if isinstance(rng, RangeSet):
            self.extend(rng)
            return
        elif _is_iterable_non_string(rng):
            raise ValueError("argument is iterable and not Range-like; use .extend() instead")
        # otherwise, convert Range to a list at first
        rng = Range(rng)
        # change the error message if necessary
        try:
            temp_ranges = self._ranges.copy()
            # if the list of ranges is empty, then add the node at the beginning
            if len(temp_ranges) == 0:
                temp_ranges.append(rng)
                inserted_node = temp_ranges.first
            # otherwise, if our range would fit at the end, then put it there
            elif rng > temp_ranges.last.value:
                temp_ranges.append(rng)
                inserted_node = temp_ranges.last
            # otherwise, find the node *before which* our range fits
            else:
                node = temp_ranges.first
                while rng > node.value:
                    node = node.next
                temp_ranges.insert_before(node, rng)
                inserted_node = node.prev
            # now, merge this range with the previous range(s):
            if inserted_node.prev:
                prev_union = inserted_node.value.union(inserted_node.prev.value)
                while prev_union and inserted_node.prev:
                    inserted_node.value = prev_union
                    temp_ranges.pop_before(inserted_node)
                    prev_union = inserted_node.value.union(inserted_node.prev.value) if inserted_node.prev else None
            # merge this range with the next range(s)
            if inserted_node.next:
                next_union = inserted_node.value.union(inserted_node.next.value)
                while next_union and inserted_node.next:
                    inserted_node.value = next_union
                    temp_ranges.pop_after(inserted_node)
                    next_union = inserted_node.value.union(inserted_node.next.value) if inserted_node.next else None
        except TypeError:
            raise TypeError(f"Range '{rng}' is not comparable with the other Ranges in this RangeSet")
        # apply changes
        self._ranges = temp_ranges
        # TODO python 3.8 update - use an assignment operator (see the following code):
        # while inserted_node.prev and (prev_union := inserted_node.value.union(inserted_node.prev.value)):
        #     inserted_node.value = prev_union
        #     self._ranges.pop_before(inserted_node)
        # while inserted_node.next and (next_union := inserted_node.value.union(inserted_node.next.value)):
        #     inserted_node.value = next_union
        #     self._ranges.pop_after(inserted_node)

    def extend(self, iterable: Iterable[Rangelike]) -> None:
        """
        Adds a copy of each Range or RangeSet in the given iterable to
        this RangeSet.

        Raises a `TypeError` if the argument is not iterable.

        This method works identically to `.add()` for RangeSets only.

        :param iterable: iterable containing Rangelike objects to add to this RangeSet
        """
        self._ranges = RangeSet._merge_ranges(
            self._ranges + (Range(r) for r in iterable)
        )

    def discard(self, rng: Rangelike) -> None:
        """
        Removes the entire contents of the given RangeSet from this RangeSet.

        This method will only remove a single RangeSet (or Range) from this
        RangeSet at a time. To remove a list of Range-like objects from this
        RangeSet, use .difference_update() instead.

        :param rng: Rangelike to remove from this RangeSet.
        """
        # be lazy and do O(n^2) erasure
        if isinstance(rng, RangeSet):
            temp = self.copy()
            for r in rng:
                temp.discard(r)
            self._ranges = temp._ranges
            return
        # elif _is_iterable_non_string(rng):
        #     raise ValueError("argument is iterable and not range-like. Use .difference_update() instead")
        # make sure rng is a Range
        rng = Range(rng)
        # remove rng from our ranges until we no longer need to
        current_node = self._ranges.first
        while current_node:
            new_range = current_node.value.difference(rng)
            if not new_range or new_range.isempty():
                # first node is entirely consumed by the range to remove. So remove it.
                self._ranges.pop_node(current_node)
            elif isinstance(new_range, RangeSet):
                # replace current value with lower, and add higher just afterwards.
                # It can't possibly overlap with the next range, because they are disjoint.
                current_node.value = new_range._ranges.first.value
                self._ranges.insert_after(current_node, new_range._ranges.last.value)
                # in this case, we also know that we just hit the top of the discarding range.
                # therefore, we can short-circuit.
                break
            else:
                # replace just this element, which was cut off
                if new_range > current_node.value:
                    # we're only computing the difference of one contiguous range.
                    # if all we've done is cut off the bottom part of this range, then
                    # we must have reached the top of the discarding range.
                    # therefore, we can short-circuit.
                    current_node.value = new_range
                    break
                else:
                    # otherwise, we just change this element (maybe replace it with itself) and keep going.
                    current_node.value = new_range
            current_node = current_node.next

    def difference(self, rng_set: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """
        Return a new RangeSet containing the ranges that are in this RangeSet
        but not in the other given RangeSet or list of RangeSets. This
        RangeSet is not modified in the process.

        :param rng_set: A rangelike object to take difference with, or an iterable of Rangelike objects
            to take difference with all of which.
        :return: a RangeSet identical to this one except with the given argument removed from it.
        """
        new_rng_set = self.copy()
        new_rng_set.difference_update(RangeSet(rng_set))
        return new_rng_set

    def difference_update(self, rng_set: Union[Rangelike, Iterable[Rangelike]]) -> None:
        """
        Removes all ranges in the given iterable from this RangeSet.

        If an error occurs while trying to do this, then this RangeSet
        remains unchanged.

        :param rng_set: A rangelike object to take difference with, or an iterable of Rangelike objects
            to take difference with all of which.
        """
        self.discard(RangeSet._to_rangeset(rng_set))

    def intersection(self, rng_set: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """
        Returns a new RangeSet containing the intersection between this
        RangeSet and the given Range or RangeSet - that is, containing
        only the elements shared between this RangeSet and the given
        RangeSet.

        :param rng_set: A rangelike, or iterable containing rangelikes, to find intersection with
        :return: a RangeSet identical to this one except with all values not overlapping the given argument removed.
        """
        # convert to a RangeSet
        rng_set = RangeSet._to_rangeset(rng_set)
        # do O(n^2) difference algorithm
        # TODO rewrite to increase efficiency by short-circuiting
        intersections = [rng1.intersection(rng2) for rng1 in self._ranges for rng2 in rng_set._ranges]
        intersections = [rng for rng in intersections if rng is not None and not rng.isempty()]
        return RangeSet(intersections)

    def intersection_update(self, rng_set: Union[Rangelike, Iterable[Rangelike]]) -> None:
        """
        Updates this RangeSet to contain only the intersections between
        this RangeSet and the given Range or RangeSet, removing the parts
        of this RangeSet's ranges that do not overlap the given RangeSet

        :param rng_set: A rangelike, or iterable containing rangelikes, to find intersection with
        """
        self._ranges = self.intersection(rng_set)._ranges

    def union(self, rng_set: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """
        Returns a new RangeSet containing the overlap between this RangeSet and the
        given RangeSet

        :param rng_set: A rangelike, or iterable of rangelikes, to find union with
        :return: a RangeSet identical to this one but also including all elements in the given argument.
        """
        # convert to RangeSet
        rng_set = RangeSet._to_rangeset(rng_set)
        # simply merge lists
        return RangeSet(self._ranges + rng_set._ranges)

    def update(self, rng_set: Union[Rangelike, Iterable[Rangelike]]) -> None:
        """
        Updates this RangeSet to add all the ranges in the given RangeSet, so
        that this RangeSet now contains the union of its old self and the
        given RangeSet.

        :param rng_set: A rangelike, or iterable of rangelikes, to find union with
        """
        # convert to RangeSet
        rng_set = RangeSet._to_rangeset(rng_set)
        # merge lists
        self._ranges = RangeSet._merge_ranges(self._ranges + rng_set._ranges)

    def symmetric_difference(self, rng_set: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """
        Returns a new RangeSet containing the symmetric difference between this
        RangeSet  and the given Range or RangeSet - everything contained by
        this RangeSet or the given RangeSet, but not both.

        :param rng_set: A rangelike, or iterable of rangelikes, to find symmetric difference with
        :return: A RangeSet containing all values in either this or the given argument, but not both
        """
        # convert to a RangeSet
        rng_set = RangeSet._to_rangeset(rng_set)
        # get union and then remove intersections
        union = self.union(rng_set)
        intersection = self.intersection(rng_set)
        union.difference_update(intersection)
        return union

    def symmetric_difference_update(self, rng_set: Union[Rangelike, Iterable[Rangelike]]) -> None:
        """
        Update this RangeSet to contain the symmetric difference between it and
        the given Range or RangeSet, by removing the parts of the given RangeSet
        that overlap with this RangeSet from this RangeSet.

        :param rng_set: A rangelike, or iterable of rangelikes, to find symmetric difference with
        """
        # the easiest way to do this is just to do regular symmetric_difference and then copy the result
        rng_set = RangeSet._to_rangeset(rng_set)
        self._ranges = self.symmetric_difference(rng_set)._ranges

    def isdisjoint(self, other: Union[Rangelike, Iterable[Rangelike]]) -> bool:
        """
        Returns `True` if there is no overlap between this RangeSet and the
        given RangeSet.

        :param other: a rangelike, or iterable of rangelikes, to check if overlaps this RangeSet
        :return: False the argument (or any element of an iterable argument) overlap this Rangeset, or True otherwise
        """
        # convert to RangeSet
        other = RangeSet._to_rangeset(other)
        # O(n^2) comparison
        # TODO improve efficiency by mergesort/short-circuiting
        return all(rng1.isdisjoint(rng2) for rng1 in self._ranges for rng2 in other._ranges)

    def popempty(self) -> None:
        """
        Removes all empty ranges from this RangeSet. This is mainly used
        internally as a helper method, but can also be used deliberately
        (in which case it will usually do nothing).
        """
        node = self._ranges.first
        while node:
            if node.value.isempty():
                # you're not supposed to remove from a list while iterating through it
                # however, since this is a linked list, this actually doesn't break!
                self._ranges.pop_node(node)
            node = node.next

    def getrange(self, item: Union[T, Iterable[T], 'RangeSet']) -> Rangelike:
        """
        If the given item is in this RangeSet, returns the specific Range it's
        in.

        If the given item is a RangeSet or Iterable and is partly contained in
        multiple ranges, then returns a RangeSet with only those ranges that
        contain some part of it.

        Otherwise, raises an `IndexError`.

        :param item: item to search for in this RangeSet
        :return: if item is a single element, then the Range containing it. If item is iterable,
            then a RangeSet containing only Ranges containing items.
        """
        if item in self:
            for rng in self._ranges:
                if item in rng:
                    return rng
            # if that doesn't work, try iterating through it
            # if this comes up non-empty, then return that
            if _is_iterable_non_string(item):
                founds = [
                    rng for rng in self._ranges
                    for subitem in item
                    if subitem in rng
                ]
                if founds:
                    return RangeSet(founds)
            raise IndexError(f"'{item}' could not be isolated")
        raise IndexError(f"'{item}' is not in this RangeSet")

    def ranges(self) -> List[Range]:
        """
        Returns a `list` of the Range objects that this RangeSet contains

        :return: the Ranges that make up this RangeSet
        """
        return list(iter(self._ranges))

    def clear(self) -> None:
        """
        Removes all ranges from this RangeSet, leaving it empty.
        """
        self._ranges = _LinkedList()

    def complement(self) -> 'RangeSet':
        """
        Returns a RangeSet containing all items not present in this RangeSet

        :return: the complement of this RangeSet
        """
        return RangeSet(Range()) - self

    def isempty(self) -> bool:
        """
        Returns True if this RangeSet contains no values, and False otherwise

        :return: whether this RangeSet is empty
        """
        return self._ranges.isempty() or all(r.isempty() for r in self._ranges)

    def copy(self) -> 'RangeSet':
        """
        Returns a shallow copy of this RangeSet

        :return: a shallow copy of this RangeSet
        """
        return RangeSet(self)

    def isinfinite(self) -> bool:
        """
        Returns True if this RangeSet has a negative bound of -Inf or a positive bound of +Inf,
        and False otherwise

        :return: whether either furthest bound of this RangeSet is infinite
        """
        return self._ranges.first.value.start == -Inf or self._ranges.last.value.end == Inf

    def containseverything(self) -> bool:
        """
        Returns True if this RangeSet contains all elements

        :return: whether this RangeSet is infinite and its complement is empty
        """
        return self.isinfinite() and self.complement().isempty()

    @staticmethod
    def _merge_ranges(ranges: Iterable[Range]) -> _LinkedList[Range]:
        """
        Compresses all of the ranges in the given iterable, and
        returns a _LinkedList containing them.

        :param ranges: iterable containing ranges to merge
        :return: a _LinkedList containing ranges, merged together.
        """
        # sort our list of ranges, first
        ranges = _LinkedList(sorted(ranges))
        # # determine if we need to do anything
        # if len(ranges) < 2:
        #     return
        # try to merge each range with the one after it, up until the end of the list
        node = ranges.first
        while node and node.next:
            prev_range = node.value
            next_range = node.next.value
            new_range = prev_range.union(next_range)
            if new_range is not None:  # TODO python 3.8 refactoring - this is a great place for :=
                node.value = new_range
                ranges.pop_after(node)
            else:
                node = node.next
        return ranges

    @staticmethod
    def _to_rangeset(other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """
        Helper method.
        Converts the given argument to a RangeSet. This mainly exists to increase performance
        by not duplicating things that are already RangeSets, and for the sake of graceful
        error handling.

        :param other: Same as arguments for RangeSet's constructor
        :return: the given RangeSet, if `other` is a RangeSet, or a RangeSet constructed from it otherwise
        """
        if not isinstance(other, RangeSet):
            try:
                other = RangeSet(other)
            except ValueError:
                raise ValueError(f"Cannot convert {type(other)} to a RangeSet")
        return other

    def __contains__(self, item: Union[T, Rangelike]) -> bool:
        """
        Returns true if this RangeSet completely contains the given item, Range,
        RangeSet, or iterable (which will be assumed to be a RangeSet unless
        coercing it into one fails, in which case it will be assumed to be an
        item).
        Returns false otherwise.
        A RangeSet will always contain itself.

        :param item: item to check if is contained in this RangeSet
        :return: whether the item is present in this RangeSet
        """
        if self == item:
            return True
        with suppress(TypeError):
            if _is_iterable_non_string(item):
                with suppress(ValueError):
                    return all(
                        any(subitem in rng for rng in self._ranges)
                        for subitem in RangeSet._to_rangeset(item)
                    )
        return any(item in rng for rng in self._ranges)

    def __invert__(self) -> 'RangeSet':
        """
        Equivalent to self.complement()

        :return: a RangeSet containing everything that is not in this RangeSet
        """
        return self.complement()

    def __eq__(self, other: Union[Range, 'RangeSet']) -> bool:
        """
        Returns True if this RangeSet's ranges exactly match the other
        RangeSet's ranges, or if the given argument is a Range and this
        RangeSet contains only one identical Range

        :param other: other object to check equality with
        :return: whether this Rangeset equals the given object
        """
        if isinstance(other, RangeSet):
            return len(self._ranges) == len(other._ranges) and \
                   all(mine == theirs for mine, theirs in zip(self._ranges, other._ranges))
        elif isinstance(other, Range):
            return len(self._ranges) == 1 and self._ranges[0] == other
        else:
            return False

    def __lt__(self, other: Union[Range, 'RangeSet']) -> bool:
        """
        Returns an ordering-based comparison based on the lowest ranges in
        self and other.

        :param other: other object to compare with
        :return: True if this RangeSet should be ordered before the other object, False otherwise
        """
        if isinstance(other, RangeSet):
            # return the first difference between this range and the next range
            for my_val, their_val in zip(self._ranges, other._ranges):
                if my_val != their_val:
                    return my_val < their_val
            return len(self._ranges) < len(other._ranges)
        elif isinstance(other, Range):
            # return based on the first range in this RangeSet
            return len(self._ranges) >= 1 and self._ranges[0] < other
        else:
            return False

    def __gt__(self, other: Union[Range, 'RangeSet']) -> bool:
        """
        Returns an ordering-based comparison based on the lowest ranges in
        self and other.

        :param other: other object to compare with
        :return: True if this RangeSet should be ordered after the other object, False otherwise
        """
        if isinstance(other, RangeSet):
            # return the first difference between this range and the next range
            for my_val, their_val in zip(self._ranges, other._ranges):
                if my_val != their_val:
                    return my_val > their_val
            return len(self._ranges) > len(other._ranges)
        elif isinstance(other, Range):
            # return based on the first range in this RangeSet
            return len(self._ranges) >= 1 and self._ranges[0] > other
        else:
            return False

    def __le__(self, other: Union[Range, 'RangeSet']) -> bool:
        """
        :param other: other object to compare with
        :return: True if this RangeSet equals or should be ordered before the other object, False otherwise
        """
        return self < other or self == other

    def __ge__(self, other: Union[Range, 'RangeSet']) -> bool:
        """
        :param other: other object to compare with
        :return: True if this RangeSet equals or should be ordered after the other object, False otherwise
        """
        return self > other or self == other

    def __ne__(self, other: Union[Range, 'RangeSet']) -> bool:
        """
        :param other: other object to compare with
        :return: True if this RangeSet is not equal to the other object, False if it is equal
        """
        return not self == other

    def __and__(self, other: Union[Range, 'RangeSet']) -> bool:
        """ returns (self & other), identical to :func:`~RangeSet.intersection` """
        return self.intersection(other)

    def __or__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ returns (self | other), identical to :func:`~RangeSet.union` """
        return self.union(other)

    def __xor__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ returns (self ^ other), identical to :func:`~RangeSet.symmetric_difference` """
        return self.symmetric_difference(other)

    def __sub__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ returns (self - other), identical to :func:`~RangeSet.difference` """
        return self.difference(other)

    def __add__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ Returns (self + other), identical to :func:`~RangeSet.union` """
        return self.union(other)

    def __iand__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ Executes (self &= other), identical to :func:`~RangeSet.intersection_update` """
        self.intersection_update(other)
        return self

    def __ior__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ Executes (self |= other), identical to :func:`~RangeSet.update` """
        self.update(other)
        return self

    def __ixor__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ Executes (self ^= other), identical to :func:`~RangeSet.symmetric_difference_update` """
        self.symmetric_difference_update(other)
        return self

    def __iadd__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ Executes (self += other), identical to :func:`~RangeSet.update` """
        self.update(other)
        return self

    def __isub__(self, other: Union[Rangelike, Iterable[Rangelike]]) -> 'RangeSet':
        """ Executes (self -= other), identical to :func:`~RangeSet.difference_update` """
        self.difference_update(other)
        return self

    def __iter__(self) -> Iterator[Range]:
        """
        Generates the ranges in this object, in order
        """
        return iter(self._ranges)

    def __hash__(self):
        return hash(tuple(iter(self._ranges)))

    def __bool__(self) -> bool:
        """
        :return: False if this RangeSet is empty, True otherwise
        """
        return not self.isempty()

    def __str__(self):
        return f"{{{', '.join(str(r) for r in self._ranges)}}}"  # other possibilities: '∪', ' | '

    def __repr__(self):
        return f"RangeSet{{{', '.join(repr(r) for r in self._ranges)}}}"
