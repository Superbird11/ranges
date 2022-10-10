from contextlib import suppress
import re
from ._helper import _InfiniteValue, Inf, Rangelike, RangelikeString
import ranges  # avoid circular imports by explicitly referring to ranges.RangeSet when needed
from typing import Any, TypeVar, Union


T = TypeVar('T', bound=Any)
_sentinel = object()


class Range:
    """ Range(self, *args)
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

        4. From the keyword arguments `start` and/or `end`.
          `start` and `end`
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

    start: T
    end: T
    include_start: bool
    include_end: bool

    def __init__(self, *args: Union['Range', RangelikeString, T],
                 start: T = _sentinel, end: T = _sentinel,
                 include_start: bool = True, include_end: bool = False):
        """ __init__(self, *args)
        Constructs a new Range from `start` to `end`, or from an existing range.
        Is inclusive on the lower bound and exclusive on the upper bound by
        default, but can be made differently exclusive by setting the
        keywords `include_start` and `include_end` to `True` or `False`.

        Can be called in the fallowing ways:
        >>> Range(2, 5)  # two arguments, start and end respectively
        >>> Range('[2..5)')  # one argument, of type String - resolves to a numeric range. Use '..' or ',' as separator
        >>> Range(Range(2, 5))  # one argument, of type Range - copies the given Range
        >>> Range(start=2, end=5)  # keyword arguments specify start and end. If not given, they default to -Inf/Inf
        >>> Range()  # no arguments - infinite bounds by default

        If using the constructor `Range('[2, 5)')`, then the created range
        will be numeric. Otherwise, the Range may be of any comparable
        type - numbers, strings, datetimes, etc. The default Infinite
        bounds will safely compare with any type, even if that type would
        not normally be comparable.

        Positional arguments for `start` and `end` will take priority over
        keyword arguments for `start` and `end`, if both are present.

        Additionally, the kwargs `include_start` and `include_end` may be
        given to toggle the exclusivity of either end of the range. By
        default, `include_start = True` and `include_end = False`. If
        using the constructor `Range('[2, 5)')`, the type of bracket
        on either end indicates exclusivity - square bracket is inclusive
        and circle bracket is exclusive. This will take priority over the
        keyword arguments, if given.
        """
        # process kwargs
        start = _InfiniteValue(negative=True) if start is _sentinel else start
        end = _InfiniteValue(negative=False) if end is _sentinel else end
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

    def isdisjoint(self, rng: Rangelike) -> bool:
        """
        returns `False` if this range overlaps with the given range,
        and `True` otherwise.

        :param rng: range to check disjointness with
        :return: False if this range overlaps with the given range, True otherwise
        """
        # if RangeSet, return that instead
        if isinstance(rng, ranges.RangeSet):
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

    def union(self, rng: Rangelike) -> Union[Rangelike, None]:
        """
        If this Range and the given Range overlap, then returns a Range that
        encompasses both of them.

        Returns `None` if the ranges don't overlap (if you need to, you can
        simply put both this Range and the given Range into a ranges.RangeSet).

        If the given range is actually a ranges.RangeSet, then returns a ranges.RangeSet.

        :param rng: range to find union with
        :return: A rangelike containing the union of this and the given rangelike, if they overlap or the given
            rangelike is a RangeSet.
        """
        # if RangeSet, return union of that instead
        if isinstance(rng, ranges.RangeSet):
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

    def intersection(self, rng: Rangelike) -> Union[Rangelike, None]:
        """
        Returns a range representing the intersection between this range and
        the given range, or `None` if the ranges don't overlap at all.

        If the given range is actually a ranges.RangeSet, then returns a ranges.RangeSet.

        :param rng: range to find intersection with
        :return: a rangelike containing the intersection between this and the given rangelike
        """
        # if a RangeSet, then return the intersection of that with this instead.
        if isinstance(rng, ranges.RangeSet):
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

    def difference(self, rng: Rangelike) -> Union[Rangelike, None]:
        """
        Returns a range containing all elements of this range that are not
        within the other range, or `None` if this range is entirely consumed
        by the other range.

        If the other range is empty, or if this Range is entirely disjoint
        with it, then returns this Range (not a copy of this Range).

        If the other range is entirely consumed by this range, then returns
        a ranges.RangeSet containing `(lower_part, higher_part)`.

        If the given range is actually a ranges.RangeSet, then returns a ranges.RangeSet
        no matter what.

        :param rng: rangelike to find the difference with
        :return: a rangelike containing the difference between this and the given rangelike
        """
        # if a RangeSet, then return the intersection of one of those with this instead.
        if isinstance(rng, ranges.RangeSet):
            return ranges.RangeSet(self).difference(rng)
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
                return ranges.RangeSet(lower, upper)
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

    def symmetric_difference(self, rng: Rangelike) -> Union[Rangelike, None]:
        """
        Returns a Range (if possible) or ranges.RangeSet (if not) of ranges
        comprising the parts of this Range and the given Range that
        do not overlap.

        Returns `None` if the ranges overlap exactly (i.e. the symmetric
        difference is empty).

        If the given range is actually a ranges.RangeSet, then returns a ranges.RangeSet
        no matter what.

        :param rng: rangelike object to find the symmetric difference with
        :return: a rangelike object containing the symmetric difference between this and the given rangelike
        """
        # if a RangeSet, then return the symmetric difference of one of those with this instead.
        if isinstance(rng, ranges.RangeSet):
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
        if isinstance(diff_a, ranges.RangeSet):
            # diffA has 2 elements, therefore diffB has 0 elements, e.g. (1,4) ^ (2,3) -> {(1,2], [3,4)}
            return diff_a
        elif isinstance(diff_b, ranges.RangeSet):
            # diffB has 2 elements, therefore diffA has 0 elements, e.g. (2,3) ^ (1,4) -> {(1,2], [3,4)}
            return diff_b
        elif diff_a is not None and diff_b is not None:
            # diffA has 1 element, diffB has 1 element, e.g. (1,3) ^ (2,4) -> {(1,2], [3,4)}
            return ranges.RangeSet(diff_a, diff_b)
        elif diff_a is not None:
            # diffA has 1 element, diffB has 0 elements, e.g. (1,4) ^ (1,2) -> [2,4)
            return diff_a
        else:
            # diffA has 0 elements, diffB has 1 element, e.g. (3,4) ^ (1,4) -> (1,3]
            return diff_b

    def complement(self) -> 'ranges.RangeSet':
        """
        Returns a RangeSet containing all items not present in this Range

        :return: the complement of this Range
        """
        return ranges.RangeSet(Range()) - self

    def clamp(self, value: T) -> T:
        """
        If this Range includes the given value, then return the value. Otherwise, return whichever
        bound is closest to the value.

        :param value: value to restrict to the borders of this range
        :return: the given value if it is in the range, or whichever border is closest to the value otherwise
        """
        if value in self:
            return value
        elif value >= self.end:
            return self.end
        elif value <= self.start:
            return self.start
        else:
            raise ValueError("Cannot clamp() the given value to this range")

    def isempty(self) -> bool:
        """
        Returns `True` if this range is empty (it contains no values), and
        `False` otherwise.

        In essence, will only return `True` if `start == end` and either end
        is exclusive.

        :return: True if this range contains no values. False otherwise
        """
        return self.start == self.end and (not self.include_start or not self.include_end)

    def copy(self) -> 'Range':
        """
        Copies this range, without modifying it.

        :return: a copy of this object, identical to calling `Range(self)`
        """
        return Range(self)

    def length(self) -> Union[T, Any]:
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

        :return: `end` - `start` for this range
        """
        # try normally
        with suppress(TypeError, ArithmeticError, ValueError):
            return self.end - self.start

        if not isinstance(self.start, self.end.__class__):
            # try one-way conversion
            with suppress(TypeError, ArithmeticError, ValueError):
                return self.end - self.end.__class__(self.start)
            # try the other-way conversion
            with suppress(TypeError, ArithmeticError, ValueError):
                return self.start.__class__(self.end) - self.start

        raise TypeError(f"Range of {self.start.__class__} to {self.end.__class__} has no defined length")

    def isinfinite(self) -> bool:
        """
        Returns True if this Range has a negative bound equal to -Inf or a positive bound equal to +Inf

        :return True if this Range has a negative bound equal to -Inf or a positive bound equal to +Inf
        """
        return self.start == -Inf or self.end == Inf

    def _above_start(self, item: Union['Range', T]) -> bool:
        """
        Returns True if the given item is greater than or equal to this Range's start,
        depending on whether this Range is set to include the start.
        If the given item is a Range, tests that range's .start.

        :param item: item to test against start
        :return: True if the given item is greater than or equal to this Range's start
        """
        if isinstance(item, Range):
            if self.include_start or self.include_start == item.include_start:
                return item.start >= self.start
            else:
                return item.start > self.start
        if self.include_start:
            return item >= self.start
        else:
            return item > self.start

    def _below_end(self, item: Union['Range', T]) -> bool:
        """
        Returns True if the given item is less than or equal to this Range's end,
        depending on whether this Range is set to include the end.
        If the given item is a Range, tests that range's .end.

        :param item: item to test against end
        :return: True if the given item is less than or equal to this Range's end
        """
        if isinstance(item, Range):
            if self.include_end or self.include_end == item.include_end:
                return item.end <= self.end
            else:
                return item.end < self.end
        if self.include_end:
            return item <= self.end
        else:
            return item < self.end

    def __eq__(self, obj: Rangelike) -> bool:
        """
        Compares the start and end of this range to the other range, along with
        inclusivity at either end. Returns `True` if everything is the same, or
        `False` otherwise. If the other object is a RangeSet, uses the other object's
        __eq__() instead. Always returns False if the other object is not rangelike.

        :return: True if the given object is equal to this Range.
        """
        if isinstance(obj, ranges.RangeSet):
            return obj == self
        try:
            if not isinstance(obj, Range):
                obj = Range(obj)
            return (self.start, self.end, self.include_start, self.include_end) == \
                   (obj.start, obj.end, obj.include_start, obj.include_end)
        except (AttributeError, ValueError):
            return False

    def __lt__(self, obj: Rangelike) -> bool:
        """
        Used for ordering, not for subranging/subsetting. Compares attributes in
        the following order, returning True/False accordingly:
        1. start
        2. include_start (inclusive < exclusive)
        3. end
        4. include_end (exclusive < inclusive)

        :return: True if this range should be ordered before the given rangelike object, False otherwise
        """
        if isinstance(obj, ranges.RangeSet):
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

    def __gt__(self, obj: Rangelike) -> bool:
        """
        Used for ordering, not for subranging/subsetting. Compares attributes in
        the following order, returning True/False accordingly:
        1. start
        2. include_start (inclusive < exclusive)
        3. end
        4. include_end (exclusive < inclusive)

        :return: True if this range should be ordered after the given rangelike object, False otherwise
        """
        if isinstance(obj, ranges.RangeSet):
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

    def __ge__(self, obj: Rangelike) -> bool:
        """
        Used for ordering, not for subranging/subsetting. See docstrings for
        __eq__() and __gt__().

        :return: True if this range is equal to or should be ordered after the given rangelike object. False otherwise.
        """
        return self > obj or self == obj

    def __le__(self, obj: Rangelike) -> bool:
        """
        Used for ordering, not for subranging/subsetting. See docstrings for
        __eq__() and __lt__().

        :return: True if this range is equal to or should be ordered before the given rangelike object. False otherwise.
        """
        return self < obj or self == obj

    def __ne__(self, obj: Rangelike) -> bool:
        """
        See docstring for __eq__(). Returns the opposite of that.

        :return: False if this range is equal to the given rangelike object. True otherwise.
        """
        return not self == obj

    def __or__(self, other: Rangelike) -> Union[Rangelike, None]:
        """
        Equivalent to self.union(other)

        :param other: rangelike to union
        :return: a rangelike object containing both this range and the given rangelike object
        """
        return self.union(other)

    def __and__(self, other: Rangelike) -> Union[Rangelike, None]:
        """
        Equivalent to self.intersect(other)

        :param other: rangelike to intersect
        :return: a rangelike object containing the overlap between this range and the given rangelike object
        """
        return self.intersection(other)

    def __sub__(self, other: Rangelike) -> Union[Rangelike, None]:
        """
        Equivalent to self.difference(other)

        :param other: rangelike to find difference with
        :return: a rangelike object containing everything in this range but not in the given rangelike object
        """
        return self.difference(other)

    def __xor__(self, other: Rangelike) -> Union[Rangelike, None]:
        """
        Equivalent to self.symmetric_difference(other)

        :param other: rangelike to find symmetric difference with
        :return: a rangelike object containing everything in either this range or the given rangelike, but not both
        """
        return self.symmetric_difference(other)

    def __invert__(self) -> 'RangeSet':
        """
        Equivalent to self.complement()

        :return: a RangeSet containing everything that is not in this Range
        """
        return self.complement()

    def __contains__(self, item: T) -> bool:
        """
        Returns `True` if the given item is inside the bounds of this range,
        `False` if it isn't.

        If the given item isn't comparable to this object's start and end
        objects, then tries to convert the item to a Range, and returns
        `True` if it is completely contained within this range, `False`
        if it isn't.

        A Range always contains itself.

        :param item: item to check if is contained
        :return: True if the item is within the bounds of this range. False otherwise
        """
        if self == item:
            return True
        if isinstance(item, ranges.RangeSet):
            return all(rng in self for rng in item.ranges())
        else:
            try:
                return self._above_start(item) and self._below_end(item)
            except TypeError:
                with suppress(ValueError):
                    rng_item = Range(item)
                    return rng_item.start in self and rng_item.end in self
                raise TypeError(f"'{item}' is not comparable with this Range's start and end")

    def __hash__(self):
        return hash((self.start, self.end, self.include_start, self.include_end))

    def __str__(self):
        return f"{'[' if self.include_start else '('}{str(self.start)}, " \
               f"{str(self.end)}{']' if self.include_end else ')'}"

    def __repr__(self):
        return f"Range{'[' if self.include_start else '('}{repr(self.start)}, " \
               f"{repr(self.end)}{']' if self.include_end else ')'}"

    def __bool__(self) -> bool:
        """
        :return: False if this range is empty, True otherwise
        """
        return not self.isempty()
