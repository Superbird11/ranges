import re
from collections.abc import Iterable
from ._helper import _LinkedList, _InfiniteValue, _is_iterable_non_string, Inf, _UnhashableFriendlyDict


class Range:
    """
    A class representing a range from a start value to an end value.
    The start and end need not be numeric, but they must be comparable.
    A Range is immutable, but not strictly so - nevertheless, it should
    not be modified directly.

    A new Range can be constructed in several ways:

        1. From an existing `Range` object

          >>> a = Range()   # range from -infinity to +infinity (see point #4 for how "infinity" works here)
          >>> b = Range(a)  # copy of a

        2. From a string, in the format "[start, end)".

          Both '()' (exclusive) and '[]' (inclusive) are valid brackets,
          and `start` and `end` must be able to be parsed as floats.
          Brackets must be present (a ValueError will be raised if they aren't).

          Also, the condition `start <= end` must be True.

          If constructing a Range from a string, then the keyword arguments
          `include_start` and `include_end` will be ignored.

          >>> c = Range("(-3, 5.5)")  # Infers include_start and include_end to both be false
          >>> d = Range("[-3, 5.5)")  # Infers include_start to be true, include_end to be false

        3. From two positional arguments representing `start` and `end`.
          `start` and `end` may be anything so long as the condition
          `start <= end` is True and does not error. Both `start` and
          `end` must be given together as positional arguments; if only
          one is given, then the program will try to consider it as an
          iterable.

          >>> e = Range(3, 5)
          >>> f = Range(3, 5, include_start=False, include_end=True)
          >>> print(e)  # [3, 5)
          >>> print(f)  # (3, 5]

        4. From the keyword arguments `start` and/or `end`. `start` and `end`
          may be anything so long as the condition `start <= end` is True and
          does not error. If not provided, `start` is set to -infinity by
          default, and `end` is set to +infinity by default. If any of the
          other methods are used to provide start and end values for the Range,
          then these keywords will be ignored.

          >>> g = Range(start=3, end=5)  # [3, 5)
          >>> h = Range(start=3)  # [3, inf)
          >>> i = Range(end=5)  # [-inf, 5)
          >>> j = Range(start=3, end=5, include_start=False, include_end=True)  # (3, 5]

          You can also use the default infinite bounds with other types:

          >>> k = Range(start=datetime.date(1969, 10, 5))  # [1969-10-05, inf)   includes any date after 5/10/1969
          >>> l = Range(end="ni", include_end=True)  # [-inf, ni)   all strings lexicographically less than 'ni'

        When constructing a Range in any way other than via a string,
        non-numeric values may be used as arguments. This includes dates:

        >>> import datetime
        >>> m = Range(datetime.date(1478, 11, 1), datetime.date(1834, 7, 15))
        >>> print(datetime.date(1492, 8, 3) in m)  # True
        >>> print(datetime.date(1979, 8, 17) in m)  # False

        and strings (using lexicographic comparisons):

        >>> n = Range("killer", "rabbit")
        >>> print("grenade" in n)  # False
        >>> print("pin" in n)  # True
        >>> print("three" in n)  # False

        or any other comparable type.

        By default, the start of a range (`include_start`) will be inclusive,
        and the end of a range (`include_end`) will be exclusive. User-given
        values for `include_start` and `include_end` will override these
        defaults.

        The Range data structure uses a special notion of "infinity" that works
        with all types, not just numeric ones. This allows for endless ranges
        in datatypes that do not provide their own notions of infinity, such
        as datetimes. Be warned that a range constructed without arguments will
        then contain every value that can possibly be contained in a Range:

        >>> q = Range(include_end=True)
        >>> print(q)  # [-inf, inf]
        >>> print(0 in q)  # True
        >>> print(1 in q)  # True
        >>> print(-99e99 in q)  # True
        >>> print("one" in q)  # True
        >>> print(datetime.date(1975, 3, 14) in q)  # True
        >>> print(None in q)  # True

        Although, for numeric types, infinity automatically conforms to the
        mathematical infinity of IEEE 754:

        >>> print(float('nan') in q)  # False

        Mathematically, infinity and negative infinity would always be
        exclusive. However, since they are defined values in the floating-
        point standard, they follow the same rules here as any other value,
        with regard to inclusivity or exclusivity in Range objects:

        >>> r = Range(include_start=True, include_end=False)
        >>> print(r)  # [-inf, inf)
        >>> print(float('-inf') in r)  # True
        >>> print(float('inf') in r)  # False

        The Range class is hashable, meaning it can be used as the key in a
        `dict`.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructs a new Range from `start` to `end`, or from an existing range.
        Is inclusive on the lower bound and exclusive on the upper bound by
        default, but can be made differently exclusive by setting the
        keywords `include_start` and `include_end` to `True` or `False`.
        """
        # process kwargs
        start = kwargs.get('start', _InfiniteValue(negative=True))
        end = kwargs.get('end', _InfiniteValue(negative=False))
        include_start = kwargs.get('include_start', True)
        include_end = kwargs.get('include_end', False)
        self.include_start = include_start
        self.include_end = include_end
        # Check how many positional args we got, and initialize accordingly
        if len(args) == 0:
            # with 0 positional args, initialize from kwargs directly
            rng = None
        elif len(args) == 1:
            # with 1 positional arg, initialize from existing range-like object
            if not args[0] and not isinstance(args[0], Range):
                raise ValueError("Cannot take a falsey non-Range value as only positional argument")
            rng = args[0]
        else:  # len(args) >= 2:
            # with 2 positional args, initialize from given start and end values
            start = args[0]
            end = args[1]
            rng = None
        # initialize differently if given a Range vs if given a Start/End.
        if rng is not None:
            # case 1: construct from Range
            if isinstance(rng, Range):
                self.start = rng.start
                self.end = rng.end
                self.include_start = rng.include_start
                self.include_end = rng.include_end
            # case 3: construct from String
            elif isinstance(rng, str):
                pattern = r"(\[|\()\s*([^\s,]+)\s*(?:,|\.\.)\s*([^\s,]+)\s*(\]|\))"
                match = re.match(pattern, rng)
                try:
                    # check for validity of open-bracket
                    if match.group(1) == "[":
                        self.include_start = True
                    elif match.group(1) == "(":
                        self.include_start = False
                    else:
                        raise AttributeError()
                    # check for validity of close-bracket
                    if match.group(4) == "]":
                        self.include_end = True
                    elif match.group(4) == ")":
                        self.include_end = False
                    else:
                        raise AttributeError()
                    # check start and end values
                    self.start = float(match.group(2))
                    self.end = float(match.group(3))
                    if self.start.is_integer():
                        self.start = int(self.start)
                    if self.end.is_integer():
                        self.end = int(self.end)
                except (AttributeError, IndexError):
                    raise ValueError(f"Range '{rng}' was given in wrong format. Must be like '(start, end)' " +
                                     "where () means exclusive, [] means inclusive")
                except ValueError:
                    raise ValueError("start and end must be numbers")
            # removed: construct from iterable representing start/end
            else:
                raise ValueError(f"cannot construct a new Range from an object of type '{type(rng)}'")
        else:
            # case 4 or 5: construct from positional args or kwargs
            self.start = start
            self.end = end
        try:
            if self.start > self.end:  # start != float('-inf') and end != float('inf') and
                raise ValueError("start must be less than or equal to end")
        except TypeError as _:
            raise ValueError("start and end are not comparable types")
        # # if bounds are infinity, make sure those respective bounds are exclusive
        # if self.start in (float('-inf'), float('inf')):
        #     self.include_start = False
        # if self.end in (float('-inf'), float('inf')):
        #     self.include_end = False

    def isdisjoint(self, rng):
        """
        returns `False` if this range overlaps with the given range,
        and `True` otherwise.
        """
        # if RangeSet, return that instead
        if isinstance(rng, RangeSet):
            return rng.isdisjoint(self)
        # convert other range to a format we can work with
        try:
            if not isinstance(rng, Range):
                rng = Range(rng)
        except ValueError:
            raise TypeError(str(rng) + " is not Range-like")
        # detect overlap
        rng_a, rng_b = (self, rng) if self < rng else (rng, self)
        return not (
                rng_a == rng_b
                or (rng_a.end in rng_b if rng_a.end != rng_b.start else (rng_a.include_end and rng_b.include_start))
                or (rng_b.start in rng_a if rng_a.end != rng_b.start else (rng_a.include_end and rng_b.include_start))
        )

    def union(self, rng):
        """
        If this Range and the given Range overlap, then returns a Range that
        encompasses both of them.

        Returns `None` if the ranges don't overlap (if you need to, you can
        simply put both this Range and the given Range into a RangeSet).

        If the given range is actually a RangeSet, then returns a RangeSet.
        """
        # if RangeSet, return union of that instead
        if isinstance(rng, RangeSet):
            return rng.union(self)
        # convert other range to a format we can really work with
        try:
            if not isinstance(rng, Range):
                rng = Range(rng)
        except ValueError:
            raise TypeError("Cannot merge a Range with a non-Range")
        # do the ranges overlap?
        rng_a, rng_b = (self, rng) if self < rng else (rng, self)
        if rng_a.isdisjoint(rng_b) and not (rng_a.end == rng_b.start and rng_a.include_end != rng_b.include_start):
            return None
        # merge 'em
        new_start = min((rng_a.start, rng_a.include_start), (rng_b.start, rng_b.include_start),
                        key=lambda x: (x[0], not x[1]))
        new_end = max((rng_a.end, rng_a.include_end), (rng_b.end, rng_b.include_end))
        return Range(start=new_start[0], end=new_end[0], include_start=new_start[1], include_end=new_end[1])

    def intersection(self, rng):
        """
        Returns a range representing the intersection between this range and
        the given range, or `None` if the ranges don't overlap at all.

        If the given range is actually a RangeSet, then returns a RangeSet.
        """
        # if a RangeSet, then return the intersection of that with this instead.
        if isinstance(rng, RangeSet):
            return rng.intersection(self)
        # convert other range to a format we can work with
        try:
            if not isinstance(rng, Range):
                rng = Range(rng)
        except ValueError:
            raise TypeError("Cannot overlap a Range with a non-Range")
        # do the ranges overlap?
        rng_a, rng_b = (self, rng) if self < rng else (rng, self)
        if rng_a.isdisjoint(rng_b):
            return None
        # compute parameters for new intersecting range
        # new_start = rng_b.start
        # new_include_start = new_start in rng_a
        # if rng_a.end < rng_b.end:
        #     new_end = rng_a.end
        #     new_include_end = new_end in rng_b
        # else:
        #     new_end = rng_b.end
        #     new_include_end = new_end in rng_a
        new_start = max((rng_a.start, rng_a.include_start), (rng_b.start, rng_b.include_start),
                        key=lambda x: (x[0], not x[1]))
        new_end = min((rng_a.end, rng_a.include_end), (rng_b.end, rng_b.include_end))
        # create and return new range
        return Range(start=new_start[0], end=new_end[0], include_start=new_start[1], include_end=new_end[1])

    def difference(self, rng):
        """
        Returns a range containing all elements of this range that are not
        within the other range, or `None` if this range is entirely consumed
        by the other range.

        If the other range is empty, or if this Range is entirely disjoint
        with it, then returns this Range (not a copy of this Range).

        If the other range is entirely consumed by this range, then returns
        a RangeSet containing `(lower_part, higher_part)`.

        If the given range is actually a RangeSet, then returns a RangeSet
        no matter what.
        """
        # if a RangeSet, then return the intersection of one of those with this instead.
        if isinstance(rng, RangeSet):
            return RangeSet(self).difference(rng)
        # convert other range to a workable format
        try:
            if not isinstance(rng, Range):
                rng = Range(rng)
        except ValueError:
            raise TypeError("Cannot diff a Range with a non-Range")
        # completely disjoint
        if rng.isempty():
            return self
        elif self.isdisjoint(rng):
            return self
        # fully contained
        elif self in rng or self == rng:
            return None
        # fully contained (in the other direction)
        elif rng in self:
            lower = Range(start=self.start, end=rng.start,
                          include_start=self.include_start, include_end=not rng.include_start)
            upper = Range(start=rng.end, end=self.end,
                          include_start=not rng.include_end, include_end=self.include_end)
            # exclude empty ranges
            if lower.isempty():
                return upper
            elif upper.isempty():
                return lower
            else:
                return RangeSet(lower, upper)
        # lower portion of this range
        elif self < rng:
            new_rng = Range(start=self.start, end=rng.start,
                            include_start=self.include_start, include_end=not rng.include_start)
            return None if new_rng.isempty() else new_rng
        # higher portion of this range
        else:  # self > rng:
            new_rng = Range(start=rng.end, end=self.end,
                            include_start=not rng.include_end, include_end=self.include_end)
            return None if new_rng.isempty() else new_rng

    def symmetric_difference(self, rng):
        """
        Returns a Range (if possible) or RangeSet (if not) of ranges
        comprising the parts of this Range and the given Range that
        do not overlap.

        Returns `None` if the ranges overlap exactly (i.e. the symmetric
        difference is empty).

        If the given range is actually a RangeSet, then returns a RangeSet
        no matter what.
        """
        # if a RangeSet, then return the symmetric difference of one of those with this instead.
        if isinstance(rng, RangeSet):
            return rng.symmetric_difference(self)
        # convert to range so we can work with it
        try:
            if not isinstance(rng, Range):
                rng = Range(rng)
        except ValueError:
            raise TypeError("Cannot diff a Range with a non-Range")
        # if ranges are equal
        if self == rng:
            return None
        # otherwise, get differences
        diff_a = self.difference(rng)
        diff_b = rng.difference(self)
        # create dummy symmetric difference object
        if isinstance(diff_a, RangeSet):
            # diffA has 2 elements, therefore diffB has 0 elements, e.g. (1,4) ^ (2,3) -> {(1,2], [3,4)}
            return diff_a
        elif isinstance(diff_b, RangeSet):
            # diffB has 2 elements, therefore diffA has 0 elements, e.g. (2,3) ^ (1,4) -> {(1,2], [3,4)}
            return diff_b
        elif diff_a is not None and diff_b is not None:
            # diffA has 1 element, diffB has 1 element, e.g. (1,3) ^ (2,4) -> {(1,2], [3,4)}
            return RangeSet(diff_a, diff_b)
        elif diff_a is not None:
            # diffA has 1 element, diffB has 0 elements, e.g. (1,4) ^ (1,2) -> [2,4)
            return diff_a
        else:
            # diffA has 0 elements, diffB has 1 element, e.g. (3,4) ^ (1,4) -> (1,3]
            return diff_b

    def isempty(self):
        """
        Returns `True` if this range is empty (it contains no values), and
        `False` otherwise.

        In essence, will only return `True` if `start == end` and either end
        is exclusive.
        """
        return self.start == self.end and (not self.include_start or not self.include_end)

    def copy(self):
        """ Returns a copy of this object, identical to calling `Range(self)` """
        return Range(self)

    def length(self):
        """
        Returns the size of this range (`end - start`), irrespective of whether
        either end is inclusive.

        If end and start are different types and are not naturally compatible
        for subtraction (e.g. `float` and `Decimal`), then first tries to
        coerce `start` to `end`'s class, and if that doesn't work then tries
        to coerce `end` to `start`'s class.

        Raises a `TypeError` if start and end are the same and not compatible
        for subtraction, or if type coercion fails.

        Custom types used as Range endpoints are expected to raise `TypeError`,
        `ArithmeticError`, or `ValueError` on failed subtraction. If not,
        whatever exception they raise will improperly handled by this method,
        and will thus be raised instead.
        """
        # try normally
        try:
            return self.end - self.start
        except (TypeError, ArithmeticError, ValueError) as _:
            pass
        if not isinstance(self.start, self.end.__class__):
            # try one-way conversion
            try:
                return self.end - self.end.__class__(self.start)
            except (TypeError, ArithmeticError, ValueError) as _:
                pass
            # try the other-way conversion
            try:
                return self.start.__class__(self.end) - self.start
            except (TypeError, ArithmeticError, ValueError) as _:
                pass
        raise TypeError(f"Range of {self.start.__class__} to {self.end.__class__} has no defined length")

    def isinfinite(self):
        """
        Returns True if this Range has a negative bound of -Inf or a positive bound of +Inf
        """
        return self.start == -Inf or self.end == Inf

    def _above_start(self, item):
        if isinstance(item, Range):
            if self.include_start or self.include_start == item.include_start:
                return item.start >= self.start
            else:
                return item.start > self.start
        if self.include_start:
            return item >= self.start
        else:
            return item > self.start

    def _below_end(self, item):
        if isinstance(item, Range):
            if self.include_end or self.include_end == item.include_end:
                return item.end <= self.end
            else:
                return item.end < self.end
        if self.include_end:
            return item <= self.end
        else:
            return item < self.end

    def __eq__(self, obj):
        """
        Compares the start and end of this range to the other range, along with
        inclusivity ateither end. Returns `True` if everything is the same, or
        `False` otherwise.
        """
        if isinstance(obj, RangeSet):
            return obj == self
        try:
            return (self.start, self.end, self.include_start, self.include_end) == \
                   (obj.start, obj.end, obj.include_start, obj.include_end)
        except AttributeError:
            return False

    def __lt__(self, obj):
        """
        Used for ordering, not for subranging/subsetting. Compares attributes in
        the following order, returning True/False accordingly:
        1. start
        2. include_start (inclusive < exclusive)
        3. end
        4. include_end (exclusive < inclusive)
        """
        if isinstance(obj, RangeSet):
            return obj > self
        try:
            if not isinstance(obj, Range):
                obj = Range(obj)
            return (self.start, not self.include_start, self.end, self.include_end) < \
                   (obj.start, not obj.include_start, obj.end, obj.include_end)
        except (AttributeError, ValueError, TypeError):
            if isinstance(obj, Range):
                raise TypeError("'<' not supported between "
                                f"'Range({self.start.__class__.__name__}, {self.end.__class__.__name__})' and "
                                f"'Range({obj.start.__class__.__name__}, {obj.end.__class__.__name__})'")
            else:
                raise TypeError("'<' not supported between instances of "
                                f"'{self.__class__.__name__}' and '{obj.__class__.__name__}'")

    def __gt__(self, obj):
        """
        Used for ordering, not for subranging/subsetting. Compares attributes in
        the following order, returning True/False accordingly:
        1. start
        2. include_start (inclusive < exclusive)
        3. end
        4. include_end (exclusive < inclusive)
        """
        if isinstance(obj, RangeSet):
            return obj < self
        try:
            if not isinstance(obj, Range):
                obj = Range(obj)
            return (self.start, not self.include_start, self.end, self.include_end) > \
                   (obj.start, not obj.include_start, obj.end, obj.include_end)
        except (AttributeError, ValueError, TypeError):
            if isinstance(obj, Range):
                raise TypeError("'<' not supported between "
                                f"'Range({self.start.__class__.__name__}, {self.end.__class__.__name__})' and "
                                f"'Range({obj.start.__class__.__name__}, {obj.end.__class__.__name__})'")
            else:
                raise TypeError("'<' not supported between instances of "
                                f"'{self.__class__.__name__}' and '{obj.__class__.__name__}'")

    def __ge__(self, obj):
        """
        Used for ordering, not for subranging/subsetting. See docstrings for
        __eq__() and __gt__().
        """
        return self > obj or self == obj

    def __le__(self, obj):
        """
        Used for ordering, not for subranging/subsetting. See docstrings for
        __eq__() and __lt__().
        """
        return self < obj or self == obj

    def __ne__(self, obj):
        """
        See docstring for __eq__(). Returns the opposite of that.
        """
        return not self == obj

    def __or__(self, other):
        """
        Equivalent to self.union(other)
        """
        return self.union(other)

    def __and__(self, other):
        return self.intersection(other)

    def __sub__(self, other):
        """
        Equivalent to self.difference(other)
        """
        return self.difference(other)

    def __xor__(self, other):
        """
        Equivalent to self.symmetric_difference(other)
        """
        return self.symmetric_difference(other)

    def __contains__(self, item):
        """
        Returns `True` if the given item is inside the bounds of this range,
        `False` if it isn't.

        If the given item isn't comparable to this object's start and end
        objects, then tries to convert the item to a Range, and returns
        `True` if it is completely contained within this range, `False`
        if it isn't.

        A Range always contains itself.
        """
        if self == item:
            return True
        if isinstance(item, RangeSet):
            return all(rng in self for rng in item.ranges())
        else:
            try:
                return self._above_start(item) and self._below_end(item)
            except TypeError:
                try:
                    rng_item = Range(item)
                    return rng_item.start in self and rng_item.end in self
                except ValueError:
                    pass
                raise TypeError(f"'{item}' is not comparable with this Range's start and end")

    def __hash__(self):
        return hash((self.start, self.end, self.include_start, self.include_end))

    def __str__(self):
        return f"{'[' if self.include_start else '('}{str(self.start)}, " \
               f"{str(self.end)}{']' if self.include_end else ')'}"

    def __repr__(self):
        return f"Range{'[' if self.include_start else '('}{repr(self.start)}, " \
               f"{repr(self.end)}{']' if self.include_end else ')'}"

    def __bool__(self):
        return not self.isempty()


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
    def __init__(self, *args):
        """
        Constructs a new RangeSet containing the given sub-ranges.
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

    def add(self, rng):
        """
        Adds a copy of the given range or RangeSet to this RangeSet.

        If the argument is not Range-like and is not a RangeSet, then
        a `ValueError` will be raised. If the argument is not comparable
        to other Ranges contained in this RangeSet, then a `TypeError`
        will be raised. If an iterable is given as the
        argument, it will be submitted to the `Range()` constructor.

        To add all ranges in an iterable containing multiple ranges,
        use `.extend()` instead.
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

    def extend(self, iterable):
        """
        Adds a copy of each Range or RangeSet in the given iterable to
        this RangeSet.

        Raises a `TypeError` if the argument is not iterable.

        This method works identically to `.add()` for RangeSets only.
        """
        self._ranges = RangeSet._merge_ranges(
            self._ranges + (Range(r) for r in iterable)
        )

    def discard(self, rng):
        """
        Removes the entire contents of the given RangeSet from this RangeSet.

        This method will only remove a single RangeSet (or Range) from this
        RangeSet at a time. To remove a list of Range-like objects from this
        RangeSet, use .difference_update() instead.
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

    def difference(self, rng_set):
        """
        Return a new RangeSet containing the ranges that are in this RangeSet
        but not in the other given RangeSet or list of RangeSets. This
        RangeSet is not modified in the process.
        """
        new_rng_set = self.copy()
        new_rng_set.difference_update(RangeSet(rng_set))
        return new_rng_set

    def difference_update(self, rng_set):
        """
        Removes all ranges in the given iterable from this RangeSet.

        If an error occurs while trying to do this, then this RangeSet
        remains unchanged.
        """
        self.discard(RangeSet._to_rangeset(rng_set))

    def intersection(self, rng_set):
        """
        Returns a new RangeSet containing the intersection between this
        RangeSet and the given Range or RangeSet - that is, containing
        only the elements shared between this RangeSet and the given
        RangeSet.
        """
        # convert to a RangeSet
        rng_set = RangeSet._to_rangeset(rng_set)
        # do O(n^2) difference algorithm
        # TODO rewrite to increase efficiency by short-circuiting
        intersections = [rng1.intersection(rng2) for rng1 in self._ranges for rng2 in rng_set._ranges]
        intersections = [rng for rng in intersections if rng is not None and not rng.isempty()]
        return RangeSet(intersections)

    def intersection_update(self, rng_set):
        """
        Updates this RangeSet to contain only the intersections between
        this RangeSet and the given Range or RangeSet, removing the parts
        of this RangeSet's ranges that do not overlap the given RangeSet
        """
        self._ranges = self.intersection(rng_set)._ranges

    def union(self, rng_set):
        """
        Returns a new RangeSet containing the overlap between this RangeSet and the
        given RangeSet
        """
        # convert to RangeSet
        rng_set = RangeSet._to_rangeset(rng_set)
        # simply merge lists
        return RangeSet(self._ranges + rng_set._ranges)

    def update(self, rng_set):
        """
        Updates this RangeSet to add all the ranges in the given RangeSet, so
        that this RangeSet now contains the union of its old self and the
        given RangeSet.
        """
        # convert to RangeSet
        rng_set = RangeSet._to_rangeset(rng_set)
        # merge lists
        self._ranges = RangeSet._merge_ranges(self._ranges + rng_set._ranges)

    def symmetric_difference(self, rng_set):
        """
        Returns a new RangeSet containing the symmetric difference between this
        RangeSet  and the given Range or RangeSet - everything contained by
        this RangeSet or the given RangeSet, but not both.
        """
        # convert to a RangeSet
        rng_set = RangeSet._to_rangeset(rng_set)
        # get union and then remove intersections
        union = self.union(rng_set)
        intersection = self.intersection(rng_set)
        union.difference_update(intersection)
        return union

    def symmetric_difference_update(self, rng_set):
        """
        Update this RangeSet to contain the symmetric difference between it and
        the given Range or RangeSet, by removing the parts of the given RangeSet
        that overlap with this RangeSet from this RangeSet.
        """
        # the easiest way to do this is just to do regular symmetric_difference and then copy the result
        rng_set = RangeSet._to_rangeset(rng_set)
        self._ranges = self.symmetric_difference(rng_set)._ranges

    def isdisjoint(self, other):
        """
        Returns `True` if there is no overlap between this RangeSet and the
        given RangeSet.
        """
        # convert to RangeSet
        other = RangeSet._to_rangeset(other)
        # O(n^2) comparison
        # TODO improve efficiency by mergesort/short-circuiting
        return all(rng1.isdisjoint(rng2) for rng1 in self._ranges for rng2 in other._ranges)

    def popempty(self):
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

    def getrange(self, item):
        """
        If the given item is in this RangeSet, returns the specific Range it's
        in.

        If the given item is a RangeSet or Iterable and is partly contained in
        multiple ranges, then returns a RangeSet with only those ranges that
        contain some part of it.

        Otherwise, raises an `IndexError`.
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

    def ranges(self):
        """
        Returns a `list` of the Range objects that this RangeSet contains
        """
        return list(iter(self._ranges))

    def clear(self):
        """
        Removes all ranges from this RangeSet, leaving it empty.
        """
        self._ranges = _LinkedList()

    def isempty(self):
        """
        Returns True if this RangeSet contains no values, and False otherwise
        """
        return self._ranges.isempty() or all(r.isempty() for r in self._ranges)

    def copy(self):
        """
        returns a shallow copy of this RangeSet
        """
        return RangeSet(self)

    def isinfinite(self):
        """
        Returns True if this RangeSet has a negative bound of -Inf or a positive bound of +Inf,
        and False otherwise
        """
        return self._ranges.first.value.start == -Inf or self._ranges.last.value.end == Inf

    @staticmethod
    def _merge_ranges(ranges):
        """
        Compresses all of the ranges in the given iterable, and
        returns a _LinkedList containing them.
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
    def _to_rangeset(other):
        """
        Helper method.
        Converts the given argument to a RangeSet. This mainly exists to increase performance
        by not duplicating things that are already RangeSets, and for the sake of graceful
        error handling.
        """
        if not isinstance(other, RangeSet):
            try:
                other = RangeSet(other)
            except ValueError:
                raise ValueError(f"Cannot convert {type(other)} to a RangeSet")
        return other

    def __contains__(self, item):
        """
        Returns true if this RangeSet completely contains the given item, Range,
        RangeSet, or iterable (which will be assumed to be a RangeSet unless
        coercing it into one fails, in which case it will be assumed to be an
        item).
        Returns false otherwise.
        A RangeSet will always contain itself.
        """
        if self == item:
            return True
        try:
            if _is_iterable_non_string(item):
                try:
                    return all(
                        any(subitem in rng for rng in self._ranges)
                        for subitem in RangeSet._to_rangeset(item)
                    )
                except ValueError:
                    pass
        except TypeError:
            pass
        return any(item in rng for rng in self._ranges)

    def __eq__(self, other):
        """
        Returns True if this RangeSet's ranges exactly match the other
        RangeSet's ranges, or if the given argument is a Range and this
        RangeSet contains only one identical Range
        """
        if isinstance(other, RangeSet):
            return len(self._ranges) == len(other._ranges) and \
                   all(mine == theirs for mine, theirs in zip(self._ranges, other._ranges))
        elif isinstance(other, Range):
            return len(self._ranges) == 1 and self._ranges[0] == other
        else:
            return False

    def __lt__(self, other):
        """
        Returns an ordering-based comparison based on the lowest ranges in
        self and other.
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

    def __gt__(self, other):
        """
        Returns an ordering-based comparison based on the lowest ranges in
        self and other.
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

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __ne__(self, other):
        return not self == other

    def __and__(self, other):
        """ returns (self & other), identical to self.intersection(other) """
        return self.intersection(other)

    def __or__(self, other):
        """ returns (self | other), identical to self.union(other) """
        return self.union(other)

    def __xor__(self, other):
        """ returns (self ^ other), identical to
        self.symmetric_difference(other) """
        return self.symmetric_difference(other)

    def __sub__(self, other):
        """ returns (self - other), identical to self.difference(other) """
        return self.difference(other)

    def __add__(self, other):
        """ Returns (self + other), identical to self.union(other) """
        return self.union(other)

    def __iand__(self, other):
        """ Executes (self &= other), identical to self.intersection_update(other) """
        self.intersection_update(other)
        return self

    def __ior__(self, other):
        """ Executes (self |= other), identical to self.update(other) """
        self.update(other)
        return self

    def __ixor__(self, other):
        """ Executes (self ^= other), identical to self.symmetric_difference_update(other) """
        self.symmetric_difference_update(other)
        return self

    def __iadd__(self, other):
        """ Executes (self += other), identical to self.update(other) """
        self.update(other)
        return self

    def __isub__(self, other):
        """ Executes (self -= other), identical to self.difference_update(other) """
        self.difference_update(other)
        return self

    def __iter__(self):
        """
        Generates the ranges in this object, in order
        """
        return iter(self._ranges)

    def __hash__(self):
        return hash(tuple(iter(self._ranges)))

    def __bool__(self):
        return not self.isempty()

    def __str__(self):
        return f"{{{', '.join(str(r) for r in self._ranges)}}}"  # other possibilities: '∪', ' | '

    def __repr__(self):
        return f"RangeSet{{{', '.join(repr(r) for r in self._ranges)}}}"


class RangeDict:
    """
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
    """
    # sentinel for checking whether an arg was passed, where anything is valid including None
    _sentinel = object()

    def __init__(self, iterable=_sentinel):
        """
        Initialize a new RangeDict from the given iterable. The given iterable
        may be either a RangeDict (in which case, a copy will be created),
        a regular dict with all keys able to be converted to Ranges, or an
        iterable of 2-tuples (range, value).
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

    def add(self, rng, value):
        """
        Add the single given Range/RangeSet to correspond to the given value.
        If the given Range overlaps with a Range that is already contained
        within this RangeDict, then the new range takes precedence.

        To add multiple Ranges of the same type, pack them into a RangeSet
        and pass that.

        To add a list of multiple Ranges of different types, use `.update()`
        instead. Using this method instead will produce a `TypeError`.

        If an empty Range is given, then this method does nothing.
        """
        # copy the range and get it into an easy-to-work-with form
        try:
            rng = RangeSet(rng)
        except TypeError:
            raise TypeError("argument 'rng' for .add() must be able to be converted to a RangeSet")
        if rng.isempty():
            return
        # first, remove this range from any existing range
        short_circuit = False
        for rngsetlist in self._rangesets:
            # rngsetlist is a tuple (_LinkedList(ranges), value)
            for rngset in rngsetlist:
                # rngset
                try:
                    rngset[0].discard(rng)
                    short_circuit = True  # (naively) assume only one type of rngset will be compatible
                except TypeError:
                    pass
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
                try:
                    # ...once we find the RangeSet of the right type
                    rngset.add(rng)
                    # And then bubble it into place in whichever _LinkedList would have contained it.
                    # This is one empty list traversal for every non-modified _LinkedList, and one gnomesort
                    #   for the one we really want. A little time loss but not that much. Especially not
                    #   any extra timeloss for single-typed RangeDicts.
                    self._sort_ranges()
                    # And short-circuit, since we've already dealt with the complications and don't need to
                    #   do any further modification of _values or _rangesets
                    return
                except TypeError:
                    pass
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
            try:
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
                return
            except TypeError:
                pass
        # if no existing rangeset accepted it, then we need to add one.
        # singleton _LinkedList containing just (rng, value), appended to self._rangesets
        self._rangesets.append(_LinkedList(((rng, value),)))

    def update(self, iterable):
        """
        Adds the contents of the given iterable (either another RangeDict, a
        `dict` mapping Range-like objects to values, or a list of 2-tuples
        `(range-like, value)`) to this RangeDict.
        """
        # coerce to RangeDict and add that
        if not isinstance(iterable, RangeDict):
            iterable = RangeDict(iterable)
        for value, rangesets in iterable._values.items():
            for rngset in rangesets:
                self.add(rngset, value)

    def getitem(self, item):
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

    def getrangesets(self, item):
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns a list of all RangeSets in this RangeDict that
        correspond to that value.

        Most of the time, this will be a single-element list, if only one
        type of Range is used in the RangeDict. Otherwise, if ranges of
        multiple types (e.g. int ranges, string ranges) correspond to the
        same value, this list will contain all of them.

        Raises a `KeyError` if the given item is not found.
        """
        return self.getitem(item)[0]

    def getrangeset(self, item):
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns the RangeSet containing the given item that
        corresponds to that value.

        To find other RangeSets of other types that correspond to the same
        value, use `.getrangesets()` instead.

        Raises a `KeyError` if the given item is not found.
        """
        return self.getitem(item)[1]

    def getrange(self, item):
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns the single contiguous range containing the given item
        that corresponds to that value.

        To find the RangeSet of all Ranges that correspond to that item,
        use `.getrangeset()` instead.

        Raises a `KeyError` if the given item is not found.
        """
        return self.getitem(item)[2]

    def get(self, item, default=_sentinel):
        """
        Returns the value corresponding to the given item, based on
        the most recently-added Range containing it.

        The `default` argument is optional.
        Like Python's built-in `dict`, if `default` is given, returns that if
        `item` is not found.
        Otherwise, raises a `KeyError`.
        """
        try:
            return self.getitem(item)[3]
        except KeyError:
            if default != RangeDict._sentinel:
                return default
            raise

    def getvalue(self, value):
        """
        Returns the list of RangeSets corresponding to the given value.

        Raises a `KeyError` if the given value is not corresponded to by
        any RangeSets in this RangeDict.
        """
        try:
            return self._values[value]
        except KeyError:
            raise KeyError(f"value '{value}' is not present in this RangeDict")

    def set(self, item, new_value):
        """
        Changes the value corresponding to the given `item` to the given
        `new_value`, such that all ranges corresponding to the old value
        now correspond to the `new_value` instead.

        Returns the original, overwritten value.

        If the given item is not found, raises a `KeyError`.
        """
        try:
            old_value = self.get(item)
        except KeyError:
            raise KeyError(f"Item '{item}' is not in any Range in this RangeDict")
        self.setvalue(old_value, new_value)

    def setvalue(self, old_value, new_value):
        """
        Changes all ranges corresponding to the given `old_value` to correspond
        to the given `new_value` instead.

        Raises a `KeyError` if the given `old_value` isn't found.
        """
        try:
            rangesets = list(self._values[old_value])
        except KeyError:
            raise KeyError(f"Value '{old_value}' is not in this RangeDict")
        for rngset in rangesets:
            self.add(rngset, new_value)

    def popitem(self, item):
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

    def poprangesets(self, item):
        """
        Finds the value to which the given item corresponds, and returns the
        list of RangeSets that correspond to that value (see
        `.getrangesets()`).

        Also removes the value, and all RangeSets from this RangeDict. To
        remove just one range and leave the rest intact, use `.remove()`
        instead.

        Raises a `KeyError` if the given item is not found.
        """
        return self.popitem(item)[0]

    def poprangeset(self, item):
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns the RangeSet containing the given item that
        corresponds to that value.

        Also removes the value and all ranges that correspond to it from this
        RangeDict. To remove just one range and leave the rest intact, use
        `.remove()` instead.

        Raises a `KeyError` if the given item is not found.
        """
        return self.popitem(item)[1]

    def poprange(self, item):
        """
        Finds the value to which the given item corresponds in this RangeDict,
        and then returns the single contiguous range containing the given item
        that corresponds to that value.

        Also removes the value and all ranges that correspond to it from this
        RangeDict. To remove just one range and leave the rest intact, use
        `.remove()` instead.

        Raises a `KeyError` if the given item is not found.
        """
        return self.popitem(item)[2]

    def pop(self, item, default=_sentinel):
        """
        Returns the value corresponding to the most recently-added range that
        contains the given item. Also removes the returned value and all
        ranges corresponding to it from this RangeDict.

        The argument `default` is optional, just like in python's built-in
        `dict.pop()`, if default is given, then if the item is not found,
        returns that instead.
        Otherwise, raises a `KeyError`.
        """
        try:
            return self.popitem(item)[3]
        except KeyError:
            if default != RangeDict._sentinel:
                return default
            raise

    def popvalue(self, value):
        """
        Removes all ranges corresponding to the given value from this RangeDict,
        as well as the value itself. Returns a list of all the RangeSets of
        various types that corresponded to the given value.
        """
        # find a RangeSet corresponding to the value, which we can use as a key
        sample_item = self._values[value][0]
        # use that RangeSet to do the regular pop() function
        return self.popitem(sample_item)[0]

    def popempty(self):
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

    def remove(self, rng):
        """
        Removes the given Range or RangeSet from this RangeDict, leaving behind
        'empty space'.

        Afterwards, empty ranges, and values with no remaining corresponding
        ranges, will be automatically removed.
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

    def isempty(self):
        """
        Returns `True` if this RangeDict contains no values, and `False` otherwise.
        """
        return not self._values

    def ranges(self):
        """
        Returns a list of RangeSets that correspond to some value in this
        RangeDict, ordered as follows:

          All Rangesets of comparable types are grouped together, with
          order corresponding to the order in which the first RangeSet of
          the given type was added to this RangeDict (earliest first).
          Within each such group, RangeSets are ordered in increasing order
          of their lower bounds.

        This function is analagous to Python's built-in `dict.keys()`
        """
        return [rngset for rngsetlist in self._rangesets for rngset, value in rngsetlist]

    def values(self):
        """
        Returns a list of values that are corresponded to by some RangeSet in
        this RangeDict, ordered by how recently they were added (via .`add()`
        or `.update()`) or set (via `.set()` or `.setvalue()`), with the
        oldest values being listed first.

        This function is synonymous to Python's built-in `dict.values()`
        """
        return list(self._values.keys())

    def items(self):
        """
        Returns a list of 2-tuples `(list of ranges corresponding to value, value)`, ordered
        by time-of-insertion of the values (see `.values()` for more detail)
        """
        return [(rngsets, value) for value, rngsets in self._values.items()]

    def clear(self):
        """
        Removes all items from this RangeDict, including all of the Ranges
        that serve as keys, and the values to which they correspond.
        """
        self._rangesets = _LinkedList()
        self._values = {}

    def copy(self):
        """
        Returns a shallow copy of this RangeDict
        """
        return RangeDict(self)

    def _sort_ranges(self):
        """ Helper method to gnomesort all _LinkedLists-of-RangeSets. """
        for linkedlist in self._rangesets:
            linkedlist.gnomesort()

    def __setitem__(self, key, value):
        self.add(key, value)

    def __getitem__(self, item):
        return self.get(item)

    def __contains__(self, item):
        """
        Returns true if the given item corresponds to any single value
        in this RangeDict
        """
        sentinel2 = object()
        return not (self.get(item, sentinel2) is sentinel2)
        # return any(item in rngset for rngsetlist in self._rangesets for (rngset, value) in rngsetlist)

    def __len__(self):
        """
        Returns the number of values, not the number of unique Ranges,
        since determining how to count Ranges is Hard
        """
        return len(self._values)

    def __eq__(self, other):
        # Actually comparing two LinkedLists together is hard, and all relevant information should be in _values anyway
        # Ordering is the big challenge here - you can't order the nested LinkedLists.
        # But what's important for equality between RangeDicts is that they have the same key-value pairs, which is
        #   properly checked just by comparing _values
        return isinstance(other, RangeDict) and self._values == other._values  # and self._rangesets == other._rangesets

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
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
