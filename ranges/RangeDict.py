from contextlib import suppress
from operator import is_
from ._helper import _UnhashableFriendlyDict, _LinkedList, _is_iterable_non_string, Rangelike
from .Range import Range
from .RangeSet import RangeSet
from typing import Iterable, Union, Any, TypeVar, List, Tuple, Dict, Tuple

T = TypeVar('T', bound=Any)
V = TypeVar('V', bound=Any)


class RangeDict:
    """ RangeDict(self, iterable, *, identity=False)
    A class representing a dict-like structure where continuous ranges
    correspond to certain values. For any item given to lookup, the
    value obtained from a RangeDict will be the one corresponding to
    the first range into which the given item fits. Otherwise, RangeDict
    provides a similar interface to python's built-in dict.

    A RangeDict can be constructed in one of four ways:

    >>> # Empty
    >>> a = RangeDict()

    >>> # From an existing RangeDict object
    >>> b = RangeDict(a)

    >>> # From a dict that maps Ranges to values
    >>> c = RangeDict({
    ...     Range('a', 'h'): "First third of the lowercase alphabet",
    ...     Range('h', 'p'): "Second third of the lowercase alphabet",
    ...     Range('p', '{'): "Final third of the lowercase alphabet",
    ... })
    >>> print(c['brian'])  # First third of the lowercase alphabet
    >>> print(c['king arthur'])  # Second third of the lowercase alphabet
    >>> print(c['python'])  # Final third of the lowercase alphabet

    >>> # From an iterable of 2-tuples, like a regular dict
    >>> d = RangeDict([
    ...     (Range('A', 'H'), "First third of the uppercase alphabet"),
    ...     (Range('H', 'P'), "Second third of the uppercase alphabet"),
    ...     (Range('P', '['), "Final third of the uppercase alphabet"),
    ... ])

    A RangeDict cannot be constructed from an arbitrary number of positional
    arguments or keyword arguments.

    RangeDicts are mutable, so new range correspondences can be added
    at any time, with Ranges or RangeSets acting like the keys in a
    normal dict/hashtable. New keys must be of type Range or RangeSet,
    or they must be able to be coerced into a RangeSet. Given
    keys are also copied before they are added to a RangeDict.

    Adding a new range that overlaps with an existing range will
    make it so that the value returned for any given number will be
    the one corresponding to the most recently-added range in which
    it was found (Ranges are compared by `start`, `include_start`, `end`,
    and `include_end` in that priority order). Order of insertion is
    important.

    The RangeDict constructor, and the `.update()` method, insert elements
    in order from the iterable they came from. As of python 3.7+, dicts
    retain the insertion order of their arguments, and iterate in that
    order - this is respected by this data structure. Other iterables,
    like lists and tuples, have order built-in. Be careful about using
    sets as arguments, since they have no guaranteed order.

    Be very careful about adding a range from -infinity to +infinity.
    If defined using the normal Range constructor without any start/end
    arguments, then that Range will by default accept any value (see
    Range's documentation for more info). However, the first non-infinite
    Range added to the RangeDict will overwrite part of the infinite Range,
    and turn it into a Range of that type only. As a result, other types
    that the infinite Range may have accepted before, will no longer work:

    >>> e = RangeDict({Range(include_end=True): "inquisition"})
    >>> print(e)  # {{[-inf, inf)}: inquisition}
    >>> print(e.get(None))  # inquisition
    >>> print(e.get(3))  # inquisition
    >>> print(e.get("holy"))  # inquisition
    >>> print(e.get("spanish"))  # inquisition
    >>>
    >>> e[Range("a", "m")] = "grail"
    >>>
    >>> print(e)  # {{[-inf, a), [m, inf)}: inquisition, {[a, m)}: grail}
    >>> print(e.get("spanish"))  # inquisition
    >>> print(e.get("holy"))  # grail
    >>> print(e.get(3))  # KeyError
    >>> print(e.get(None))  # KeyError

    In general, unless something has gone wrong, the RangeDict will not
    include any empty ranges. Values will disappear if there are not
    any keys that map to them. Adding an empty Range to the RangeDict
    will not trigger an error, but will have no effect.

    By default, the range set will determine value uniqueness by equality
    (`==`), not by identity (`is`), and multiple rangekeys pointing to the
    same value will be compressed into a single RangeSet pointed at a
    single value. This is mainly meaningful for values that are mutable,
    such as `list`s or `set`s.
    If using assignment operators besides the generic `=` (`+=`, `|=`, etc.)
    on such values, be warned that the change will reflect upon the entire
    rangeset.

    >>> # [{3}] == [{3}] is True, so the two ranges are made to point to the same object
    >>> f = RangeDict({Range(1, 2): {3}, Range(4, 5): {3}})
    >>> print(f)  # {{[1, 2), [4, 5)}: {3}}
    >>>
    >>> # f[1] returns the {3}. When |= is used, this object changes to {3, 4}
    >>> f[Range(1, 2)] |= {4}
    >>> # since the entire rangeset is pointing at the same object, the entire range changes
    >>> print(f)  # {{[1, 2), [4, 5)}: {3, 4}}

    This is because `dict[value] = newvalue` calls `dict.__setitem__()`, whereas
    `dict[value] += item` instead calls `dict[value].__iadd__()` instead.
    To make the RangeDict use identity comparison instead, construct it with the
    keyword argument `identity=True`, which should help:

    >>> # `{3} is {3}` is False, so the two ranges don't coalesce
    >>> g = RangeDict({Range(1, 2): {3}, Range(4, 5): {3}}, identity=True)
    >>> print(g)  # {{[1, 2)}: {3}, {[4, 5)}: {3}}

    To avoid the problem entirely, you can also simply not mutate mutable values
    that multiple rangekeys may refer to, substituting non-mutative operations:

    >>> h = RangeDict({Range(1, 2): {3}, Range(4, 5): {3}})
    >>> print(h)  # {{[1, 2), [4, 5)}: {3}}
    >>> h[Range(1, 2)] = h[Range(1, 2)] | {4}
    >>> print(h)  # {{[4, 5)}: {3}, {[1, 2)}: {3, 4}}
    """
    # sentinel for checking whether an arg was passed, where anything is valid including None
    _sentinel = object()

    def __init__(self, iterable: Union['RangeDict', Dict[Rangelike, V], Iterable[Tuple[Rangelike, V]]] = _sentinel,
                 *, identity=False):
        """ __init__(iterable, *, identity=False)
        Initialize a new RangeDict from the given iterable. The given iterable
        may be either a RangeDict (in which case, a copy will be created),
        a regular dict with all keys able to be converted to Ranges, or an
        iterable of 2-tuples (range, value).

        If the argument `identity=True` is given, the RangeDict will use `is` instead
        of `==` when it compares multiple rangekeys with the same associated value to
        possibly merge them.

        :param iterable: Optionally, an iterable from which to source keys - either a RangeDict, a regular dict
            with Rangelike objects as keys, or an iterable of (range, value) tuples.
        :param identity: optionally, a toggle to use identity instead of equality when determining key-value
            similarity. By default, uses equality, but will use identity instead if True is passed.
        """
        # Internally, RangeDict has two data structures
        #    _values is a dict {value: [rangeset, ...], ..., '_sentinel': [(value: [rangeset, ...]), ...]}
        #          The sentinel allows the RangeDict to accommodate unhashable types.
        #    _ranges is a list-of-lists, [[(intrangeset1, value1), (intrangeset2, value2), ...],
        #                                 [(strrangeset1, value1), (strrangeset2, value2), ...],
        #                                 ...]
        #          where each inner list is a list of (RangeSet, corresponding_value) tuples.
        #          Each inner list corresponds to a different, mutually-incomparable, type of Range.
        # We use _values to cross-reference with while adding new ranges, to avoid having to search the entire
        #  _ranges for the value we want to point to.
        # Meanwhile, _ranges is a list-of-lists instead of just a list, so that we can accommodate ranges of
        #  different types (e.g. a RangeSet of ints and a RangeSet of strings) pointing to the same values.
        self._values = _UnhashableFriendlyDict()
        if identity:
            self._values._operator = is_
        if iterable is RangeDict._sentinel:
            self._rangesets = _LinkedList()
        elif isinstance(iterable, RangeDict):
            self._values.update({val: rngsets[:] for val, rngsets in iterable._values.items()})
            self._rangesets = _LinkedList([rngset.copy() for rngset in iterable._rangesets])
        elif isinstance(iterable, dict):
            self._rangesets = _LinkedList()
            for rng, val in iterable.items():
                if _is_iterable_non_string(rng):
                    for r in rng:
                        self.add(r, val)
                else:
                    self.add(rng, val)
        else:
            try:
                assert(_is_iterable_non_string(iterable))  # creative method of avoiding code reuse!
                self._rangesets = _LinkedList()
                for rng, val in iterable:
                    # this should not produce an IndexError. It produces a TypeError instead.
                    # (or a ValueError in case of too many to unpack. Which is fine because it screens for 3-tuples)
                    if _is_iterable_non_string(rng):
                        # this allows constructing with e.g. rng=[Range(1, 2), Range('a', 'b')], which makes sense
                        for r in rng:
                            self.add(r, val)
                    else:
                        self.add(rng, val)
            except (TypeError, ValueError, AssertionError):
                raise ValueError("Expected a dict, RangeDict, or iterable of 2-tuples")
        self._values[RangeDict._sentinel] = []
        self.popempty()

    def add(self, rng: Rangelike, value: V) -> None:
        """
        Add the single given Range/RangeSet to correspond to the given value.
        If the given Range overlaps with a Range that is already contained
        within this RangeDict, then the new range takes precedence.

        To add multiple Ranges of the same type, pack them into a RangeSet
        and pass that.

        To add a list of multiple Ranges of different types, use `.update()`
        instead. Using this method instead will produce a `TypeError`.

        If an empty Range is given, then this method does nothing.

        :param rng: Rangekey to add
        :param value: value to add corresponding to the given Rangekey
        """
        # copy the range and get it into an easy-to-work-with form
        try:
            rng = RangeSet(rng)
        except TypeError:
            raise TypeError("argument 'rng' for .add() must be able to be converted to a RangeSet")
        if rng.isempty():
            return
        # special case: if we try to add a perfectly infinite range, then completely empty this rangeset
        # and add this as the only element (since it will subsume everything else anyway)
        if rng.containseverything():
            self._rangesets.clear()
            self._values.clear()
        # first, remove this range from any existing range
        short_circuit = False
        for rngsetlist in self._rangesets:
            # rngsetlist is a tuple (_LinkedList(ranges), value)
            for rngset in rngsetlist:
                # rngset
                with suppress(TypeError):
                    rngset[0].discard(rng)
                    short_circuit = True  # (naively) assume only one type of rngset will be compatible
            if short_circuit:
                self.popempty()
                break
        # then, add it back in depending on whether it shares an existing value or not.
        if value in self._values:
            # duplicate value. More than one range must map to it.
            existing_rangesets = self._values[value]
            # existing_rangesets is a list (not _LinkedList) of RangeSets that correspond to value.
            # if there's already a whole RangeSet pointing to value, then simply add to that RangeSet
            for rngset in existing_rangesets:
                if len(existing_rangesets) > 1 and rngset.containseverything():
                    continue
                with suppress(TypeError):
                    # ...once we find the RangeSet of the right type
                    rngset.add(rng)
                    # And then bubble it into place in whichever _LinkedList would have contained it.
                    # This is one empty list traversal for every non-modified _LinkedList, and one gnomesort
                    #   for the one we really want. A little time loss but not that much. Especially not
                    #   any extra timeloss for single-typed RangeDicts.
                    self._sort_ranges()
                    self._coalesce_infinite_ranges()
                    # And short-circuit, since we've already dealt with the complications and don't need to
                    #   do any further modification of _values or _rangesets
                    return
            # if we didn't find a RangeSet of the right type, then we must add rng as a new RangeSet of its own type.
            # add a reference in _values
            self._values[value].append(rng)
        else:
            # new value. This is easy, we just need to add a value for it:
            self._values[value] = [rng]
        # Now that we've added our new RangeSet into _values, we need to make sure it's accounted for in _rangesets
        # we will first try to insert it into all our existing rangesets
        for rngsetlist in self._rangesets:
            # rngsetlist is a _LinkedList of (RangeSet, value) tuples
            # [(rangeset0, value0), (rangeset1, value1), ...]
            with suppress(TypeError):
                # "try" == "assess comparability with the rest of the RangeSets in this _LinkedList".
                # This is checked via trying to execute a dummy comparison with the first RangeSet in this category,
                #   and seeing if it throws a TypeError.
                # Though it's kinda silly, this is probably the best way to handle this. See:
                #     https://stackoverflow.com/q/57717100/2648811
                _ = rng < rngsetlist[0][0]
                # If it doesn't raise an error, then it's comparable and we're good.
                # Add it, bubble it to sorted order via .gnomesort(), and return.
                rngsetlist.append((rng, value))
                rngsetlist.gnomesort()
                self._coalesce_infinite_ranges()
                return
        # if no existing rangeset accepted it, then we need to add one.
        # singleton _LinkedList containing just (rng, value), appended to self._rangesets
        self._rangesets.append(_LinkedList(((rng, value),)))
        self._coalesce_infinite_ranges()

    def adddefault(self, rng: Rangelike, value: V) -> None:
        """
        Add a single Range/Rangeset to correspond to the given value.
        If the given range overlaps with an existing rangekey, the
        existing rangekey takes precedence.

        To add a list of multiple Ranges of different types, use `.update()`
        instead. Using this method instead will produce a `TypeError`.

        If an empty Range is given, then this method does nothing.

        If a range is given that contains everything (regardless of whether
        its infinite endpoints are inclusive or exclusive), then the 'default'
        value for all types of ranges currently contained in this RangeDict
        will be made to correspond to the given value (no ranges of new types
        will be added, and types that were previously incompatible with this
        RangeDict's contents will remain that way).

        :param rng: Rangekey to add
        :param value: value to add corresponding to the given Rangekey
        """
        # copy the range and get it into an easy-to-work-with form
        try:
            rng = RangeSet(rng)
        except TypeError:
            raise TypeError("argument 'rng' for .adddefault() must be able to be converted to a RangeSet")
        if rng.isempty():
            return
        # special case: if the range is both infinite and typeless
        # in this case, instead of finding all differences from rng, we must
        # find all differences _for each type of rangeset_ in this dict.
        if rng.containseverything():
            if self.isempty():
                self.add(rng, value)
                return
            i = 0
            while i < len(self._rangesets):
                rngsetlist = self._rangesets[i]
                i += 1
                # rngsetlist is a _LinkedList of (RangeSet, value) tuples
                # [(rangeset0, value0), (rangeset1, value1), ...]
                r = rng.copy()
                for rngset, _ in rngsetlist:
                    r.difference_update(rngset)
                    if r.isempty():
                        break
                if not r.isempty():
                    self.add(r, value)
                    i -= 1
            return
        # if range is not infinite and typeless, then
        # remove all ranges that currently exist from the given range
        # (ignoring ranges that conflict in type)
        for rngsetlist in self._rangesets:
            # rngsetlist is a _LinkedList of (RangeSet, value) tuples
            # [(rangeset0, value0), (rangeset1, value1), ...]
            try:
                for rngset, _ in rngsetlist:
                    rng.difference_update(rngset)
                    if rng.isempty():
                        return
            except TypeError:
                continue
        # now that we can be confident the given range doesn't overlap any existing ranges,
        # add it as normal
        self.add(rng, value)

    def update(self, iterable: Union['RangeDict', Dict[Rangelike, V], Iterable[Tuple[Rangelike, V]]]) -> None:
        """
        Adds the contents of the given iterable (either another RangeDict, a
        `dict` mapping Range-like objects to values, or a list of 2-tuples
        `(range-like, value)`) to this RangeDict.

        :param iterable: An iterable containing keys and values to add to this RangeDict
        """
        # coerce to RangeDict and add that
        if not isinstance(iterable, RangeDict):
            iterable = RangeDict(iterable)
        for value, rangesets in iterable._values.items():
            for rngset in rangesets:
                self.add(rngset, value)

    def getitem(self, item: T) -> Tuple[List[RangeSet], RangeSet, Range, V]:
        """
        Returns both the value corresponding to the given item, the Range
        containing it, and the set of other contiguous ranges that would
        have also yielded the same value, as a 4-tuple
        `([RangeSet1, Rangeset2, ...], RangeSet, Range, value)`.

        In reverse order, that is
          - the value corresponding to item
          - the single continuous range directly containing the item
          - the RangeSet directly containing the item and corresponding
            to the value
          - a list of all RangeSets (of various non-mutually-comparable
            types) that all correspond to the value. Most of the time,
            this will be a single-element list, if only one type of Range
            is used in the RangeDict. Otherwise, if ranges of multiple
            types (e.g. int ranges, string ranges) correspond to the same
            value, this list will contain all of them.

        Using `.get()`, `.getrange()`, `.getrangeset()`, or
        `.getrangesets()` to isolate just one of those return values is
        usually easier. This method is mainly used internally.

        Raises a `KeyError` if the desired item is not found.

        :param item: item to search for
        :return: a 4-tuple (keys with same value, containing RangeSet, containing Range, value)
        """
        for rngsets in self._rangesets:
            # rngsets is a _LinkedList of (RangeSet, value) tuples
            for rngset, value in rngsets:
                try:
                    rng = rngset.getrange(item)
                    return self._values[value], rngset, rng, value
                except IndexError:
                    # try RangeSets of the same type, corresponding to other values
                    continue
                except TypeError:
                    # try RangeSets of a different type
                    break
        raise KeyError(f"'{item}' was not found in any range")

    def getrangesets(self, item: T) -> List[RangeSet]:
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns a list of all RangeSets in this RangeDict that
        correspond to that value.

        Most of the time, this will be a single-element list, if only one
        type of Range is used in the RangeDict. Otherwise, if ranges of
        multiple types (e.g. int ranges, string ranges) correspond to the
        same value, this list will contain all of them.

        Raises a `KeyError` if the given item is not found.

        :param item: item to search for
        :return: all RangeSets in this RangeDict that correspond to the same value as the given item
        """
        return self.getitem(item)[0]

    def getrangeset(self, item: T) -> RangeSet:
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns the RangeSet containing the given item that
        corresponds to that value.

        To find other RangeSets of other types that correspond to the same
        value, use `.getrangesets()` instead.

        Raises a `KeyError` if the given item is not found.

        :param item: item to search for
        :return: the RangeSet key containing the given item
        """
        return self.getitem(item)[1]

    def getrange(self, item: T) -> Range:
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns the single contiguous range containing the given item
        that corresponds to that value.

        To find the RangeSet of all Ranges that correspond to that item,
        use `.getrangeset()` instead.

        Raises a `KeyError` if the given item is not found.

        :param item: item to search for
        :return: the Range most directly containing the given item
        """
        return self.getitem(item)[2]

    def get(self, item: T, default: Any = _sentinel) -> Union[V, Any]:
        """
        Returns the value corresponding to the given item, based on
        the most recently-added Range containing it.

        The `default` argument is optional.
        Like Python's built-in `dict`, if `default` is given, returns that if
        `item` is not found.
        Otherwise, raises a `KeyError`.

        :param item: item to search for
        :param default: optionally, a value to return, if item is not found
            (if not provided, raises a KeyError if not found)
        :return: the value corrsponding to the item, or default if item is not found
        """
        try:
            return self.getitem(item)[3]
        except KeyError:
            if default is not RangeDict._sentinel:
                return default
            raise

    def getoverlapitems(self, rng: Rangelike) -> List[Tuple[List[RangeSet], RangeSet, V]]:
        """
        Returns a list of 3-tuples
        [([RangeSet1, ...], RangeSet, value), ...]
        corresponding to every distinct rangekey of this RangeDict that
        overlaps the given range.

        In reverse order, for each tuple, that is
          - the value corresponding to the rangeset
          - the RangeSet corresponding to the value that intersects the given range
          - a list of all RangeSets (of various non-mutually-comparable
            types) that all correspond to the value. Most of the time,
            this will be a single-element list, if only one type of Range
            is used in the RangeDict. Otherwise, if ranges of multiple
            types (e.g. int ranges, string ranges) correspond to the same
            value, this list will contain all of them.

        Using `.getoverlap()`, `.getoverlapranges()`, or
        `.getoverlaprangesets()`
        to isolate just one of those return values is
        usually easier. This method is mainly used internally.

        :param rng: Rangelike to search for
        :return: a list of 3-tuples (Rangekeys with same value, containing RangeSet, value)
        """
        ret = []
        for rngsets in self._rangesets:
            # rngsets is a _LinkedList of (RangeSet, value) tuples
            for rngset, value in rngsets:
                try:
                    if rngset.intersection(rng):
                        ret.append((self._values[value], rngset, value))
                except TypeError:
                    break
                # do NOT except ValueError - if `rng` is not rangelike, then error should be thrown.
        return ret

    def getoverlap(self, rng: Rangelike) -> List[V]:
        """
        Returns a list of values corresponding to every distinct
        rangekey of this RangeDict that overlaps the given range.

        :param rng: Rangelike to search for
        :return: a list of values corresponding to each rangekey intersected by rng
        """
        return [t[2] for t in self.getoverlapitems(rng)]

    def getoverlapranges(self, rng: Rangelike) -> List[RangeSet]:
        """
        Returns a list of all rangekeys in this RangeDict that intersect with
        the given range.

        :param rng: Rangelike to search for
        :return: a list of all RangeSet rangekeys intersected by rng
        """
        return [t[1] for t in self.getoverlapitems(rng)]

    def getoverlaprangesets(self, rng: Rangelike) -> List[List[RangeSet]]:
        """
        Returns a list of RangeSets corresponding to the same value as every
        rangekey that intersects the given range.

        :param rng: Rangelike to search for
        :return: a list lists of rangesets that correspond to the same values as every rangekey intersected by rng
        """
        return [t[0] for t in self.getoverlapitems(rng)]

    def getvalue(self, value: V) -> List[RangeSet]:
        """
        Returns the list of RangeSets corresponding to the given value.

        Raises a `KeyError` if the given value is not corresponded to by
        any RangeSets in this RangeDict.

        :param value: value to search for
        :return: a list of rangekeys that correspond to the given value
        """
        try:
            return self._values[value]
        except KeyError:
            raise KeyError(f"value '{value}' is not present in this RangeDict")

    def set(self, item: T, new_value: V) -> V:
        """
        Changes the value corresponding to the given `item` to the given
        `new_value`, such that all ranges corresponding to the old value
        now correspond to the `new_value` instead.

        Returns the original, overwritten value.

        If the given item is not found, raises a `KeyError`.

        :param item: item to search for
        :param new_value: value to set for all rangekeys sharing the same value as item corresponds to
        :return: the previous value those rangekeys corresponded to
        """
        try:
            old_value = self.get(item)
        except KeyError:
            raise KeyError(f"Item '{item}' is not in any Range in this RangeDict")
        self.setvalue(old_value, new_value)
        return old_value

    def setvalue(self, old_value: V, new_value: V) -> None:
        """
        Changes all ranges corresponding to the given `old_value` to correspond
        to the given `new_value` instead.

        Raises a `KeyError` if the given `old_value` isn't found.

        :param old_value: value to change for all keys that correspond to it
        :param new_value: value to replace it with
        """
        try:
            rangesets = list(self._values[old_value])
        except KeyError:
            raise KeyError(f"Value '{old_value}' is not in this RangeDict")
        for rngset in rangesets:
            self.add(rngset, new_value)

    def popitem(self, item: T) -> Tuple[List[RangeSet], RangeSet, Range, V]:
        """
        Returns the value corresponding to the given item, the Range containing
        it, and the set of other contiguous ranges that would have also yielded
        the same value, as a 4-tuple
        `([RangeSet1, Rangeset2, ...], RangeSet, Range, value)`.

        In reverse order, that is
          - the value corresponding to item
          - the single continuous range directly containing the item
          - the RangeSet directly containing the item and corresponding to the
            value
          - a list of all RangeSets (of various non-mutually-comparable types)
            that all correspond to the value. Most of the time, this will be a
            single-element list, if only one type of Range is used in the
            RangeDict. Otherwise, if ranges of multiple types (e.g. int ranges,
            string ranges) correspond to the same value, this list will contain
            all of them.

        Also removes all of the above from this RangeDict.

        While this method is used a lot internally, it's usually easier to
        simply use `.pop()`, `.poprange()`, `.poprangeset()`, or
        `.poprangesets()` to get the single item of interest.

        Raises a KeyError if the desired item is not found.

        :param item: item to search for
        :return: a 4-tuple (keys with same value, containing RangeSet, containing Range, value)
        """
        # search for item linked list-style
        for rngsetlist in self._rangesets:
            # rngsetlist is a _LinkedList of (RangeSet, value) tuples
            cur = rngsetlist.first
            while cur:
                try:
                    rng = cur.value[0].getrange(item)
                    rngsetlist.pop_node(cur)
                    rngsets = self._values.pop(cur.value[1])
                    self.popempty()
                    return rngsets, cur.value[0], rng, cur.value[1]
                except IndexError:
                    # try the next range correspondence
                    cur = cur.next
                    continue
                except TypeError:
                    # try ranges of a different type
                    break
        raise KeyError(f"'{item}' was not found in any range")

    def poprangesets(self, item: T) -> List[RangeSet]:
        """
        Finds the value to which the given item corresponds, and returns the
        list of RangeSets that correspond to that value (see
        `.getrangesets()`).

        Also removes the value, and all RangeSets from this RangeDict. To
        remove just one range and leave the rest intact, use `.remove()`
        instead.

        Raises a `KeyError` if the given item is not found.

        :param item: item to search for
        :return: all RangeSets in this RangeDict that correspond to the same value as the given item
        """
        return self.popitem(item)[0]

    def poprangeset(self, item: T) -> RangeSet:
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns the RangeSet containing the given item that
        corresponds to that value.

        Also removes the value and all ranges that correspond to it from this
        RangeDict. To remove just one range and leave the rest intact, use
        `.remove()` instead.

        Raises a `KeyError` if the given item is not found.

        :param item: item to search for
        :return: the RangeSet key containing the given item
        """
        return self.popitem(item)[1]

    def poprange(self, item: T) -> Range:
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns the single contiguous range containing the given item
        that corresponds to that value.

        Also removes the value and all ranges that correspond to it from this
        RangeDict. To remove just one range and leave the rest intact, use
        `.remove()` instead.

        Raises a `KeyError` if the given item is not found.

        :param item: item to search for
        :return: the Range containing the given item
        """
        return self.popitem(item)[2]

    def pop(self, item: T, default: Any = _sentinel) -> Union[V, Any]:
        """
        Returns the value corresponding to the most recently-added range that
        contains the given item. Also removes the returned value and all
        ranges corresponding to it from this RangeDict.

        The argument `default` is optional, just like in python's built-in
        `dict.pop()`, if default is given, then if the item is not found,
        returns that instead.
        Otherwise, raises a `KeyError`.

        :param item: item to search for
        :param default: optionally, a value to return, if item is not found
            (if not provided, raises a KeyError if not found)
        :return: the value corrsponding to the item, or default if item is not found
        """
        try:
            return self.popitem(item)[3]
        except KeyError:
            if default != RangeDict._sentinel:
                return default
            raise

    def popvalue(self, value: V) -> List[RangeSet]:
        """
        Removes all ranges corresponding to the given value from this RangeDict,
        as well as the value itself. Returns a list of all the RangeSets of
        various types that corresponded to the given value.

        :param value: value to purge
        :return: all RangeSets in this RangeDict that correspond to the given value
        """
        # find a RangeSet corresponding to the value, which we can use as a key
        sample_item = self._values[value][0]
        # use that RangeSet to do the regular pop() function
        return self.popitem(sample_item)[0]

    def popempty(self) -> None:
        """
        Removes all empty ranges from this RangeDict, as well as all values
        that have no corresponding ranges. The RangeDict calls this method on
        itself after most operations that modify it, so calling it manually,
        while possible, will usually do nothing.
        """
        # We start by traversing _ranges and removing all empty things.
        rngsetlistnode = self._rangesets.first
        while rngsetlistnode:
            # rngsetlistnode is a Node(_LinkedList((RangeSet, value)))
            rngsetnode = rngsetlistnode.value.first
            # First, empty all RangeSets
            while rngsetnode:
                # rngsetnode is a Node((RangeSet, value))
                rngset = rngsetnode.value[0]
                # popempty() on the RangeSet in rngsetnode
                rngset.popempty()
                # if the RangeSet is empty, then remove it.
                if rngset.isempty():
                    rngsetlistnode.value.pop_node(rngsetnode)
                    # also remove this RangeSet from .values()
                    self._values[rngsetnode.value[1]].remove(rngset)
                # deletion while traversing is fine in a linked list only
                rngsetnode = rngsetnode.next
            # Next, check for an empty list of RangeSets
            if len(rngsetlistnode.value) == 0:
                self._rangesets.pop_node(rngsetlistnode)
                # in this case, there are no RangeSets to pop, so we can leave ._values alone
            # and finally, advance to the next list of RangeSets
            rngsetlistnode = rngsetlistnode.next
        # Once we've removed all RangeSets, we then remove all values with no corresponding Range-like objects
        for value in list(self._values.keys()):
            if not self._values[value]:
                self._values.pop(value)

    def remove(self, rng: Rangelike):
        """
        Removes the given Range or RangeSet from this RangeDict, leaving behind
        'empty space'.

        Afterwards, empty ranges, and values with no remaining corresponding
        ranges, will be automatically removed.

        :param rng: Range to remove as rangekeys from this dict
        """
        # no mutation unless the operation is successful
        rng = RangeSet(rng)
        temp = self.copy()
        # do the removal on the copy
        for rngsetlist in temp._rangesets:
            for rngset, value in rngsetlist:
                try:
                    rngset.discard(rng)
                except TypeError:
                    break
        temp.popempty()
        self._rangesets, self._values = temp._rangesets, temp._values

    def isempty(self) -> bool:
        """
        :return: `True` if this RangeDict contains no values, and `False` otherwise.
        """
        return not self._values

    def ranges(self) -> List[RangeSet]:
        """
        Returns a list of RangeSets that correspond to some value in this
        RangeDict, ordered as follows:

          All Rangesets of comparable types are grouped together, with
          order corresponding to the order in which the first RangeSet of
          the given type was added to this RangeDict (earliest first).
          Within each such group, RangeSets are ordered in increasing order
          of their lower bounds.

        This function is analagous to Python's built-in `dict.keys()`

        :return: a list of RangeSet keys in this RangeDict
        """
        return [rngset for rngsetlist in self._rangesets for rngset, value in rngsetlist]

    def values(self) -> List[V]:
        """
        Returns a list of values that are corresponded to by some RangeSet in
        this RangeDict, ordered by how recently they were added (via .`add()`
        or `.update()`) or set (via `.set()` or `.setvalue()`), with the
        oldest values being listed first.

        This function is synonymous to Python's built-in `dict.values()`

        :return: a list of values contained in this RangeDict
        """
        return list(self._values.keys())

    def items(self) -> List[Tuple[Any, Any]]:
        """
        :return: a list of 2-tuples `(list of ranges corresponding to value, value)`, ordered
            by time-of-insertion of the values (see `.values()` for more detail)
        """
        return [(rngsets, value) for value, rngsets in self._values.items()]

    def clear(self) -> None:
        """
        Removes all items from this RangeDict, including all of the Ranges
        that serve as keys, and the values to which they correspond.
        """
        self._rangesets = _LinkedList()
        self._values = {}

    def copy(self) -> 'RangeDict':
        """
        :return: a shallow copy of this RangeDict
        """
        return RangeDict(self)

    def _sort_ranges(self) -> None:
        """ Helper method to gnomesort all _LinkedLists-of-RangeSets. """
        for linkedlist in self._rangesets:
            linkedlist.gnomesort()

    def _coalesce_infinite_ranges(self) -> None:
        """
        Helper method, intended for internal use only
        If any element of _rangesets ends up equal to Range(-inf, inf) due to some weird
        addition operation, then sorts that infinite range to the end of _rangesets.
        """
        def __condition(rngsets):
            return len(rngsets) == 1 and all(rngset.containseverything() for rngset, _ in rngsets)
        if any(__condition(r) for r in self._rangesets):
            self._rangesets = _LinkedList(
                [r for r in self._rangesets if not __condition(r)] + [r for r in self._rangesets if __condition(r)]
            )

    def __setitem__(self, key: Rangelike, value: V):
        """
        Equivalent to :func:`~RangeDict.add`.
        """
        self.add(key, value)

    def __getitem__(self, item: T):
        """
        Equivalent to :func:`~RangeDict.get`. If `item` is a range, then this will only
        return a corresponding value if `item` is completely contained by one
        of this RangeDict's rangekeys. To get values corresponding to all
        overlapping ranges, use `.getoverlap(item)` instead.
        """
        return self.get(item)

    def __contains__(self, item: T):
        """
        :return: True if the given item corresponds to any single value in this RangeDict, False otherwise
        """
        sentinel2 = object()
        return not (self.get(item, sentinel2) is sentinel2)
        # return any(item in rngset for rngsetlist in self._rangesets for (rngset, value) in rngsetlist)

    def __len__(self) -> int:
        """
        Returns the number of values, not the number of unique Ranges,
        since determining how to count Ranges is Hard

        :return: the number of unique values contained in this RangeDict
        """
        return len(self._values)

    def __eq__(self, other: 'RangeDict') -> bool:
        """
        Tests whether this RangeDict is equal to the given RangeDict (has the same keys and values).
        Note that this always tests equality for values, not identity, regardless of whether this
        RangeDict was constructed in 'strict' mode.

        :param other: RangeDict to compare against
        :return: True if this RangeDict is equal to the given RangeDict, False otherwise
        """
        # Actually comparing two LinkedLists together is hard, and all relevant information should be in _values anyway
        # Ordering is the big challenge here - you can't order the nested LinkedLists.
        # But what's important for equality between RangeDicts is that they have the same key-value pairs, which is
        #   properly checked just by comparing _values
        return isinstance(other, RangeDict) and self._values == other._values  # and self._rangesets == other._rangesets

    def __ne__(self, other: 'RangeDict') -> bool:
        """
        :param other: RangeDict to compare against
        :return: False if this RangeDict is equal to the given RangeDict, True otherwise
        """
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        """
        :return: False if this RangeDict is empty, True otherwise
        """
        return not self.isempty()

    def __str__(self):
        # nested f-strings, whee
        return f"""{{{
            ', '.join(
                f"{{{', '.join(str(rng) for rngset in rngsets for rng in rngset)}}}: {value}"
                for value, rngsets in self._values.items()
            )
        }}}"""

    def __repr__(self):
        return f"""RangeDict{{{
        ', '.join(
            f"RangeSet{{{', '.join(repr(rng) for rngset in rngsets for rng in rngset)}}}: {repr(value)}"
            for value, rngsets in self._values.items()
        )
        }}}"""
