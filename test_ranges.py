import pytest
from pytest import fail
from ranges import Range, RangeSet, RangeDict
import numbers
from decimal import Decimal
import datetime


def asserterror(errortype, func, args=None, kwargs=None):
    """
    A helper method - basically, "execute the given function with the given args and
    assert that it produces the correct error type.
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    try:
        func(*args, **kwargs)
        fail(f"Function {func.__name__} with args {args} and kwargs {kwargs} should have raised {errortype.__name__}")
    except errortype:
        pass

#######################################################################################################
# Tests for Range
#######################################################################################################


@pytest.mark.parametrize(
    "start,end,include_start,include_end,isempty", [
            # boundary value
            (1, 2, False, False, False),
            (0, 8.5, False, False, False),
            (-1.3, 0, False, False, False),
            (-999, 10000000, False, False, False),
            (float('-inf'), float('inf'), False, False, False),
            (1.0000000001, 1.0000000002, False, False, False),
            # inclusivity
            (9, 9, True, True, False),
            (2.5, 2.5, True, False, True),
            (-72.421642, -72.421642, False, True, True),
            (7, 7, False, False, True),
            # acceptance
            (float('inf'), float('inf'), True, True, False),
            (float('-inf'), float('-inf'), True, True, False),
            (0.3, 0.1+0.2, False, False, False),  # floating point errors tee hee hee
            (Decimal(1), Decimal(2), False, False, False),
            (Decimal(1)/Decimal(10), 0.1, False, False, False),
            ('aardvark', 'pistachio', False, False, False),
            ('bongo', 'bongo', False, False, True),
            ('bingo', 'bongo', False, False, False),
            (datetime.date(2018, 7, 2), datetime.date(2018, 7, 3), False, False, False),
            (datetime.date(2018, 7, 2), datetime.date(2018, 7, 2), False, False, True),
            (datetime.timedelta(3), datetime.timedelta(4), False, False, False),
            (datetime.time(2, 34, 7, 2154), datetime.time(2, 34, 7, 2155), False, False, False)
        ]
)
def test_range_constructor_valid(start, end, include_start, include_end, isempty):
    """
    Tests all possible permutations of the Range() constructor to make sure that they produce valid ranges.
    Also tests is_empty().
    """
    fakestart = 5 if start == 4 else 4
    fakeend = 9 if start == 8 else 8
    test_ranges = [
        (Range(start, end), {'check_include_start', 'check_include_end'}),
        (Range(start=start, end=end), {'check_include_start', 'check_include_end'}),
        (Range(start, end, include_start=include_start), {'check_include_end'}),
        (Range(start, end, include_end=include_end), {'check_include_start'}),
        (Range(start, end, include_start=include_start, include_end=include_end), {}),
        (Range(start=start, end=end, include_start=include_start), {'check_include_end'}),
        (Range(start=start, end=end, include_end=include_end), {'check_include_start'}),
        (Range(start=start, end=end, include_start=include_start, include_end=include_end), {}),
        (Range(start, end, start=fakestart, end=fakeend), {'check_include_start', 'check_include_end'}),
        (Range(start, end, start=fakestart, end=fakeend, include_start=include_start), {'check_include_end'}),
        (Range(start, end, start=fakestart, end=fakeend, include_end=include_end), {'check_include_start'}),
        (Range(start, end, start=fakestart, end=fakeend, include_start=include_start, include_end=include_end), {}),
    ]
    if isinstance(start, numbers.Number) and isinstance(end, numbers.Number):
        test_ranges += [
            (Range(start=start, include_start=include_start), {'infinite_end', 'check_include_end'}),
            (Range(start=start, include_end=include_end), {'infinite_end', 'check_include_start'}),
            (Range(start=start, include_start=include_start, include_end=include_end), {'infinite_end'}),
            (Range(end=end, include_start=include_start), {'infinite_start', 'check_include_end'}),
            (Range(end=end, include_end=include_end), {'infinite_start', 'check_include_start'}),
            (Range(end=end, include_start=include_start, include_end=include_end), {'infinite_start'}),
            (Range(start=start), {'infinite_end', 'check_include_start', 'check_include_end'}),
            (Range(end=end), {'infinite_start', 'check_include_start', 'check_include_end'}),
        ]
    numstr = ""
    if (isinstance(start, int) and isinstance(end, int)) or (isinstance(start, float) and isinstance(end, float)):
        numstr = f"{'[' if include_start else '('}{start}, {end}{']' if include_end else ')'}"
        numstr2 = numstr.replace(", ", "..")
        test_ranges += [
            (Range(numstr), {}),
            (Range(numstr, start=fakestart), {}),
            (Range(numstr, end=fakeend), {}),
            (Range(numstr, include_start=not include_start), {}),
            (Range(numstr, include_end=not include_end), {}),
            (Range(numstr, start=fakestart, end=fakeend), {}),
            (Range(numstr, start=fakestart, include_start=not include_start), {}),
            (Range(numstr, start=fakestart, include_end=not include_end), {}),
            (Range(numstr, end=fakeend, include_start=not include_start), {}),
            (Range(numstr, end=fakeend, include_end=not include_end), {}),
            (Range(numstr, include_start=not include_start, include_end=not include_end), {}),
            (Range(numstr, start=fakestart, end=fakeend, include_start=not include_start), {}),
            (Range(numstr, start=fakestart, end=fakeend, include_end=not include_end), {}),
            (Range(numstr, start=fakestart, include_start=not include_start, include_end=not include_end), {}),
            (Range(numstr, end=fakeend, include_start=not include_start, include_end=not include_end), {}),
            (Range(numstr, start=fakestart, end=fakeend, include_start=not include_start, include_end=not include_end),
                {}),
            (Range(numstr2), {}),
            (Range(numstr2, start=fakestart), {}),
            (Range(numstr2, end=fakeend), {}),
            (Range(numstr2, include_start=not include_start), {}),
            (Range(numstr2, include_end=not include_end), {}),
            (Range(numstr2, start=fakestart, end=fakeend), {}),
            (Range(numstr2, start=fakestart, include_start=not include_start), {}),
            (Range(numstr2, start=fakestart, include_end=not include_end), {}),
            (Range(numstr2, end=fakeend, include_start=not include_start), {}),
            (Range(numstr2, end=fakeend, include_end=not include_end), {}),
            (Range(numstr2, include_start=not include_start, include_end=not include_end), {}),
            (Range(numstr2, start=fakestart, end=fakeend, include_start=not include_start), {}),
            (Range(numstr2, start=fakestart, end=fakeend, include_end=not include_end), {}),
            (Range(numstr2, start=fakestart, include_start=not include_start, include_end=not include_end), {}),
            (Range(numstr2, end=fakeend, include_start=not include_start, include_end=not include_end), {}),
            (Range(numstr2, start=fakestart, end=fakeend, include_start=not include_start, include_end=not include_end),
                {}),
        ]
    for idx, test in enumerate(test_ranges):
        # print(idx, test)
        assert(test[0].start == start if 'infinite_start' not in test[1] else test[0].start == float('-inf'))
        assert(test[0].end == end if 'infinite_end' not in test[1] else test[0].end == float('inf'))
        assert(test[0].include_start == include_start
               if 'check_include_start' not in test[1] else test[0].include_start)
        assert(test[0].include_end == include_end if 'check_include_end' not in test[1] else not test[0].include_end)
        if 'check_include_start' not in test[1] and 'check_include_end' not in test[1] \
                and 'infinite_start' not in test[1] and 'infinite_end' not in test[1]:
            assert(test[0].isempty() == isempty)
            assert(bool(test[0]) != isempty)
        if (isinstance(start, int) and isinstance(end, int)) or (isinstance(start, float) and isinstance(end, float)):
            assert str(test[0] == numstr)


@pytest.mark.parametrize(
    "args,kwargs", [
        # invalid types/argument combinations
        (([1, 2], 3), {}),
        ((1, [2, 3]), {}),
        ((1,), {}),
        ((1,), {"end": 2}),
        ((1,), {"start": 0, "end": 2}),
        # bad order
        (([2, 1],), {}),
        ([datetime.timedelta(3), datetime.timedelta(2)], {}),
        (("z", "a"), {}),
        (("[2, 1]",), {}),
        (("(2, 1)",), {}),
        (([2, 1]), {}),
        ((), {"start": 2, "end": 1}),
        # non-comparable types
        ((1, "2"), {}),
        ((1, datetime.timedelta(3)), {}),
        ((1, datetime.date(3, 2, 1)), {}),
        (("1", datetime.date(3, 2, 1)), {}),
        # non-compatible types w.r.t. default arguments
        # note: this is no longer a valid concern, since _InfiniteValue was implemented
        # ((), {"start": datetime.timedelta(3)}),
        # ((), {"start": "-inf"}),
        # ((), {"end": datetime.date(3, 2, 1)}),
        # ((), {"end": "inf"}),
        # invalid string formats
        (("1, 2",), {}),
        (("1",), {}),
        (("[]",), {}),
        (("",), {}),
        (("{1, 2}",), {}),
        (("(1 2)",), {}),
        (("(one, two)",), {}),
        (("[1, 2",), {}),
    ]
)
def test_range_constructor_invalid(args, kwargs):
    """ Tests invalid calls to `Range.__init__()`, asserting that they yield the correct error. """
    asserterror(ValueError, Range, args, kwargs)


@pytest.mark.parametrize(
    "rng, item, contains, strr, reprr", [
        (Range(1, 2), 1, True, "[1, 2)", "Range[1, 2)"),
        (Range(1, 2), 2, False, "[1, 2)", "Range[1, 2)"),
        (Range(1, 2), 1.5, True, "[1, 2)", "Range[1, 2)"),
        (Range("(0.3, 0.4)"), 0.1+0.2, True, "(0.3, 0.4)", "Range(0.3, 0.4)"),
        (Range("(0.3, 0.4)"), 0.3, False, "(0.3, 0.4)", "Range(0.3, 0.4)"),
        (Range(), 99e99, True, "[-inf, inf)", "Range[-inf, inf)"),
        (Range(), -99e99, True, "[-inf, inf)", "Range[-inf, inf)"),
        (Range(), float('inf'), False, "[-inf, inf)", "Range[-inf, inf)"),  # inclusive Infinity is deliberate
        (Range(include_end=True), float('inf'), True, "[-inf, inf]", "Range[-inf, inf]"),  # (see IEEE 754)
        (Range(-3, 3), Range(1, 2), True, "[-3, 3)", "Range[-3, 3)"),
        (Range(-3, 3), Range(1, 3), False, "[-3, 3)", "Range[-3, 3)"),
        (Range(-3, 3), Range(-4, 4), False, "[-3, 3)", "Range[-3, 3)"),
        (Range(-3, 3), Range(-3, -2), True, "[-3, 3)", "Range[-3, 3)"),
        (Range(), float('nan'), False, "[-inf, inf)", "Range[-inf, inf)"),
        (Range(datetime.date(2017, 5, 27), datetime.date(2018, 2, 2)), datetime.date(2017, 12, 1), True,
            "[2017-05-27, 2018-02-02)", "Range[datetime.date(2017, 5, 27), datetime.date(2018, 2, 2))"),
        (Range(datetime.date(2017, 5, 27), datetime.date(2018, 2, 2), include_end=True), datetime.date(2018, 12, 1),
            False, "[2017-05-27, 2018-02-02]", "Range[datetime.date(2017, 5, 27), datetime.date(2018, 2, 2)]"),
        (Range(datetime.timedelta(0, 3600), datetime.timedelta(0, 7200)), datetime.timedelta(0, 6000), True,
            "[1:00:00, 2:00:00)", "Range[datetime.timedelta(seconds=3600), datetime.timedelta(seconds=7200))"),
        (Range(datetime.timedelta(1, 1804), datetime.timedelta(3)), datetime.timedelta(1), False,
            "[1 day, 0:30:04, 3 days, 0:00:00)",
            "Range[datetime.timedelta(days=1, seconds=1804), datetime.timedelta(days=3))"),
        (Range("begin", "end"), "middle", False, "[begin, end)", "Range['begin', 'end')"),
        (Range("begin", "end"), "cows", True, "[begin, end)", "Range['begin', 'end')"),
        # RangeSets
        (Range(1, 10), RangeSet(Range(2, 9)), True, "[1, 10)", "Range[1, 10)"),
        (Range(1, 10), RangeSet(Range(2, 3), Range(4, 5), Range(6, 7), Range(8, 9)), True, "[1, 10)", "Range[1, 10)"),
        (Range(1, 10), RangeSet(Range(0, 11)), False, "[1, 10)", "Range[1, 10)"),
        (Range(1, 4), RangeSet(Range(2, 3), Range(5, 6)), False, "[1, 4)", "Range[1, 4)"),
    ]
)
def test_range_contains(rng, item, contains, strr, reprr):
    """
    Tests the __contains__, __str__, __repr__, and __hash__ methods of the range.
    """
    assert(contains == (item in rng))
    assert(strr == str(rng))
    assert(reprr == repr(rng))
    assert(hash(rng) == hash(rng.copy()))
    assert(rng in rng)


@pytest.mark.parametrize(
    "lesser,greater,equal", [
        (Range(), Range(), True),
        (Range(1, 2), Range("[1, 2)"), True),
        (Range(1, 2), Range(1, 2, include_end=True), False),
        (Range(1, 2, include_start=True), Range(1, 2, include_start=False), False),
        (Range(), Range(1, 2), False),
        (Range(1, 4), Range(2, 3), False),
        (Range(1, 3), Range(2, 4), False),
    ]
)
def test_range_comparisons(lesser, greater, equal):
    """
    Tests the comparison operators (<, >, etc.) on the Range class
    """
    assert(equal == (lesser == greater))
    assert(equal != (lesser != greater))
    assert(lesser <= greater)
    assert(equal != (lesser < greater))
    assert(not (greater < lesser))
    assert(equal != (greater > lesser))
    assert(not (lesser > greater))
    assert(greater >= lesser)
    pass


@pytest.mark.parametrize(
    "rng1,rng2,isdisjoint,error_type", [
        # proper test cases
        (Range(1, 3), Range(2, 4), False, None),
        (Range(1, 3), Range(4, 6), True, None),
        (Range(1, 3), Range(3, 5), True, None),
        (Range(1, 3), "[3, 5)", True, "r2"),
        (Range(1, 4), Range(2, 3), False, None),
        (Range(1, 3, include_end=True), Range(3, 5,), False, None),
        (Range(), Range(1, 3), False, None),
        # RangeSets
        (Range(1, 4), RangeSet(), True, None),
        (Range(2, 4), RangeSet(Range(0, 1), Range(5, 6)), True, None),
        (Range(2, 4), RangeSet(Range(1, 3)), False, None),
        (Range(2, 4), RangeSet(Range(1, 3), Range(5, 6)), False, None),
        # errors
        (Range(1, 3), Range("apple", "banana"), None, TypeError),
        (Range(1, 3), "2, 4", False, TypeError),
        (Range(1, 3), 2, False, TypeError),
    ]
)
def test_range_isdisjoint(rng1, rng2, isdisjoint, error_type):
    if error_type == "r2":
        assert(isdisjoint == rng1.isdisjoint(rng2))
        rng2 = Range(rng2)
        error_type = None
    if error_type is not None:
        asserterror(error_type, rng1.isdisjoint, (rng2,))
    else:
        assert(rng1.isdisjoint(rng2) == rng2.isdisjoint(rng1))
        assert(isdisjoint == rng1.isdisjoint(rng2))


@pytest.mark.parametrize(
    "rng1,rng2,union,error_type", [
        (Range(1, 3), Range(2, 4), Range(1, 4), None),
        (Range(1, 3), "[2, 4)", Range(1, 4), "r2"),
        (Range(1, 3), Range(2, 4, include_end=True), Range(1, 4, include_end=True), None),
        (Range(1, 3), Range(3, 5), Range(1, 5), None),
        (Range(2, 4), Range(1, 3), Range(1, 4), None),
        (Range(1, 3), Range(3, 5, include_start=False), None, None),
        (Range(1, 3), Range(4, 6), None, None),
        (Range(1, 4), Range(2, 3), Range(1, 4), None),
        (Range(1, 4), Range(1, 4), Range(1, 4), None),
        (Range(1, 4, include_start=False), Range(1, 4, include_end=True), Range(1, 4, include_end=True), None),
        (Range(2, 3), RangeSet(Range(1, 2), Range(3, 4)), Range(1, 4), None),  # test other stuff in RangeSet.union
        # intended errors
        (Range(1, 3), Range("apple", "banana"), None, TypeError),
        (Range(1, 3), "2, 4", None, TypeError),
        (Range(1, 3), 2, None, TypeError),
    ]
)
def test_range_union(rng1, rng2, union, error_type):
    if error_type == "r2":
        assert(union == rng1.union(rng2))
        rng2 = Range(rng2)
        error_type = None
    if error_type is not None:
        asserterror(error_type, rng1.union, (rng2,))
    else:
        assert(rng1.union(rng2) == rng2.union(rng1))
        assert(rng1.union(rng2) == rng1 | rng2)
        assert(union == rng1.union(rng2))


@pytest.mark.parametrize(
    "rng1,rng2,intersect,error_type", [
        (Range(1, 3), Range(2, 4), Range(2, 3, include_end=False), None),
        (Range(1, 3), "[2, 4)", Range(2, 3, include_end=False), "r2"),
        (Range(1, 3, include_end=True), Range(2, 4), Range(2, 3, include_end=True), None),
        (Range(1, 2), Range(2, 3), Range(2, 2), None),
        (Range(1, 3), Range(1, 3), Range(1, 3), None),
        (Range(1, 4), Range(2, 3), Range(2, 3), None),
        (Range(1, 3), Range(3, 5, include_start=False), None, None),
        (Range(1, 2), Range(3, 4), None, None),
        (Range(1, 4), RangeSet(Range(3, 6)), Range(3, 4), None),
        # intended errors
        (Range(1, 3), Range("apple", "banana"), None, TypeError),
        (Range(1, 3), "2, 4", None, TypeError),
        (Range(1, 3), 2, None, TypeError),
    ]
)
def test_range_intersect(rng1, rng2, intersect, error_type):
    if error_type == "r2":
        assert(intersect == rng1.intersection(rng2))
        rng2 = Range(rng2)
        error_type = None
    if error_type is not None:
        asserterror(error_type, rng1.intersection, (rng2,))
    else:
        assert(rng1.intersection(rng2) == rng2.intersection(rng1))
        assert(rng1 & rng2 == rng1.intersection(rng2))
        assert(intersect == rng1.intersection(rng2))


@pytest.mark.parametrize(
    "rng1,rng2,forward_diff,backward_diff,error_type", [
        (Range(1, 3), Range(2, 4), Range(1, 2), Range(3, 4), None),
        (Range(1, 3), "[2, 4)", Range(1, 2), Range(3, 4), "r2"),
        (Range(1, 3), Range(2, 3), Range(1, 2), None, None),
        (Range(1, 3), Range(1, 2), Range(2, 3), None, None),
        (Range(1, 3), Range(2, 3), Range(1, 2), None, None),
        (Range(1, 3), Range(4, 6), Range(1, 3), Range(4, 6), None),
        (Range(1, 3), Range(1, 3), None, None, None),
        (Range(1, 3, include_end=True), Range(2, 4), Range(1, 2), Range(3, 4, include_start=False), None),
        (Range(1, 4), Range(2, 3), RangeSet((Range(1, 2), Range(3, 4))), None, None),
        (Range(1, 3), RangeSet(Range(2, 4)), RangeSet(Range(1, 2)), Range(3, 4), None),
        (Range(1, 3), Range(2, 2), RangeSet(Range(1, 3)), None, None),
        # intended errors
        (Range(1, 3), Range("apple", "banana"), None, None, TypeError),
        (Range(1, 3), "2, 4", None, None, TypeError),
        (Range(1, 3), 2, None, None, TypeError),
    ]
)
def test_range_difference(rng1, rng2, forward_diff, backward_diff, error_type):
    if error_type == "r2":
        assert(rng1.difference(rng2) == rng1 - rng2)
        rng2 = Range(rng2)
        error_type = None
    if error_type is not None:
        asserterror(error_type, rng1.difference, (rng2,))
    else:
        assert(rng1.difference(rng2) == rng1 - rng2)
        assert(rng2.difference(rng1) == rng2 - rng1)
        assert(forward_diff == rng1.difference(rng2))
        assert(backward_diff == rng2.difference(rng1))


@pytest.mark.parametrize(
    "rng1,rng2,symdiff,error_type", [
        (Range(1, 3), Range(2, 4), RangeSet(Range(1, 2), Range(3, 4)), None),  # standard overlapping
        (Range(1, 2), Range(3, 4), RangeSet(Range(1, 2), Range(3, 4)), None),  # totally disjoint
        (Range(1, 4), Range(2, 3), RangeSet(Range(1, 2), Range(3, 4)), None),  # one contains the other
        (Range(1, 4), Range(2, 4), Range(1, 2), None),  # single range
        (Range(1, 4), Range(1, 4), None, None),  # exactly the same, no symmetric difference
        (Range("[1..4]"), Range("(1..4)"), RangeSet(Range("[1..1]"), Range("[4..4]")), None),  # single-point ranges
        (Range(1, 3), RangeSet(Range(2, 4)), RangeSet(Range(1, 2), Range(3, 4)), None),  # basic RangeSet
        # intended errors
        (Range(1, 3), Range("apple", "banana"), None, TypeError),
        (Range(1, 3), "2, 4", None, TypeError),
        (Range(1, 3), 2, None, TypeError),
    ]
)
def test_range_symmetric_difference(rng1, rng2, symdiff, error_type):
    if error_type is not None:
        asserterror(error_type, rng1.symmetric_difference, (rng2,))
    else:
        assert(rng1.symmetric_difference(rng2) == rng2.symmetric_difference(rng1))
        assert(rng1.symmetric_difference(rng2) == rng1 ^ rng2)
        assert(symdiff == rng1.symmetric_difference(rng2))


@pytest.mark.parametrize(
    "rng,length,error_type", [
        # regular numbers
        (Range(1, 2), 1, None),
        (Range(-2, 2), 4, None),
        (Range(3, 4.5), 1.5, None),
        (Range(3.25, 4.75), 1.5, None),
        (Range(0.1, 0.2), 0.1, None),
        (Range(), float('inf'), None),
        (Range(start=9e99), float('inf'), None),
        (Range(end=-9e99), float('inf'), None),
        # irregular but comparable arguments
        (Range(Decimal(1), Decimal(4)), Decimal(3), None),
        (Range(Decimal(1.5), Decimal(4.75)), Decimal(3.25), None),
        (Range(datetime.date(2018, 4, 1), datetime.date(2018, 4, 16)), datetime.timedelta(days=15), None),
        (Range(datetime.timedelta(seconds=82800), datetime.timedelta(days=1, seconds=3600)),
            datetime.timedelta(seconds=7200), None),
        # type coercion
        (Range(1, Decimal(4.5)), 3.5, None),
        (Range(1.5, Decimal(4.5)), 3, None),
        (Range(Decimal(1.5), 4), 2.5, None),
        (Range(Decimal(1.5), 4.75), 3.25, None),
        # errors
        (Range('apple', 'banana'), 0, TypeError),
    ]
)
def test_range_length(rng, length, error_type):
    if error_type is not None:
        asserterror(error_type, rng.length, ())
    else:
        assert(length == rng.length())


def test_range_docstring():
    a = Range()
    b = Range()
    assert(a == b)
    assert(str(a) == "[-inf, inf)")

    c = Range("(-3, 5.5)")
    d = Range("[-3, 5.5)")
    assert(c != d)
    assert(c > d)
    assert(c.start == d.start and c.end == d.end)
    assert(c.start == -3 and c.end == 5.5)

    e = Range(3, 5)
    f = Range(3, 5, include_start=False, include_end=True)
    assert(e != f)
    assert(e < f)
    assert(str(e) == "[3, 5)")
    assert(str(f) == "(3, 5]")
    assert(e.start == f.start and e.end == f.end)

    g = Range(start=3, end=5)
    h = Range(start=3)
    i = Range(end=5)
    j = Range(start=3, end=5, include_start=False, include_end=True)
    k = Range(start=datetime.date(1969, 10, 5))
    l = Range(end="ni", include_end=True)
    assert(str(g) == "[3, 5)")
    assert(str(h) == "[3, inf)")
    assert(str(i) == "[-inf, 5)")
    assert(str(j) == "(3, 5]")
    assert(str(k) == "[1969-10-05, inf)")
    assert(repr(k) == "Range[datetime.date(1969, 10, 5), inf)")
    assert(str(l) == "[-inf, ni]")
    assert(repr(l) == "Range[-inf, 'ni']")

    m = Range(datetime.date(1478, 11, 1), datetime.date(1834, 7, 15))
    assert(datetime.date(1492, 8, 3) in m)
    assert(datetime.date(1979, 8, 17) not in m)

    n = Range("killer", "rabbit")
    assert("grenade" not in n)
    assert("pin" in n)
    assert("three" not in n)

    o = Range(include_end=True)
    assert(str(o) == "[-inf, inf]")
    assert(0 in o)
    assert(1 in o)
    assert(-99e99 in o)
    assert("one" in o)
    assert(datetime.date(1975, 3, 14) in o)
    assert(None in o)
    assert(float('nan') not in o)

    r = Range(include_start=True, include_end=False)
    assert(str(r) == "[-inf, inf)")
    assert(float('-inf') in r)
    assert(float('inf') not in r)


#######################################################################################################
# Tests for RangeSet
#######################################################################################################


@pytest.mark.parametrize(
    "args,ranges,strr,reprr,isempty", [
        ([], [], "{}", "RangeSet{}", True),  # empty RangeSet
        (["[1..1]"], [Range("[1..1]")], "{[1, 1]}", "RangeSet{Range[1, 1]}", False),  # contains one nonempty Range
        (["(1..1)"], [Range("(1..1)")], "{(1, 1)}", "RangeSet{Range(1, 1)}", True),  # contains one empty Range
        (["[1, 2)", "[3, 4)", "[5, 6)"], [Range(1, 2), Range(3, 4), Range(5, 6)],
            "{[1, 2), [3, 4), [5, 6)}", "RangeSet{Range[1, 2), Range[3, 4), Range[5, 6)}", False),
        ([[]], [], "{}", "RangeSet{}", True),  # once-nested empty list
        (["[0, 1)", ["[1.5, 2)", "[2.5, 3)"], "[4, 5)"], [Range(0, 1), Range(1.5, 2), Range(2.5, 3), Range(4, 5)],
            "{[0, 1), [1.5, 2), [2.5, 3), [4, 5)}",
            "RangeSet{Range[0, 1), Range[1.5, 2), Range[2.5, 3), Range[4, 5)}", False),  # mix Rangelike, iterable args
        (["[0, 3]", "[2, 4)", "[5, 6]"], [Range(0, 4), Range("[5, 6]")],
            "{[0, 4), [5, 6]}", "RangeSet{Range[0, 4), Range[5, 6]}", False),  # overlapping
        (["[0, 4)", "(1, 3)"], [Range(0, 4)], "{[0, 4)}", "RangeSet{Range[0, 4)}", False),  # overlapping 2
        ([Range(1, 3), Range(2, 4)], [Range(1, 4)], "{[1, 4)}", "RangeSet{Range[1, 4)}", False),
        ([Range('apple', 'carrot'), Range('banana', 'durian')], [Range('apple', 'durian')],
            "{[apple, durian)}", "RangeSet{Range['apple', 'durian')}", False),
        ([RangeSet("(0, 1)", "(1, 2)", "(2, 3)")], [Range("(0, 1)"), Range("(1, 2)"), Range("(2, 3)")],
            "{(0, 1), (1, 2), (2, 3)}", "RangeSet{Range(0, 1), Range(1, 2), Range(2, 3)}", False)
    ]
)
def test_rangeset_constructor_valid(args, ranges, strr, reprr, isempty):
    """
    Tests that the constructor of rngset works as intended. Also, as a byproduct,
    tests the .ranges(), .__str__(), .__repr__(), .clear(), and .isempty()
    """
    rangeset = RangeSet(*args)
    assert(ranges == rangeset.ranges())
    assert(strr == str(rangeset))
    assert(reprr == repr(rangeset))
    assert(isempty == rangeset.isempty())
    assert(isempty != bool(rangeset))
    assert(hash(rangeset) == hash(rangeset.copy()))
    rangeset.clear()
    assert("{}" == str(rangeset))
    assert("RangeSet{}" == repr(rangeset))
    assert(rangeset.isempty())
    assert(not bool(rangeset))


@pytest.mark.parametrize(
    "args,error_type", [
        ([[[]]], ValueError),  # triply-nested but empty (empty shouldn't matter)
        (["4, 5"], ValueError),  # invalid range object
        ([["4, 5"]], ValueError),  # iterable containing invalid range object
        ([6], ValueError),  # non-RangeLike, non-iterable single argument
        ([datetime.date(4, 5, 6)], ValueError),  # non-RangeLike, non-iterable single argument
        ([Range(4, 5), Range("apple", "banana")], TypeError)  # type mismatch
    ]
)
def test_rangeset_constructor_invalid(args, error_type):
    asserterror(error_type, RangeSet, args)


@pytest.mark.parametrize(
    "rngset,to_add,before,after,error_type", [
        (RangeSet(), Range(1, 3), "{}", "{[1, 3)}", None),
        (RangeSet(), "[1..3)", "{}", "{[1, 3)}", None),
        (RangeSet(Range(1, 2)), Range(3, 4), "{[1, 2)}", "{[1, 2), [3, 4)}", None),
        (RangeSet(Range(1, 3)), Range(2, 4), "{[1, 3)}", "{[1, 4)}", None),
        (RangeSet(Range(1, 4)), Range(2, 3), "{[1, 4)}", "{[1, 4)}", None),
        (RangeSet(Range(1, 4)), Range(3, 4, include_end=True), "{[1, 4)}", "{[1, 4]}", None),
        (RangeSet(Range(1, 3), Range(4, 6)), Range(2, 5), "{[1, 3), [4, 6)}", "{[1, 6)}", None),
        (RangeSet(Range(1, 2), Range(3, 4)), RangeSet(Range(5, 6), Range(7, 8)),
            "{[1, 2), [3, 4)}", "{[1, 2), [3, 4), [5, 6), [7, 8)}", None),
        (RangeSet(), RangeSet(Range(1, 2), Range(3, 4)), "{}", "{[1, 2), [3, 4)}", None),
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(2, 5), Range(7, 9)),
            "{[1, 3), [4, 6)}", "{[1, 6), [7, 9)}", None),
        (RangeSet(Range(1, 2), Range(4, 5)), Range(3, 3, include_end=True),
            "{[1, 2), [4, 5)}", "{[1, 2), [3, 3], [4, 5)}", None),
        (RangeSet(), Range(Range(1, 2), Range(3, 4)), "{}", "{[[1, 2), [3, 4))}", None),
        # expected error conditions
        (RangeSet(), [Range(1, 2)], "{}", "", ValueError),
        (RangeSet(), "1, 3", "{}", "", ValueError),
        (RangeSet("[1, 2)"), Range("apple", "banana"), "{[1, 2)}", "", TypeError)
    ]
)
def test_rangeset_add(rngset, to_add, before, after, error_type):
    assert(before == str(rngset))
    if error_type is not None:
        asserterror(error_type, rngset.add, (to_add,))
        assert(before == str(rngset))
    else:
        rngset.add(to_add)
        assert(after == str(rngset))


@pytest.mark.parametrize(
    "rngset,to_extend,before,after,error_type", [
        # correct adds
        (RangeSet(), RangeSet(), "{}", "{}", None),
        (RangeSet(), RangeSet("[1, 2]"), "{}", "{[1, 2]}", None),
        (RangeSet(), RangeSet(Range(1, 3), Range(4, 6)), "{}", "{[1, 3), [4, 6)}", None),
        (RangeSet(), [Range(1, 3), Range(4, 6)], "{}", "{[1, 3), [4, 6)}", None),
        (RangeSet(), [Range("apple", "banana"), Range("cherry", "durian")],
            "{}", "{[apple, banana), [cherry, durian)}", None),
        (RangeSet(Range(1, 3), Range(4, 6)), [Range(7, 9)], "{[1, 3), [4, 6)}", "{[1, 3), [4, 6), [7, 9)}", None),
        (RangeSet(Range(1, 3), Range(4, 6)), [Range(2, 5), Range(7, 9)], "{[1, 3), [4, 6)}", "{[1, 6), [7, 9)}", None),
        # expected errors
        (RangeSet(), (1, 3), "{}", "", ValueError),
        (RangeSet(), Range(1, 3), "{}", "", TypeError),
        (RangeSet(), "[1, 3)", "{}", "", ValueError),
        (RangeSet(), ["[3, 1]"], "{}", "", ValueError),  # invalid range definition, valid otherwise
        (RangeSet("[1, 3)"), RangeSet(Range("apple", "banana"), Range("cherry", "durian")),
            "{[1, 3)}", "{[1, 3)}", TypeError),
        (RangeSet(), [Range("apple", "banana"), Range(1, 3)], "{}", "{}", TypeError),
    ]
)
def test_rangeset_extend(rngset, to_extend, before, after, error_type):
    assert(before == str(rngset))
    if error_type is not None:
        asserterror(error_type, rngset.extend, (to_extend,))
        assert(before == str(rngset))
    else:
        rngset.extend(to_extend)
        assert(after == str(rngset))


@pytest.mark.parametrize(
    "rngset,to_discard,before,after,error_type", [
        # remains unchanged
        (RangeSet(), Range(), "{}", "{}", None),
        (RangeSet(), Range(1, 3), "{}", "{}", None),
        (RangeSet(Range(2, 3)), Range(0, 1), "{[2, 3)}", "{[2, 3)}", None),
        (RangeSet(Range(2, 3)), RangeSet((Range(0, 1), Range(4, 5))), "{[2, 3)}", "{[2, 3)}", None),
        # is modified properly
        (RangeSet(Range(1, 5)), "(2, 4]", "{[1, 5)}", "{[1, 2], (4, 5)}", None),
        (RangeSet(Range(1, 5)), Range(3, 5), "{[1, 5)}", "{[1, 3)}", None),
        (RangeSet(Range(1, 5)), Range(3, 6), "{[1, 5)}", "{[1, 3)}", None),
        (RangeSet(Range(1, 5)), Range(0, 3), "{[1, 5)}", "{[3, 5)}", None),
        (RangeSet(Range(1, 5)), Range(1, 3), "{[1, 5)}", "{[3, 5)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(3, 6), "{[1, 4), [5, 8)}", "{[1, 3), [6, 8)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(3, 9), "{[1, 4), [5, 8)}", "{[1, 3)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(3, 4.5), "{[1, 4), [5, 8)}", "{[1, 3), [5, 8)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(0, 6), "{[1, 4), [5, 8)}", "{[6, 8)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(0, 9), "{[1, 4), [5, 8)}", "{}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(1, 8), "{[1, 4), [5, 8)}", "{}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(), "{[1, 4), [5, 8)}", "{}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), "(3, 6]", "{[1, 4), [5, 8)}", "{[1, 3], (6, 8)}", None),
        (RangeSet(Range()), Range(5, 8), "{[-inf, inf)}", "{[-inf, 5), [8, inf)}", None),
        # error conditions
        (RangeSet(), "[3, 1)", "{}", "", ValueError),
        (RangeSet(Range(2, 3)), Range("apple", "banana"), "{[2, 3)}", "", TypeError),
        (RangeSet(), [Range(1, 2), Range(3, 4)], "{}", "", ValueError),
        (RangeSet(), 2, "{}", "", ValueError),
        # we'll mostly leave RangeSets and other iterables alone for now, since they get tested later
    ]
)
def test_rangeset_discard(rngset, to_discard, before, after, error_type):
    assert(before == str(rngset))
    if error_type is not None:
        asserterror(error_type, rngset.discard, (to_discard,))
        assert(before == str(rngset))
    else:
        rngset.discard(to_discard)
        assert(after == str(rngset))


@pytest.mark.parametrize(
    "rngset,to_discard,before,after,error_type", [
        # unchanged
        (RangeSet(), Range(), "{}", "{}", None),
        (RangeSet(), RangeSet(), "{}", "{}", None),
        (RangeSet(), [], "{}", "{}", None),
        (RangeSet(), ["(3, 4)"], "{}", "{}", None),
        (RangeSet(), RangeSet("(3, 4)"), "{}", "{}", None),
        (RangeSet(), ["(3, 4)", "(1, 2)"], "{}", "{}", None),
        (RangeSet(), RangeSet("(3, 4)", "(1, 2)"), "{}", "{}", None),
        (RangeSet(Range(1, 2), Range(3, 4)), RangeSet("[0, 1)", "[5, 6]"),
            "{[1, 2), [3, 4)}", "{[1, 2), [3, 4)}", None),
        # changed properly
        (RangeSet(Range()), [Range(1, 3), Range(4, 6)], "{[-inf, inf)}", "{[-inf, 1), [3, 4), [6, inf)}", None),
        (RangeSet(Range(1, 3)), [Range(2, 4)], "{[1, 3)}", "{[1, 2)}", None),
        (RangeSet(Range(1, 4)), [Range(1, 2), Range(3, 4)], "{[1, 4)}", "{[2, 3)}", None),
        (RangeSet(Range(3, 6), Range(7, 10)), RangeSet(Range(1, 4), Range(5, 8), Range(9, 11)),
            "{[3, 6), [7, 10)}", "{[4, 5), [8, 9)}", None),
        (RangeSet(Range(1, 10)), [Range(1, 2), Range(3, 4), Range(5, 6), Range(7, 8), Range(9, 10)],
            "{[1, 10)}", "{[2, 3), [4, 5), [6, 7), [8, 9)}", None),
        # error conditions
        (RangeSet(), [""], "{}", "", ValueError),
        (RangeSet(Range(2, 3)), [Range("apple", "banana")], "{[2, 3)}", "", TypeError),
        (RangeSet(Range(1, 4)), [Range(2, 3), Range("apple", "banana")], "{[1, 4)}", "", TypeError),
        # tests left over from discard() that still apply
        (RangeSet(), Range(), "{}", "{}", None),
        (RangeSet(), Range(1, 3), "{}", "{}", None),
        (RangeSet(Range(2, 3)), Range(0, 1), "{[2, 3)}", "{[2, 3)}", None),
        (RangeSet(Range(2, 3)), RangeSet((Range(0, 1), Range(4, 5))), "{[2, 3)}", "{[2, 3)}", None),
        (RangeSet(Range(1, 5)), "(2, 4]", "{[1, 5)}", "{[1, 2], (4, 5)}", None),
        (RangeSet(Range(1, 5)), Range(3, 5), "{[1, 5)}", "{[1, 3)}", None),
        (RangeSet(Range(1, 5)), Range(3, 6), "{[1, 5)}", "{[1, 3)}", None),
        (RangeSet(Range(1, 5)), Range(0, 3), "{[1, 5)}", "{[3, 5)}", None),
        (RangeSet(Range(1, 5)), Range(1, 3), "{[1, 5)}", "{[3, 5)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(3, 6), "{[1, 4), [5, 8)}", "{[1, 3), [6, 8)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(3, 9), "{[1, 4), [5, 8)}", "{[1, 3)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(3, 4.5), "{[1, 4), [5, 8)}", "{[1, 3), [5, 8)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(0, 6), "{[1, 4), [5, 8)}", "{[6, 8)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(0, 9), "{[1, 4), [5, 8)}", "{}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(1, 8), "{[1, 4), [5, 8)}", "{}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), Range(), "{[1, 4), [5, 8)}", "{}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), "(3, 6]", "{[1, 4), [5, 8)}", "{[1, 3], (6, 8)}", None),
        (RangeSet(Range()), Range(5, 8), "{[-inf, inf)}", "{[-inf, 5), [8, inf)}", None),
    ]
)
def test_rangeset_difference(rngset, to_discard, before, after, error_type):
    # Tests both .difference() and .difference_update()
    assert(before == str(rngset))
    if error_type is not None:
        asserterror(error_type, rngset.difference, (to_discard,))
        asserterror(error_type, rngset.difference_update, (to_discard,))
        assert(before == str(rngset))
    else:
        copy_rngset = rngset.copy()
        new_rngset = rngset.difference(to_discard)
        rngset.difference_update(to_discard)
        sub_rngset = rngset - to_discard
        copy_rngset -= to_discard
        assert(after == str(new_rngset))
        assert(after == str(rngset))
        assert(after == str(sub_rngset))
        assert(after == str(copy_rngset))


@pytest.mark.parametrize(
    "rngset,to_intersect,before,after,error_type", [
        (RangeSet(Range(2, 3), Range(7, 8)), [Range(1, 4), Range(5, 6)], "{[2, 3), [7, 8)}", "{[2, 3)}", None),
        (RangeSet(Range(1, 4)), Range(3, 5), "{[1, 4)}", "{[3, 4)}", None),
        (RangeSet(Range(1, 4)), RangeSet(Range(3, 5)), "{[1, 4)}", "{[3, 4)}", None),
        (RangeSet(Range(3, 5)), RangeSet(Range(1, 4)), "{[3, 5)}", "{[3, 4)}", None),
        (RangeSet(Range(1, 5)), RangeSet(Range(2, 3)), "{[1, 5)}", "{[2, 3)}", None),
        (RangeSet(Range(2, 3)), RangeSet(Range(1, 5)), "{[2, 3)}", "{[2, 3)}", None),
        (RangeSet(Range(1, 6)), RangeSet(Range(2, 3), Range(4, 5)), "{[1, 6)}", "{[2, 3), [4, 5)}", None),
        (RangeSet(Range(2, 3), Range(4, 5)), RangeSet(Range(1, 6)), "{[2, 3), [4, 5)}", "{[2, 3), [4, 5)}", None),
        (RangeSet(Range(1, 3), Range(4, 6)), Range(2, 5), "{[1, 3), [4, 6)}", "{[2, 3), [4, 5)}", None),
        (RangeSet(Range(2, 5)), RangeSet(Range(1, 3), Range(4, 6)), "{[2, 5)}", "{[2, 3), [4, 5)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), RangeSet(Range(2, 3), Range(6, 7)),
            "{[1, 4), [5, 8)}", "{[2, 3), [6, 7)}", None),
        (RangeSet(Range(2, 3), Range(6, 7)), RangeSet(Range(1, 4), Range(5, 8)),
            "{[2, 3), [6, 7)}", "{[2, 3), [6, 7)}", None),
        (RangeSet(Range(1, 4), Range(5, 6)), RangeSet(Range(2, 3), Range(7, 8)), "{[1, 4), [5, 6)}", "{[2, 3)}", None),
        (RangeSet(Range(2, 3), Range(7, 8)), RangeSet(Range(1, 4), Range(5, 6)), "{[2, 3), [7, 8)}", "{[2, 3)}", None),
        (RangeSet(Range(1, 4), Range(5, 6)), Range(2, 10), "{[1, 4), [5, 6)}", "{[2, 4), [5, 6)}", None),
        (RangeSet(Range(2, 10)), RangeSet(Range(1, 4), Range(5, 6)), "{[2, 10)}", "{[2, 4), [5, 6)}", None),
        (RangeSet(Range(1, 4)), Range(1, 4), "{[1, 4)}", "{[1, 4)}", None),
        (RangeSet(Range(1, 4)), RangeSet(Range(1, 4)), "{[1, 4)}", "{[1, 4)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), RangeSet(Range(1, 3), Range(6, 8, include_end=True)),
            "{[1, 4), [5, 8)}", "{[1, 3), [6, 8)}", None),
        (RangeSet(Range(1, 4), Range(5, 8)), RangeSet(Range(1, 3), Range(6, 8)),
            "{[1, 4), [5, 8)}", "{[1, 3), [6, 8)}", None),
        (RangeSet(Range("apple", "cherry", include_end=True)), RangeSet(Range("banana", "durian", include_start=False)),
            "{[apple, cherry]}", "{(banana, cherry]}", None),
        (RangeSet(Range("banana", "durian", include_start=False)), RangeSet(Range("apple", "cherry", include_end=True)),
            "{(banana, durian)}", "{(banana, cherry]}", None),
        (RangeSet(), RangeSet(), "{}", "{}", None),
        (RangeSet(Range(1, 4)), RangeSet(), "{[1, 4)}", "{}", None),
        (RangeSet(Range()), RangeSet(), "{[-inf, inf)}", "{}", None),
        (RangeSet(), Range(), "{}", "{}", None),
        (RangeSet(Range()), RangeSet(Range(1, 4)), "{[-inf, inf)}", "{[1, 4)}", None),
        (RangeSet(Range(1, 4)), RangeSet(Range()), "{[1, 4)}", "{[1, 4)}", None),
        (RangeSet(Range(include_end=True)), Range(include_start=False), "{[-inf, inf]}", "{(-inf, inf)}", None),
        (RangeSet(Range(include_start=False)), Range(include_end=True), "{(-inf, inf)}", "{(-inf, inf)}", None),
        # error conditions
        (RangeSet(), [""], "{}", "", ValueError),
        (RangeSet(Range(2, 3)), [Range("apple", "banana")], "{[2, 3)}", "", TypeError),
        (RangeSet(Range(1, 4)), [Range(2, 3), Range("apple", "banana")], "{[1, 4)}", "", TypeError),
    ]
)
def test_rangeset_intersection(rngset, to_intersect, before, after, error_type):
    # tests both .intersection() and .intersection_update()
    assert(before == str(rngset))
    if error_type is not None:
        asserterror(error_type, rngset.intersection, (to_intersect,))
        asserterror(error_type, rngset.intersection_update, (to_intersect,))
        assert(before == str(rngset))
    else:
        copy_rngset = rngset.copy()
        new_rngset = rngset.intersection(to_intersect)
        and_rngset = rngset & to_intersect
        rngset.intersection_update(to_intersect)
        copy_rngset &= to_intersect
        assert(after == str(new_rngset))
        assert(after == str(rngset))
        assert(after == str(and_rngset))
        assert(after == str(copy_rngset))


@pytest.mark.parametrize(
    "rngset,to_union,before,after,error_type", [
        (RangeSet(), RangeSet(), "{}", "{}", None),
        (RangeSet(), Range(1, 4), "{}", "{[1, 4)}", None),
        (RangeSet(Range(1, 4)), RangeSet(), "{[1, 4)}", "{[1, 4)}", None),
        (RangeSet(), Range(), "{}", "{[-inf, inf)}", None),
        (RangeSet(Range(1, 4)), Range(), "{[1, 4)}", "{[-inf, inf)}", None),
        (RangeSet(Range()), Range(1, 4), "{[-inf, inf)}", "{[-inf, inf)}", None),
        (RangeSet(Range()), RangeSet(), "{[-inf, inf)}", "{[-inf, inf)}", None),
        (RangeSet(Range(1, 4)), [Range(3, 6)], "{[1, 4)}", "{[1, 6)}", None),
        (RangeSet(Range(1, 4)), Range(3, 6), "{[1, 4)}", "{[1, 6)}", None),
        (RangeSet(Range(3, 6)), Range(1, 4), "{[3, 6)}", "{[1, 6)}", None),
        (RangeSet(Range(1, 4)), Range(1, 4), "{[1, 4)}", "{[1, 4)}", None),
        (RangeSet(Range(1, 4)), Range(1, 4, include_end=True), "{[1, 4)}", "{[1, 4]}", None),
        (RangeSet(Range(1, 4)), [Range(1, 2), Range(3, 4, include_end=True)], "{[1, 4)}", "{[1, 4]}", None),
        (RangeSet(Range(1, 2)), Range(3, 4), "{[1, 2)}", "{[1, 2), [3, 4)}", None),
        (RangeSet(Range(3, 4)), Range(1, 2), "{[3, 4)}", "{[1, 2), [3, 4)}", None),
        (RangeSet(Range(1, 3), Range(4, 7), Range(8, 10)), [Range(2, 5), Range(6, 9)],
            "{[1, 3), [4, 7), [8, 10)}", "{[1, 10)}", None),
        (RangeSet(Range(1, 5)), Range(2, 3), "{[1, 5)}", "{[1, 5)}", None),
        (RangeSet(Range(1, 4), Range(5, 7)), RangeSet(Range(4, 5), Range(8, 10)),
            "{[1, 4), [5, 7)}", "{[1, 7), [8, 10)}", None),
        (RangeSet(Range(1, 3)), Range(1, 2), "{[1, 3)}", "{[1, 3)}", None),
        (RangeSet(Range(1, 3)), Range(2, 3), "{[1, 3)}", "{[1, 3)}", None),
        # error conditions
        (RangeSet(), [""], "{}", "", ValueError),
        (RangeSet(Range(2, 3)), [Range("apple", "banana")], "{[2, 3)}", "", TypeError),
        (RangeSet(Range(2, 3)), [Range(4, 5), Range("apple", "banana")], "{[2, 3)}", "", TypeError),
    ]
)
def test_rangeset_union(rngset, to_union, before, after, error_type):
    # tests .union() and .update()
    assert(before == str(rngset))
    if error_type is not None:
        asserterror(error_type, rngset.union, (to_union,))
        asserterror(error_type, rngset.update, (to_union,))
        assert(before == str(rngset))
    else:
        copy_rngset = rngset.copy()
        copy_rngset2 = rngset.copy()
        new_rngset = rngset.union(to_union)
        add_rngset = rngset + to_union
        or_rngset = rngset | to_union
        rngset.update(to_union)
        copy_rngset += to_union
        copy_rngset2 |= to_union
        assert(after == str(new_rngset))
        assert(after == str(add_rngset))
        assert(after == str(or_rngset))
        assert(after == str(rngset))
        assert(after == str(copy_rngset))
        assert(after == str(copy_rngset2))


@pytest.mark.parametrize(
    "rngset,to_symdiff,before,after,error_type", [
        (RangeSet(), RangeSet(), "{}", "{}", None),
        (RangeSet(), RangeSet(Range(2, 4)), "{}", "{[2, 4)}", None),
        (RangeSet(), Range(2, 4), "{}", "{[2, 4)}", None),
        (RangeSet(), [Range(2, 4)], "{}", "{[2, 4)}", None),
        (RangeSet(Range(2, 4)), RangeSet(), "{[2, 4)}", "{[2, 4)}", None),
        (RangeSet(), [Range(2, 4), Range(5, 7)], "{}", "{[2, 4), [5, 7)}", None),
        (RangeSet(Range(2, 4), Range(5, 7)), RangeSet(), "{[2, 4), [5, 7)}", "{[2, 4), [5, 7)}", None),
        (RangeSet(), Range(), "{}", "{[-inf, inf)}", None),
        (RangeSet(Range()), RangeSet(), "{[-inf, inf)}", "{[-inf, inf)}", None),
        (RangeSet(Range()), Range(2, 4), "{[-inf, inf)}", "{[-inf, 2), [4, inf)}", None),
        (RangeSet(Range(2, 4)), Range(), "{[2, 4)}", "{[-inf, 2), [4, inf)}", None),
        (RangeSet(Range()), [Range(2, 3), Range(4, 5)], "{[-inf, inf)}", "{[-inf, 2), [3, 4), [5, inf)}", None),
        (RangeSet(Range()), Range(), "{[-inf, inf)}", "{}", None),
        (RangeSet(Range(1, 2)), Range(1, 2), "{[1, 2)}", "{}", None),
        (RangeSet(Range(1, 4)), RangeSet(Range(2, 3)), "{[1, 4)}", "{[1, 2), [3, 4)}", None),
        (RangeSet(Range(1, 3)), Range(2, 4), "{[1, 3)}", "{[1, 2), [3, 4)}", None),
        (RangeSet(Range(1, 3), Range(4, 6)), Range(2, 5), "{[1, 3), [4, 6)}", "{[1, 2), [3, 4), [5, 6)}", None),
        (RangeSet(Range(2, 5)), [Range(1, 3), Range(4, 6)], "{[2, 5)}", "{[1, 2), [3, 4), [5, 6)}", None),
        # error conditions
        (RangeSet(), [""], "{}", "", ValueError),
        (RangeSet(Range(2, 3)), [Range("apple", "banana")], "{[2, 3)}", "", TypeError),
        (RangeSet(Range(2, 3)), [Range(4, 5), Range("apple", "banana")], "{[2, 3)}", "", TypeError),
    ]
)
def test_rangeset_symdiff(rngset, to_symdiff, before, after, error_type):
    # tests .symmetric_difference() and .symmetric_difference_update()
    assert(before == str(rngset))
    if error_type is not None:
        asserterror(error_type, rngset.symmetric_difference, (to_symdiff,))
        asserterror(error_type, rngset.symmetric_difference_update, (to_symdiff,))
        assert(before == str(rngset))
    else:
        copy_rngset = rngset.copy()
        new_rngset = rngset.symmetric_difference(to_symdiff)
        xor_rngset = rngset ^ to_symdiff
        rngset.symmetric_difference_update(to_symdiff)
        copy_rngset ^= to_symdiff
        assert(after == str(new_rngset))
        assert(after == str(xor_rngset))
        assert(after == str(rngset))
        assert(after == str(copy_rngset))


@pytest.mark.parametrize(
    "rng1,rng2,isdisjoint,error_type", [
        # test cases carried over from Range.isdisjoint()
        (RangeSet(Range(1, 3)), Range(2, 4), False, None),
        (RangeSet(Range(1, 3)), Range(4, 6), True, None),
        (RangeSet(Range(1, 3)), Range(3, 5), True, None),
        (RangeSet(Range(1, 3)), "[3, 5)", True, None),
        (RangeSet(Range(1, 4)), Range(2, 3), False, None),
        (RangeSet(Range(1, 3, include_end=True)), Range(3, 5), False, None),
        (RangeSet(Range()), Range(1, 3), False, None),
        # new original test cases
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(3, 4)), True, None),
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(3, 4, include_end=True)), False, None),
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(3, 4), Range(6, 7)), True, None),
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(3, 4), Range(6, 7), Range(1, 2)), False, None),
        (RangeSet(Range(1, 4)), RangeSet(), True, None),
        (RangeSet(Range(2, 4)), RangeSet(Range(0, 1), Range(5, 6)), True, None),
        (RangeSet(Range(2, 4)), RangeSet(Range(1, 3)), False, None),
        (RangeSet(Range(2, 4)), RangeSet(Range(1, 3), Range(5, 6)), False, None),
        # errors
        (RangeSet(Range(1, 3)), RangeSet(Range("apple", "banana")), None, TypeError),
        (RangeSet(Range(1, 3)), [Range(4, 6), Range("apple", "banana")], None, TypeError),
        (RangeSet(Range(1, 3)), Range("apple", "banana"), None, TypeError),
        (RangeSet(Range(1, 3)), "2, 4", None, ValueError),
    ]
)
def test_rangeset_isdisjoint(rng1, rng2, isdisjoint, error_type):
    if error_type is not None:
        asserterror(error_type, rng1.isdisjoint, (rng2,))
    else:
        assert(rng1.isdisjoint(rng2) == RangeSet(rng2).isdisjoint(rng1))
        assert(isdisjoint == rng1.isdisjoint(rng2))


@pytest.mark.parametrize(
    "rngset,before,after", [
        (RangeSet(), "{}", "{}"),
        (RangeSet(Range(1, 3)), "{[1, 3)}", "{[1, 3)}"),
        (RangeSet("[1, 1]"), "{[1, 1]}", "{[1, 1]}"),
        (RangeSet("[1, 1)"), "{[1, 1)}", "{}"),
        (RangeSet("(1, 1]"), "{(1, 1]}", "{}"),
        (RangeSet("(1, 1)"), "{(1, 1)}", "{}"),
        (RangeSet(Range(2, 3), Range(1, 1, include_start=False)), "{(1, 1), [2, 3)}", "{[2, 3)}"),
        (RangeSet(Range(1, 1, include_start=False)), "{(1, 1)}", "{}"),  # contains one empty range, should be removed
        (RangeSet(Range(1, 1, include_end=True)), "{[1, 1]}", "{[1, 1]}"),  # one non-empty range, should be preserved
        (RangeSet(Range(1, 2, include_start=False), Range(3, 3, include_start=False)), "{(1, 2), (3, 3)}", "{(1, 2)}"),
    ]
)
def test_rangeset_popempty(rngset, before, after):
    assert(before == str(rngset))
    rngset.popempty()
    assert(after == str(rngset))


@pytest.mark.parametrize(
    "rngset,item,rng", [
        (RangeSet(Range(1, 2)), 1, Range(1, 2)),
        (RangeSet(Range(1, 2)), 1.5, Range(1, 2)),
        (RangeSet(Range(1, 2)), 2, IndexError),
        (RangeSet(Range(1, 2)), 0, IndexError),
        (RangeSet(Range(1, 2)), 'banana', TypeError),
        (RangeSet(Range(1, 4)), Range(2, 3), Range(1, 4)),
        (RangeSet(Range(1, 3), Range(4, 6)), 2, Range(1, 3)),
        (RangeSet(Range(1, 3), Range(4, 6)), 5, Range(4, 6)),
        (RangeSet(Range(1, 3), Range(4, 6)), Range(2, 5), IndexError),
        (RangeSet(Range(1, 6)), RangeSet(Range(2, 3), Range(4, 5)), Range(1, 6)),
        (RangeSet(Range(1, 6), Range(7, 8)), RangeSet(Range(2, 3), Range(4, 5)), Range(1, 6)),
        (RangeSet(Range(1, 4), Range(5, 8)), RangeSet(Range(2, 3), Range(6, 7)), RangeSet(Range(1, 4), Range(5, 8))),
        (RangeSet(Range(1, 4), Range(5, 8), Range(10, 11)), RangeSet(Range(2, 3), Range(6, 7)),
            RangeSet(Range(1, 4), Range(5, 8))),
        (RangeSet(Range(1, 4), Range(5, 8)), RangeSet(Range(2, 3), Range(6, 9)), IndexError),
        (RangeSet(Range(1, 3)), Range('apple', 'banana'), TypeError),
        (RangeSet(Range('a', 'ba'), Range('bb', 'da'), Range('db', 'z')), 'bubble', Range('bb', 'da')),
        (RangeSet(Range((1, 2), (3, 3))), (1, 999), Range((1, 2), (3, 3))),
        (RangeSet(Range((1, 2), (3, 3))), (3, 2), Range((1, 2), (3, 3))),
        (RangeSet(Range((1, 2), (3, 3))), (3, 4), IndexError),
    ]
)
def test_rangeset_getrange(rngset, item, rng):
    # also tests __contains__
    assert(rngset in rngset)
    if rng in (IndexError,):
        # test the error condition
        assert (item not in rngset)
        asserterror(rng, rngset.getrange, (item,))
    elif rng in (ValueError, TypeError):
        asserterror(rng, rngset.__contains__, (item,))
        asserterror(rng, rngset.getrange, (item,))
    else:
        # test the actual condition
        assert(item in rngset)
        assert(item in rng)
        assert(rng == rngset.getrange(item))


@pytest.mark.parametrize(
    "lesser,greater,equal", [
        # from Range comparisons
        (RangeSet(Range()), Range(), True),
        (RangeSet(Range(1, 2)), Range("[1, 2)"), True),
        (RangeSet(Range(1, 2)), Range(1, 2, include_end=True), False),
        (RangeSet(Range(1, 2, include_start=True)), Range(1, 2, include_start=False), False),
        (RangeSet(Range()), Range(1, 2), False),
        (RangeSet(Range(1, 4)), Range(2, 3), False),
        (RangeSet(Range(1, 3)), Range(2, 4), False),
        # new RangeSet-specific stuff
        (RangeSet(Range(1, 3), Range(4, 6)), Range(2, 5), False),
        (RangeSet(Range(1, 3)), RangeSet(Range(1, 3), Range(4, 6)), False),
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(1, 3), Range(4, 6)), True),
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(1, 3), Range(4, 6, include_end=True)), False),
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(1, 3, include_end=True), Range(4, 6)), False),
        (RangeSet(Range(1, 3), Range(4, 6)), RangeSet(Range(1, 3, include_end=True), Range(4, 5)), False),
    ]
)
def test_rangeset_comparisons(lesser, greater, equal):
    assert (equal == (lesser == greater))
    assert (equal != (lesser != greater))
    assert (lesser <= greater)
    assert (equal != (lesser < greater))
    assert (not (greater < lesser))
    assert (equal != (greater > lesser))
    assert (not (lesser > greater))
    assert (greater >= lesser)


def test_rangeset_docstring():
    a = RangeSet()
    b = RangeSet([Range(0, 1), Range(2, 3), Range(4, 5)])
    c = RangeSet(Range(0, 1), Range(2, 3), Range(4, 5))
    d = RangeSet("[0, 1)", ["[1.5, 2)", "[2.5, 3)"], "[4, 5]")
    assert(str(a) == "{}")
    assert(str(b) == "{[0, 1), [2, 3), [4, 5)}")
    assert(str(c) == "{[0, 1), [2, 3), [4, 5)}")
    assert(b == c)
    assert(str(d) == "{[0, 1), [1.5, 2), [2.5, 3), [4, 5]}")

    asserterror(ValueError, RangeSet, ([[Range(0, 1), Range(2, 3)], [Range(4, 5), Range(6, 7)]],))

    f = RangeSet("[0, 3]", "[2, 4)", "[5, 6]")
    assert(str(f) == "{[0, 4), [5, 6]}")


#######################################################################################################
# Tests for RangeDict
#######################################################################################################


@pytest.mark.parametrize(
    "iterable,strr,reprr,isempty,length,error_type", [
        # empty iterable constructors
        ((), "{}", "RangeDict{}", True, 0, None),
        ([], "{}", "RangeDict{}", True, 0, None),
        ({}, "{}", "RangeDict{}", True, 0, None),
        (RangeDict(), "{}", "RangeDict{}", True, 0, None),
        # construct via tuple (and do most of the actual functional tests)
        ([(Range(1, 2), "dummy1")], "{{[1, 2)}: dummy1}", "RangeDict{RangeSet{Range[1, 2)}: 'dummy1'}", False, 1, None),
        ([("[1, 2)", "dummy1")], "{{[1, 2)}: dummy1}", "RangeDict{RangeSet{Range[1, 2)}: 'dummy1'}", False, 1, None),
        ([(Range(1, 1), "dummy1")], "{}", "RangeDict{}", True, 0, None),  # empty ranges are removed in most operations
        ([(Range(1, 2), "d1"), (Range(2, 3), "d2"), (Range(3, 4), "d3")],
            "{{[1, 2)}: d1, {[2, 3)}: d2, {[3, 4)}: d3}",
            "RangeDict{RangeSet{Range[1, 2)}: 'd1', RangeSet{Range[2, 3)}: 'd2', RangeSet{Range[3, 4)}: 'd3'}",
            False, 3, None),
        ([(RangeSet(Range(1, 2), Range(3, 4)), "d1"), (Range(2, 3), "d2")],
            "{{[1, 2), [3, 4)}: d1, {[2, 3)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4)}: 'd1', RangeSet{Range[2, 3)}: 'd2'}", False, 2, None),
        ([(RangeSet(Range(1, 2), Range(2, 3)), "d1"), (Range(3, 4), "d2")],
            "{{[1, 3)}: d1, {[3, 4)}: d2}", "RangeDict{RangeSet{Range[1, 3)}: 'd1', RangeSet{Range[3, 4)}: 'd2'}",
            False, 2, None),
        ([(Range(1, 2), 'd1'), (Range(2, 3), 'd1'), (Range(3, 4), 'd2')],
            "{{[1, 3)}: d1, {[3, 4)}: d2}", "RangeDict{RangeSet{Range[1, 3)}: 'd1', RangeSet{Range[3, 4)}: 'd2'}",
            False, 2, None),
        ([(Range(1, 2), 'd1'), (Range(2, 3), 'd2'), (Range(3, 4), 'd1')],
            "{{[1, 2), [3, 4)}: d1, {[2, 3)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4)}: 'd1', RangeSet{Range[2, 3)}: 'd2'}", False, 2, None),
        ([(Range(1, 4), 'd1'), (Range(2, 3), 'd2')], "{{[1, 2), [3, 4)}: d1, {[2, 3)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4)}: 'd1', RangeSet{Range[2, 3)}: 'd2'}", False, 2, None),
        ([(Range(1, 6), 'd1'), ([Range(2, 3), Range(4, 5)], 'd2')],
            "{{[1, 2), [3, 4), [5, 6)}: d1, {[2, 3), [4, 5)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4), Range[5, 6)}: 'd1', " +
            "RangeSet{Range[2, 3), Range[4, 5)}: 'd2'}", False, 2, None),
        ([([Range(1, 2), Range('a', 'b')], "dummy")], "{{[1, 2), [a, b)}: dummy}",
            "RangeDict{RangeSet{Range[1, 2), Range['a', 'b')}: 'dummy'}", False, 1, None),
        ([(Range(1, 4), 'd1'), (Range(2, 3), 'd2'), (Range('a', 'd'), 'd1'), (Range('b', 'c'), 'd2')],
            "{{[1, 2), [3, 4), [a, b), [c, d)}: d1, {[2, 3), [b, c)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4), Range['a', 'b'), Range['c', 'd')}: 'd1', " +
            "RangeSet{Range[2, 3), Range['b', 'c')}: 'd2'}", False, 2, None),
        ([(Range(1, 4), 'd1'), (Range(2, 3), 'd2'), (Range('b', 'c'), 'd2'), (Range('a', 'd'), 'd1')],
            "{{[1, 2), [3, 4), [a, d)}: d1, {[2, 3)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4), Range['a', 'd')}: 'd1', RangeSet{Range[2, 3)}: 'd2'}",
            False, 2, None),  # order matters
        ([(Range(2, 3), 'd2'), (Range('b', 'c'), 'd2'), ([Range(1, 4), Range('a', 'd')], 'd1')],
            "{{[1, 4), [a, d)}: d1}", "RangeDict{RangeSet{Range[1, 4), Range['a', 'd')}: 'd1'}", False, 1, None),
        # construct via dict
        ({Range(1, 2): "dummy1"}, "{{[1, 2)}: dummy1}", "RangeDict{RangeSet{Range[1, 2)}: 'dummy1'}", False, 1, None),
        ({"[1, 2)": "dummy1"}, "{{[1, 2)}: dummy1}", "RangeDict{RangeSet{Range[1, 2)}: 'dummy1'}", False, 1, None),
        ({Range(1, 2): "d1", Range(2, 3): "d2", Range(3, 4): "d3"},
            "{{[1, 2)}: d1, {[2, 3)}: d2, {[3, 4)}: d3}",
            "RangeDict{RangeSet{Range[1, 2)}: 'd1', RangeSet{Range[2, 3)}: 'd2', RangeSet{Range[3, 4)}: 'd3'}",
            False, 3, None),
        ({RangeSet(Range(1, 2), Range(3, 4)): "d1", Range(2, 3): "d2"},
            "{{[1, 2), [3, 4)}: d1, {[2, 3)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4)}: 'd1', RangeSet{Range[2, 3)}: 'd2'}", False, 2, None),
        ({(Range(1, 2), Range(3, 4)): "d1", Range(2, 3): "d2"},
            "{{[1, 2), [3, 4)}: d1, {[2, 3)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4)}: 'd1', RangeSet{Range[2, 3)}: 'd2'}", False, 2, None),
        ({(Range(1, 2), Range('a', 'b')): "d1", Range(2, 3): "d2"},
            "{{[1, 2), [a, b)}: d1, {[2, 3)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range['a', 'b')}: 'd1', RangeSet{Range[2, 3)}: 'd2'}", False, 2, None),
        ({Range(1, 2): 'd1', Range(2, 3): 'd1', Range(3, 4): 'd2'}, "{{[1, 3)}: d1, {[3, 4)}: d2}",
            "RangeDict{RangeSet{Range[1, 3)}: 'd1', RangeSet{Range[3, 4)}: 'd2'}", False, 2, None),
        ({Range(1, 6): 'd1', (Range(2, 3), Range(4, 5)): 'd2'},
            "{{[1, 2), [3, 4), [5, 6)}: d1, {[2, 3), [4, 5)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4), Range[5, 6)}: 'd1', "
            "RangeSet{Range[2, 3), Range[4, 5)}: 'd2'}", False, 2, None),
        ({Range(1, 4): 'd1', Range(2, 3): 'd2', Range('b', 'c'): 'd2', Range('a', 'd'): 'd1'},
            "{{[1, 2), [3, 4), [a, d)}: d1, {[2, 3)}: d2}",
            "RangeDict{RangeSet{Range[1, 2), Range[3, 4), Range['a', 'd')}: 'd1', RangeSet{Range[2, 3)}: 'd2'}",
            False, 2, None),
        ({Range(2, 3): 'd2', Range('b', 'c'): 'd2', (Range(1, 4), Range('a', 'd')): 'd1'},
            "{{[1, 4), [a, d)}: d1}", "RangeDict{RangeSet{Range[1, 4), Range['a', 'd')}: 'd1'}", False, 1, None),
        ({Range(1, 2): datetime.date(2016, 8, 4)}, "{{[1, 2)}: 2016-08-04}",
            "RangeDict{RangeSet{Range[1, 2)}: datetime.date(2016, 8, 4)}", False, 1, None),
        # error - non-iterables
        (1, "", "", None, 0, ValueError),
        ("", "", "", None, 0, ValueError),
        ("ab", "", "", None, 0, ValueError),
        (None, "", "", None, 0, ValueError),
        (Range(1, 2), "", "", None, 0, ValueError),
        # bad iterable length (it's supposed to be an iterable of 2-tuples)
        ([1], "", "", None, 0, ValueError),
        ([Range(1, 2)], "", "", None, 0, ValueError),
        ([Range(1, 2), "dummy"], "", "", None, 0, ValueError),
        ([(Range(1, 2), "dummy", None)], "", "", None, 0, ValueError),  # 3 elements, otherwise valid
        ([(Range(1, 2), "dummy"), None], "", "", None, 0, ValueError),  # second element in iterable is wrong length
        ([(Range(1, 2), "dummy"), (Range(3, 4), "dummy2", None)], "", "", None, 0, ValueError),
        # invalid arguments
        ([("1, 2", "dummy")], "", "", None, 0, ValueError),
        ([(1, "dummy")], "", "", None, 0, ValueError),
        ([((1, 2), "dummy")], "", "", None, 0, ValueError),
        ([("[2, 1)", "dummy")], "", "", None, 0, ValueError),
    ]
)
def test_rangedict_constructor(iterable, strr, reprr, isempty, length, error_type):
    # also tests .__str__(), .__repr__(), .clear(), .isempty(), .copy(), and __bool__()
    # Tests .popempty() as a byproduct.
    # does a pretty good job of testing .add() too, honestly, but that still
    #   gets its own set of tests due to different and more complex logic
    #   being possible when using it outside of __init__().
    # test for error cases
    if error_type is not None:
        asserterror(error_type, RangeDict, (iterable,))
    # test non-error constructors
    else:
        rngdict = RangeDict(iterable)
        dup_rngdict = RangeDict(rngdict)
        copy_rngdict = rngdict.copy()
        # assert regular rangedict is right
        assert(strr == str(rngdict))
        assert(reprr == repr(rngdict))
        assert(isempty == rngdict.isempty())
        assert(isempty != bool(rngdict))
        assert(length == len(rngdict))
        # assert dupe rangedict is right
        assert(strr == str(dup_rngdict))
        assert(reprr == repr(dup_rngdict))
        assert(isempty == dup_rngdict.isempty())
        assert(isempty != bool(dup_rngdict))
        assert(length == len(dup_rngdict))
        # assert copy rangedict is right
        assert(strr == str(copy_rngdict))
        assert(reprr == repr(copy_rngdict))
        assert(isempty == copy_rngdict.isempty())
        assert(isempty != bool(copy_rngdict))
        assert(length == len(copy_rngdict))
        rngdict.clear()
        # assert cleared rangedict is right
        assert("{}" == str(rngdict))
        assert("RangeDict{}" == repr(rngdict))
        assert(rngdict.isempty())
        assert(not bool(rngdict))
        assert(0 == len(rngdict))
        # assert copied rangedict was not affected
        assert(strr == str(dup_rngdict))
        assert(reprr == repr(dup_rngdict))
        assert(isempty == dup_rngdict.isempty())
        assert(isempty != bool(dup_rngdict))
        assert(length == len(dup_rngdict))
    # flat test for no-arguments constructor
    empty_rngdict = RangeDict()
    assert("{}" == str(empty_rngdict))
    assert("RangeDict{}" == repr(empty_rngdict))
    assert(empty_rngdict.isempty())
    assert(not bool(empty_rngdict))
    assert(0 == len(empty_rngdict))


@pytest.mark.parametrize(
    "rngdict,rng,value,before,after,error_type", [
        # add from nothing
        (RangeDict(), Range(1, 2), 1, RangeDict(), RangeDict({"[1, 2)": 1}), None),
        (RangeDict(), "[1, 2)", 1, RangeDict(), RangeDict({"[1, 2)": 1}), None),
        (RangeDict(), RangeSet("[1, 2)"), 1, RangeDict(), RangeDict({"[1, 2)": 1}), None),
        (RangeDict(), RangeSet("[1, 2)", "[3, 4)"), 1, RangeDict(), RangeDict({("[1, 2)", "[3, 4)"): 1}), None),
        (RangeDict(), ["[1, 2)", "[3, 4)"], 1, RangeDict(), RangeDict({("[1, 2)", "[3, 4)"): 1}), None),
        (RangeDict(), Range("a", "b", include_end=True, include_start=False), 1,
            RangeDict(), RangeDict({Range('a', 'b', include_end=True, include_start=False): 1}), None),
        (RangeDict(), Range(1, 2), "one", RangeDict(), RangeDict({"[1, 2)": "one"}), None),
        (RangeDict(), Range(1, 2), datetime.date(2019, 6, 3),
            RangeDict(), RangeDict({"[1, 2)": datetime.date(2019, 6, 3)}), None),
        # add to already-existing single-element RangeDict
        (RangeDict({"[1, 2)": 1}), Range(3, 4), 1,
            RangeDict({"[1, 2)": 1}), RangeDict({("[1, 2)", "[3, 4)"): 1}), None),
        (RangeDict({"[1, 2)": 1}), Range(3, 4), 2,
            RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 1, "[3, 4)": 2}), None),
        (RangeDict({"[1, 2)": 1}), Range(2, 3), 1, RangeDict({"[1, 2)": 1}), RangeDict({"[1, 3)": 1}), None),
        (RangeDict({"[1, 2)": 1}), Range(1, 2), 1, RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 1}), None),
        (RangeDict({"[1, 2)": 1}), Range(1, 2), 2, RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 2}), None),
        (RangeDict({"[1, 3)": 1}), Range(2, 4), 2,
            RangeDict({"[1, 3)": 1}), RangeDict({"[1, 2)": 1, "[2, 4)": 2}), None),
        (RangeDict({"[1, 2)": 1}), Range('a', 'b'), 2,
            RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 1, Range('a', 'b'): 2}), None),
        (RangeDict({"[1, 2)": 1}), Range('a', 'b'), 1,
            RangeDict({"[1, 2)": 1}), RangeDict({("[1, 2)", Range('a', 'b')): 1}), None),
        (RangeDict({Range(): 1}), Range(2, 3), 2,
            RangeDict({"[-inf, inf)": 1}), RangeDict({("[-inf, 2)", "[3, inf)"): 1, "[2, 3)": 2}), None),
        (RangeDict({Range(): 1}), RangeSet("[2, 3)", "[4, 5)"), 2,
            RangeDict({"[-inf, inf)": 1}), RangeDict({("[-inf, 2)", "[3, 4)", "[5, inf)"): 1, ("[2, 3)", "[4, 5)"): 2}),
            None),
        (RangeDict({Range(): 1}), Range("a", "b"), 2,
            RangeDict({"[-inf, inf)": 1}), RangeDict({(Range(end='a'), Range(start='b')): 1, Range('a', 'b'): 2}),
            None),
        (RangeDict({Range(): 1}), RangeSet(Range("a", "b"), Range("c", "d")), 2,
            RangeDict({"[-inf, inf)": 1}),
            RangeDict({(Range(end='a'), Range('b', 'c'), Range(start='d')): 1, (Range('a', 'b'), Range('c', 'd')): 2}),
            None),
        (RangeDict({Range(float('-inf'), float('inf')): 1}), Range("a", "b"), 2,
            RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1, Range('a', 'b'): 2}), None),
        (RangeDict({Range(float('-inf'), float('inf')): 1}), RangeSet(Range("a", "b"), Range("c", "d")), 2,
            RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1, (Range('a', 'b'), Range('c', 'd')): 2}), None),
        # this is a fun special case: removing an empty range. For Range.difference(), it returns a singleton RangeSet.
        # For RangeDict, nothing happens - because the RangeSet gets cleaved in half and then gets sewed back together
        # immediately.
        (RangeDict({"[1, 3)": 1}), Range(2, 2), 2, RangeDict({"[1, 3)": 1}), RangeDict({"[1, 3)": 1}), None),
        # multiple-element RangeDicts
        (RangeDict({("[1, 3)", Range('a', 'c')): 1}), Range(4, 6), 2,
            RangeDict({("[1, 3)", Range('a', 'c')): 1}), RangeDict({("[1, 3)", Range('a', 'c')): 1, "[4, 6)": 2}),
            None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1}), Range(2, 6), 2,
            RangeDict({("[1, 3)", Range('a', 'c')): 1}), RangeDict({("[1, 2)", Range('a', 'c')): 1, "[2, 6)": 2}),
            None),
        (RangeDict({("[1, 4)", Range('a', 'c')): 1}), RangeSet("[0, 2]", "[3, 5]"), 2,
            RangeDict({("[1, 4)", Range('a', 'c')): 1}),
            RangeDict({("(2, 3)", Range('a', 'c')): 1, ("[0, 2]", "[3, 5]"): 2}), None),
        # error conditions
        (RangeDict(), ["[1, 2)", Range('a', 'b')], 1, RangeDict(), "", TypeError),
        (RangeDict(), 1, 1, RangeDict(), "", ValueError),
        (RangeDict(), "1, 2", 1, RangeDict(), "", ValueError),
    ]
)
def test_rangedict_add(rngdict, rng, value, before, after, error_type):
    # also tests .__additem__()
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.add, (rng, value))
        asserterror(error_type, rngdict.__setitem__, (rng, value))
        assert(before == rngdict)
    else:
        copy_rngdict = rngdict.copy()
        assert(before == copy_rngdict)
        rngdict.add(rng, value)
        copy_rngdict[rng] = value
        assert(after == rngdict)
        assert(after == copy_rngdict)


@pytest.mark.parametrize(
    "rngdict,to_update,before,after,error_type", [
        # empty
        (RangeDict(), (), RangeDict(), RangeDict(), None),
        (RangeDict(), {}, RangeDict(), RangeDict(), None),
        (RangeDict(), RangeDict(), RangeDict(), RangeDict(), None),
        # original tests
        (RangeDict(), ((["[3, 5)", Range('c', 'd')], 2),),
            RangeDict(), RangeDict(((["[3, 5)", Range('c', 'd')], 2),)), None),
        (RangeDict(), [(["[3, 5)", Range('c', 'd')], 2)],
            RangeDict(), RangeDict({("[3, 5)", Range('c', 'd')): 2}), None),
        (RangeDict(), {("[3, 5)", Range('c', 'd')): 2}, RangeDict(), RangeDict({("[3, 5)", Range('c', 'd')): 2}), None),
        (RangeDict(), RangeDict({("[3, 5)", Range('c', 'd')): 2}),
            RangeDict(), RangeDict({("[3, 5)", Range('c', 'd')): 2}), None),
        (RangeDict(), (("[3..5)", Range('c', 'd')),), RangeDict(), RangeDict({"[3..5)": Range('c', 'd')}), None),
        (RangeDict(), ((Range('c', 'd'), "[3..5)"),), RangeDict(), RangeDict({Range('c', 'd'): "[3..5)"}), None),
        (RangeDict(), ((RangeSet("[1, 2]", "[3, 4]"), 2),),
            RangeDict(), RangeDict({RangeSet("[1, 2]", "[3, 4]"): 2}), None),
        (RangeDict(), [((("[1, 2)", "[3, 5)"), ("[6, 8)",)), 2)],
            RangeDict(), RangeDict({(("[1, 2)", "[3, 5)"), ("[6, 8)",)): 2}), None),
        (RangeDict(), [(Range(1, 1), "dummy")], RangeDict(), RangeDict(), None),
        # original tests on multi-element RangeDicts
        (RangeDict({("[1, 3)", Range('a', 'c')): 1}), [(["[3, 5)", Range('c', 'd')], 2)],
            RangeDict({("[1, 3)", Range('a', 'c')): 1}),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, ("[3, 5)", Range('c', 'd')): 2}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1}), [(["[1, 3)", Range('a', 'c')], 2)],
            RangeDict({("[1, 3)", Range('a', 'c')): 1}), RangeDict({("[1, 3)", Range('a', 'c')): 2}), None),
        (RangeDict({("[1, 4)", Range('a', 'd')): 1}), [(["[2, 3)", Range('b', 'c')], 2)],
            RangeDict({("[1, 4)", Range('a', 'd')): 1}),
            RangeDict({("[1, 2)", "[3, 4)", Range('a', 'b'), Range('c', 'd')): 1, ("[2, 3)", Range('b', 'c')): 2}),
            None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1}), [(["[3, 5)", Range('a', 'd')], 2)],
            RangeDict({("[1, 3)", Range('a', 'c')): 1}),
            RangeDict({"[1, 3)": 1, ("[3, 5)", Range('a', 'd')): 2}), None),
        # error conditions
        (RangeDict(), Range(), RangeDict(), "", ValueError),
        (RangeDict(), "[3, 5)", RangeDict(), "", ValueError),
        (RangeDict(), (("[3..5)", Range('c', 'd')), 2), RangeDict(), "", ValueError),  # second element isn't Range
        (RangeDict(), ((Range('c', 'd'), "[3..5)"), 2), RangeDict(), "", ValueError),
        (RangeDict(), [(((("[1, 2)", "[3, 5)"), ("[6, 8)",)),), 2)], RangeDict(), "", ValueError),  # too much nesting
    ]
)
def test_rangedict_update(rngdict, to_update, before, after, error_type):
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.update, (to_update,))
        assert(before == rngdict)
    else:
        rngdict.update(to_update)
        assert(after == rngdict)


@pytest.mark.parametrize(
    "rngdict,item,new_value,before,after,error_type", [
        # simple single-value changing
        (RangeDict({"[1, 3)": 2}), 2, None, RangeDict({"[1, 3)": 2}), RangeDict({"[1, 3)": None}), None),
        (RangeDict({"[1, 3)": 2}), 2, 3, RangeDict({"[1, 3)": 2}), RangeDict({"[1, 3)": 3}), None),
        (RangeDict({"[1, 3)": 2}), 2, "potato", RangeDict({"[1, 3)": 2}), RangeDict({"[1, 3)": "potato"}), None),
        # multiple keys, only change one
        (RangeDict({"[1, 3)": 2, "[4, 6)": 3}), 2, 6,
            RangeDict({"[1, 3)": 2, "[4, 6)": 3}), RangeDict({"[1, 3)": 6, "[4, 6)": 3}), None),
        (RangeDict({"[1, 3)": 2, "[4, 6)": 3}), 5, 6,
            RangeDict({"[1, 3)": 2, "[4, 6)": 3}), RangeDict({"[1, 3)": 2, "[4, 6)": 6}), None),
        (RangeDict({"[1, 3)": 2, Range('a', 'b'): 3}), 2, 6,
            RangeDict({"[1, 3)": 2, Range('a', 'b'): 3}), RangeDict({Range('a', 'b'): 3, "[1, 3)": 6}), None),
        (RangeDict({"[1, 3)": 2, Range('a', 'b'): 3}), 'apple', 6,
            RangeDict({"[1, 3)": 2, Range('a', 'b'): 3}), RangeDict({Range('a', 'b'): 6, "[1, 3)": 2}), None),
        (RangeDict({"[1, 3)": 2, Range('a', 'b'): 3}), Range(1, 2), 6,
            RangeDict({"[1, 3)": 2, Range('a', 'b'): 3}), RangeDict({Range('a', 'b'): 3, "[1, 3)": 6}), None),
        (RangeDict({"[1, 3)": 2, Range('a', 'b'): 3}), RangeSet("[1.5, 2]", "[2.25, 2.75]"), 6,
            RangeDict({"[1, 3)": 2, Range('a', 'b'): 3}), RangeDict({Range('a', 'b'): 3, "[1, 3)": 6}), None),
        # multiple ranges, change all of them
        (RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 3}), 1.5, 6,
            RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 3}),
            RangeDict({RangeSet("[1, 2)", "[3, 4)"): 6, RangeSet("[2, 3)", "[4, 5)"): 3}), None),
        (RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 3}), 2.5, 6,
            RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 3}),
            RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 6}), None),
        (RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 3}), 2, 6,
            RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 3}),
            RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 6}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), 2, 6,
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 6, ("[4, 6)", Range('c', 'e')): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), 'b', 6,
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 6, ("[4, 6)", Range('c', 'e')): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), 5, 6,
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 6}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), 'd', 6,
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 6}), None),
        # range-merging
        (RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), 2, 3,
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}),
            RangeDict({("[1, 3)", "[4, 6)", Range('a', 'e')): 3}), None),
        (RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), 2, 3,
            RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), RangeDict({"[1, 2)": 1, "[2, 4)": 3}), None),
        (RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), 3, 1,
            RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}),
            RangeDict({("[1, 2)", "[3, 4)"): 1, "[2, 3)": 2}), None),
        # error conditions
        (RangeDict(), None, None, RangeDict(), "", KeyError),
        (RangeDict({"[1, 3)": 2}), None, None, RangeDict({"[1, 3)": 2}), "", KeyError),
        (RangeDict({"[1, 3)": 2}), 0.999, None, RangeDict({"[1, 3)": 2}), "", KeyError),
        (RangeDict({"[1, 3)": 2}), 72, None, RangeDict({"[1, 3)": 2}), "", KeyError),
        (RangeDict({"[1, 3)": 2}), 3, None, RangeDict({"[1, 3)": 2}), "", KeyError),
        (RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 3}), 0, 6,
            RangeDict({RangeSet("[1, 2)", "[3, 4)"): 2, RangeSet("[2, 3)", "[4, 5)"): 3}), "", KeyError),
        (RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), 'e', 6,
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), "", KeyError),
        (RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), datetime.date(2019, 6, 13), 6,
            RangeDict({("[1, 3)", Range('a', 'c')): 2, ("[4, 6)", Range('c', 'e')): 3}), "", KeyError),
    ]
)
def test_rangedict_set(rngdict, item, new_value, before, after, error_type):
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.set, (item, new_value))
        assert(before == rngdict)
    else:
        rngdict.set(item, new_value)
        assert(after == rngdict)


@pytest.mark.parametrize(
    "rngdict,old,new,before,after,error_type", [
        # single-element replacement, type checking
        (RangeDict({"[1, 2)": 1}), 1, 2, RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 2}), None),
        (RangeDict({"[1, 2)": 1}), 1, None, RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": None}), None),
        (RangeDict({"[1, 2)": 1}), 1, datetime.date(2018, 5, 23),
            RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": datetime.date(2018, 5, 23)}), None),
        (RangeDict({"[1, 2)": None}), None, 1, RangeDict({"[1 ,2)": None}), RangeDict({"[1, 2)": 1}), None),
        (RangeDict({"[1, 2)": datetime.date(2018, 5, 23)}), datetime.date(2018, 5, 23), 63,
            RangeDict({"[1, 2)": datetime.date(2018, 5, 23)}), RangeDict({"[1, 2)": 63}), None),
        # multi-element
        (RangeDict({"[1, 2)": 1, "[2, 3)": 2}), 1, 3,
            RangeDict({"[1, 2)": 1, "[2, 3)": 2}), RangeDict({"[1, 2)": 3, "[2, 3)": 2}), None),
        (RangeDict({"[1, 2)": 1, "[2, 3)": 2}), 2, 3,
            RangeDict({"[1, 2)": 1, "[2, 3)": 2}), RangeDict({"[1, 2)": 1, "[2, 3)": 3}), None),
        (RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), 1, 4, RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}),
            RangeDict({"[1, 2)": 4, "[2, 3)": 2, "[3, 4)": 3}), None),
        (RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), 1, 3, RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}),
            RangeDict({("[1, 2)", "[3, 4)"): 3, "[2, 3)": 2}), None),
        (RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), 1, 2,
            RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), RangeDict({"[1, 3)": 2, "[3, 4)": 3}), None),
        (RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), 2, 3,
            RangeDict({"[1, 2)": 1, "[2, 3)": 2, "[3, 4)": 3}), RangeDict({"[1, 2)": 1, "[2, 4)": 3}), None),
        (RangeDict({("[1, 2)", "[3, 4)"): 1, "[2, 3)": 2}), 1, 3,
            RangeDict({("[1, 2)", "[3, 4)"): 1, "[2, 3)": 2}), RangeDict({("[1, 2)", "[3, 4)"): 3, "[2, 3)": 2}), None),
        (RangeDict({("[1, 2)", "[3, 4)"): 1, "[2, 3)": 2}), 2, 1,
            RangeDict({("[1, 2)", "[3, 4)"): 1, "[2, 3)": 2}), RangeDict({"[1, 4)": 1}), None),
        (RangeDict({("[1, 2)", "(3, 4)"): 1, "[2, 3)": 2}), 2, 1,
            RangeDict({("[1, 2)", "(3, 4)"): 1, "[2, 3)": 2}), RangeDict({("[1, 3)", "(3, 4)"): 1}), None),
        (RangeDict({("[1, 2)", "[3, 4)"): 1, "[2, 3)": 2, "[4, 5)": 3}), 2, 1,
            RangeDict({("[1, 2)", "[3, 4)"): 1, "[2, 3)": 2, "[4, 5)": 3}),
            RangeDict({"[1, 4)": 1, "[4, 5)": 3}), None),
        # error cases
        (RangeDict(), None, 4, RangeDict(), "", KeyError),
        (RangeDict({"[1, 2)": 1}), 1.5, 4, RangeDict({"[1, 2)": 1}), "", KeyError),
        (RangeDict({"[1, 2)": 1}), 'carrot', 4, RangeDict({"[1, 2)": 1}), "", KeyError),
    ]
)
def test_rangedict_setvalue(rngdict, old, new, before, after, error_type):
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.setvalue, (old, new))
        assert(before == rngdict)
    else:
        rngdict.setvalue(old, new)
        assert(after == rngdict)


@pytest.mark.parametrize(
    "rngdict,key,expected,before,after,error_type", [
        # normal use cases
        (RangeDict({"[1, 3)": 1}), 2, 1, RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 1.5, 1, RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 2.25, 1, RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 1, 1, RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 2, 1,
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[3, 5)": 2}), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 4, 2,
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[1, 3)": 1}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 2, 1,
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 'b', 1,
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 4, 2,
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 'd', 3,
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, ("[1, 3)", Range('a', 'c')): 1}), None),
        # infinity shenanigans
        (RangeDict({Range(): 1}), 1, 1, RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), None, 1, RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), datetime.date(2017, 8, 24), 1, RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), "xkcd", 1, RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 0, 1,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({"[1, 4)": 2, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 2, 2,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'b', 3,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2}), None),
        # error cases
        (RangeDict(), 1, "", RangeDict(), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 3, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 0, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 'zaire', 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'zaire', 1,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}), "", KeyError),
    ]
)
def test_rangedict_pop(rngdict, key, expected, before, after, error_type):
    # also tests .get()
    # all of these methods test .popitem() by extension, so we're not testing.popitem() explicitly
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.get, (key,))
        asserterror(error_type, rngdict.pop, (key,))
        asserterror(error_type, rngdict.__getitem__, (key,))
        assert(before == rngdict)
    else:
        assert(expected == rngdict.get(key))
        assert(before == rngdict)
        assert(expected == rngdict[key])
        assert(before == rngdict)
        assert(expected == rngdict.pop(key))
        assert(after == rngdict)


@pytest.mark.parametrize(
    "rngdict,key,default", [
        (RangeDict(), 1, "polo"),
        (RangeDict(), 1, None),
        (RangeDict(), 1, 42),
        (RangeDict({"[1, 3)": 1}), 3, "fish"),
        (RangeDict({"[1, 3)": 1}), 0, "artistic"),
        (RangeDict({"[1, 3)": 1}), "al-queda", datetime.date(2001, 9, 11)),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'zaire', "Democratic Republic of the Congo"),
    ]
)
def test_rangedict_pop_default(rngdict, key, default):
    # because modifying test_rangedict_pop() to also include testing the default value was too much trouble
    # this method should be outright incapable of throwing an error
    before = rngdict.copy()
    asserterror(KeyError, rngdict.get, (key,))
    assert(default == rngdict.get(key, default))
    assert(before == rngdict)
    asserterror(KeyError, rngdict.pop, (key,))
    assert(before == rngdict)
    assert(default == rngdict.pop(key, default))
    assert(before == rngdict)


@pytest.mark.parametrize(
    "rngdict,key,expected,before,after,error_type", [
        # test cases carried over from test_rangedict_pop() and repurposed, because that should be sufficient
        # normal use cases
        (RangeDict({"[1, 3)": 1}), 2, Range(1, 3), RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 1.5, Range(1, 3), RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 2.25, Range(1, 3), RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 1, Range(1, 3), RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 2, Range(1, 3),
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[3, 5)": 2}), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 4, Range(3, 5),
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[1, 3)": 1}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 2, Range(1, 3),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 'b', Range('a', 'c'),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 4, Range(3, 5),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 'd', Range('c', 'e'),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, ("[1, 3)", Range('a', 'c')): 1}), None),
        # infinity shenanigans
        (RangeDict({Range(): 1}), 1, Range(), RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), None, Range(), RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), datetime.date(2017, 8, 24), Range(), RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), "xkcd", Range(), RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 0, Range(end=1),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({"[1, 4)": 2, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 5, Range(start=4),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({"[1, 4)": 2, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 2, Range(1, 4),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'b', Range('a', 'c'),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2}), None),
        # complex test cases
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         0, Range(end=1),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         4, Range(3, 5),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         8, Range(start=7),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         2, Range(1, 3),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         6, Range(5, 7),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         'b', Range('a', 'c'),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         'f', Range('e', 'g'),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         '`', Range(end='a'),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         'd', Range('c', 'e'),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         'z', Range(start='g'),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
         None),
        # error cases
        (RangeDict(), 1, "", RangeDict(), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 3, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 0, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 'zaire', 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'zaire', 1,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}), "", KeyError),
    ]
)
def test_rangedict_poprange(rngdict, key, expected, before, after, error_type):
    # also tests .getrange()
    assert (before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.getrange, (key,))
        asserterror(error_type, rngdict.poprange, (key,))
        assert (before == rngdict)
    else:
        assert (expected == rngdict.getrange(key))
        assert (before == rngdict)
        assert (expected == rngdict.poprange(key))
        assert (after == rngdict)


@pytest.mark.parametrize(
    "rngdict,key,expected,before,after,error_type", [
        # normal use cases
        (RangeDict({"[1, 3)": 1}), 2, RangeSet("[1, 3)"), RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 1.5, RangeSet("[1, 3)"), RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 2.25, RangeSet("[1, 3)"), RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 1, RangeSet("[1, 3)"), RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 2, RangeSet("[1, 3)"),
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[3, 5)": 2}), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 4, RangeSet("[3, 5)"),
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[1, 3)": 1}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 2, RangeSet("[1, 3)"),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 'b', RangeSet(Range('a', 'c')),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 4, RangeSet("[3, 5)"),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 'd', RangeSet(Range('c', 'e')),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, ("[1, 3)", Range('a', 'c')): 1}), None),
        # infinity shenanigans
        (RangeDict({Range(): 1}), 1, RangeSet(Range()), RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), None, RangeSet(Range()), RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), datetime.date(2017, 8, 24), RangeSet(Range()), RangeDict({Range(): 1}), RangeDict(),
            None),
        (RangeDict({Range(): 1}), "xkcd", RangeSet(Range()), RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 0, RangeSet(Range(end=1), Range(start=4)),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({"[1, 4)": 2, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 5, RangeSet(Range(end=1), Range(start=4)),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({"[1, 4)": 2, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 2, RangeSet("[1, 4)"),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'b', RangeSet(Range('a', 'c')),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2}), None),
        # complex test cases
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            0, RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            4, RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            8, RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            2, RangeSet("[1, 3)", "[5, 7)"),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            6, RangeSet("[1, 3)", "[5, 7)"),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            'b', RangeSet(Range('a', 'c'), Range('e', 'g')),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            'f', RangeSet(Range('a', 'c'), Range('e', 'g')),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            '`', RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g')),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            'd', RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g')),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            'z', RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g')),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
         None),
        # error cases
        (RangeDict(), 1, "", RangeDict(), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 3, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 0, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 'zaire', 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'zaire', 1,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}), "", KeyError),
    ]
)
def test_rangedict_poprangeset(rngdict, key, expected, before, after, error_type):
    # also tests .getrangeset()
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.getrangeset, (key,))
        asserterror(error_type, rngdict.poprangeset, (key,))
        assert(before == rngdict)
    else:
        assert(expected == rngdict.getrangeset(key))
        assert(before == rngdict)
        assert(expected == rngdict.poprangeset(key))
        assert(after == rngdict)


@pytest.mark.parametrize(
    "rngdict,key,expected,before,after,error_type", [
        # normal use cases
        (RangeDict({"[1, 3)": 1}), 2, [RangeSet("[1, 3)")], RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 1.5, [RangeSet("[1, 3)")], RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 2.25, [RangeSet("[1, 3)")], RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1}), 1, [RangeSet("[1, 3)")], RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 2, [RangeSet("[1, 3)")],
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[3, 5)": 2}), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 4, [RangeSet("[3, 5)")],
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[1, 3)": 1}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 2,
            [RangeSet("[1, 3)"), RangeSet(Range('a', 'c'))],
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 'b',
            [RangeSet("[1, 3)"), RangeSet(Range('a', 'c'))],
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 4, [RangeSet("[3, 5)")],
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 'd', [RangeSet(Range('c', 'e'))],
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, ("[1, 3)", Range('a', 'c')): 1}), None),
        # infinity shenanigans
        (RangeDict({Range(): 1}), 1, [RangeSet(Range())], RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), None, [RangeSet(Range())], RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1}), datetime.date(2017, 8, 24), [RangeSet(Range())], RangeDict({Range(): 1}), RangeDict(),
            None),
        (RangeDict({Range(): 1}), "xkcd", [RangeSet(Range())], RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 0, [RangeSet(Range(end=1), Range(start=4))],
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({"[1, 4)": 2, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 5, [RangeSet(Range(end=1), Range(start=4))],
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({"[1, 4)": 2, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 2, [RangeSet("[1, 4)")],
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'b', [RangeSet(Range('a', 'c'))],
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2}), None),
        # complex test cases
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            0, [RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
                RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            4, [RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
                RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            8, [RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
                RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            2, [RangeSet("[1, 3)", "[5, 7)"), RangeSet(Range('a', 'c'), Range('e', 'g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            6, [RangeSet("[1, 3)", "[5, 7)"), RangeSet(Range('a', 'c'), Range('e', 'g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            'b', [RangeSet("[1, 3)", "[5, 7)"), RangeSet(Range('a', 'c'), Range('e', 'g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            'f', [RangeSet("[1, 3)", "[5, 7)"), RangeSet(Range('a', 'c'), Range('e', 'g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            '`', [RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
                  RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            'd', [RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
                  RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            'z', [RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
                  RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
         None),
        # error cases
        (RangeDict(), 1, "", RangeDict(), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 3, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 0, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 'zaire', 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'zaire', 1,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}), "", KeyError),
    ]
)
def test_rangedict_poprangesets(rngdict, key, expected, before, after, error_type):
    # also tests .getrangesets()
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.getrangesets, (key,))
        asserterror(error_type, rngdict.poprangesets, (key,))
        assert(before == rngdict)
    else:
        assert(expected == rngdict.getrangesets(key))
        assert(before == rngdict)
        assert(expected == rngdict.poprangesets(key))
        assert(after == rngdict)


@pytest.mark.parametrize(
    "rngdict,value,expected,before,after,error_type", [
        # normal use cases
        (RangeDict({"[1, 3)": 1}), 1, [RangeSet("[1, 3)")], RangeDict({"[1, 3)": 1}), RangeDict(), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 1, [RangeSet("[1, 3)")],
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[3, 5)": 2}), None),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), 2, [RangeSet("[3, 5)")],
            RangeDict({"[1, 3)": 1, "[3, 5)": 2}), RangeDict({"[1, 3)": 1}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 1,
            [RangeSet("[1, 3)"), RangeSet(Range('a', 'c'))],
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 2, [RangeSet("[3, 5)")],
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({("[1, 3)", Range('a', 'c')): 1, Range('c', 'e'): 3}), None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}), 3, [RangeSet(Range('c', 'e'))],
            RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 5)": 2, Range('c', 'e'): 3}),
            RangeDict({"[3, 5)": 2, ("[1, 3)", Range('a', 'c')): 1}), None),
        # infinity shenanigans
        (RangeDict({Range(): 1}), 1, [RangeSet(Range())], RangeDict({Range(): 1}), RangeDict(), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 1, [RangeSet(Range(end=1), Range(start=4))],
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({"[1, 4)": 2, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 2, [RangeSet("[1, 4)")],
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, Range('a', 'c'): 3}), None),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 3, [RangeSet(Range('a', 'c'))],
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}),
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2}), None),
        # complex test cases
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            2, [RangeSet(Range(end=1), "[3, 5)", Range(start=7)),
                RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1}),
            None),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            1, [RangeSet("[1, 3)", "[5, 7)"), RangeSet(Range('a', 'c'), Range('e', 'g'))],
            RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                       (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            RangeDict({(Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
            None),
        # error cases
        (RangeDict(), 1, "", RangeDict(), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 3, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), None, 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({"[1, 3)": 1}), 'zaire', 1, RangeDict({"[1, 3)": 1}), "", KeyError),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 2.5, 1,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}), "", KeyError),
        (RangeDict({Range(): 1, "[1, 4)": 2, Range('a', 'c'): 3}), 'b', 1,
            RangeDict({(Range(end=1), Range(start=4)): 1, "[1, 4)": 2, Range('a', 'c'): 3}), "", KeyError),
    ]
)
def test_rangedict_popvalue(rngdict, value, expected, before, after, error_type):
    # also tests .getvalue()
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.getvalue, (value,))
        asserterror(error_type, rngdict.popvalue, (value,))
        assert(before == rngdict)
    else:
        assert(expected == rngdict.getvalue(value))
        assert(before == rngdict)
        assert(expected == rngdict.popvalue(value))
        assert(after == rngdict)


@pytest.mark.parametrize(
    "rngdict,to_remove,before,after,error_type", [
        (RangeDict(), Range(), RangeDict(), RangeDict(), None),
        (RangeDict(), Range(1, 3), RangeDict(), RangeDict(), None),
        (RangeDict(), Range('alpha', 'zeta'), RangeDict(), RangeDict(), None),
        (RangeDict({"[1, 4)": 1, "[4, 8)": 2}), Range(2, 3),
            RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeDict({("[1, 2)", "[3, 4)"): 1, "[4, 8)": 2}), None),
        (RangeDict({"[1, 4)": 1, "[4, 8)": 2}), Range(0, 2, include_end=True),
            RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeDict({"(2, 4)": 1, "[4, 8)": 2}), None),
        (RangeDict({"[1, 4)": 1, "[4, 8)": 2}), Range(3, 5),
            RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeDict({"[1, 3)": 1, "[5, 8)": 2}), None),
        (RangeDict({"[1, 4)": 1, "[4, 8)": 2}), Range(0, 5),
            RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeDict({"[5, 8)": 2}), None),
        (RangeDict({"[1, 4)": 1, "[4, 8)": 2}), Range(3, 3),
            RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeDict({"[1, 4)": 1, "[4, 8)": 2}), None),
        (RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeSet(Range(2, 3), Range(5, 6)),
            RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeDict({("[1, 2)", "[3, 4)"): 1, ("[4, 5)", "[6, 8)"): 2}), None),
        (RangeDict({"[1, 4)": 1, "[4, 8)": 2}), Range('a', 'z'),
            RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeDict({"[1, 4)": 1, "[4, 8)": 2}), None),
        (RangeDict({"[1, 4)": 1, "[4, 8)": 2}), Range(), RangeDict({"[1, 4)": 1, "[4, 8)": 2}), RangeDict(), None),
        (RangeDict({("[1, 4)", Range('a', 'd')): 1, ("[4, 8)", Range('d', 'g')): 2}), Range('b', 'c'),
            RangeDict({("[1, 4)", Range('a', 'd')): 1, ("[4, 8)", Range('d', 'g')): 2}),
            RangeDict({("[1, 4)", Range('a', 'b'), Range('c', 'd')): 1, ("[4, 8)", Range('d', 'g')): 2}), None),
        # error conditions
        (RangeDict(), 2, RangeDict(), "", ValueError),
        (RangeDict(), "[4, 2]", RangeDict(), "", ValueError),
        (RangeDict(), "4, 2", RangeDict(), "", ValueError),
    ]
)
def test_rangedict_remove(rngdict, to_remove, before, after, error_type):
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.remove, (to_remove,))
        assert(before == rngdict)
    else:
        rngdict.remove(to_remove)
        assert(after == rngdict)


@pytest.mark.parametrize(
    "rngdict,item,contains", [
        (RangeDict(), 1, False),
        (RangeDict(), None, False),
        (RangeDict(), "nothing", False),
        (RangeDict({Range(): 1}), "everything", True),
        (RangeDict({Range(): 1}), 2, True),
        (RangeDict({Range(): 1}), None, True),
        (RangeDict({Range(): 1}), RangeSet("[1, 2)", "[5, 8)"), True),
        (RangeDict({Range(): 1}), ["[1, 2)", Range('a', 'e')], True),
        (RangeDict({Range(): 1}), RangeDict({RangeSet("[1, 2)", "[5, 8)"): 1}), True),
        (RangeDict({Range(): 1}), float('nan'), False),
        (RangeDict({Range(): 1, "[1, 5)": 2}), 2, True),
        (RangeDict({Range(): 1, "[1, 5)": 2}), 9, True),
        (RangeDict({Range(): 1, "[1, 5)": 2}), "some things", False),
        (RangeDict({"[1, 5)": 1, "[7, 12)": 2}), "some things", False),
        (RangeDict({"[1, 5)": 1, "[7, 12)": 2}), 1, True),
        (RangeDict({"[1, 5)": 1, "[7, 12)": 2}), 3, True),
        (RangeDict({"[1, 5)": 1, "[7, 12)": 2}), 5, False),
        (RangeDict({"[1, 5)": 1, "[7, 12)": 2}), Range(8, 10), True),
        (RangeDict({"[1, 5)": 1, "[7, 12)": 2}), RangeSet(Range(8, 10)), True),
        (RangeDict({"[1, 5)": 1, "[7, 12)": 2}), RangeSet(Range(2, 3), Range(8, 10)), False),
        (RangeDict({"[1, 5)": 1, "[7, 12)": 2}), RangeSet(Range(1.5, 2.5), Range(3.5, 4.5)), True),
        (RangeDict({("[1, 5)", Range('a', 'e')): 1, ("[7, 12)", Range('g', 'k')): 2}),
            ["[2, 4)", Range('b', 'd')], False),
        (RangeDict({("[1, 5)", Range('a', 'e')): 1, ("[7, 12)", Range('g', 'k')): 2}), 'b', True),
        (RangeDict({("[1, 5)", Range('a', 'e')): 1, ("[7, 12)", Range('g', 'k')): 2}), 'g', True),
        (RangeDict({("[1, 5)", Range('a', 'e')): 1, ("[7, 12)", Range('g', 'k')): 2}), 'f', False),
        (RangeDict({("[1, 5)", Range('a', 'e')): 1, ("[7, 12)", Range('g', 'k')): 2}), None, False),
    ]
)
def test_rangedict_contains(rngdict, item, contains):
    assert(contains == (item in rngdict))


@pytest.mark.parametrize(
    "rngdict1,rngdict2,equal", [
        (RangeDict(), Range(), False),
        (RangeDict(), RangeSet(), False),
        (RangeDict(), 2, False),
        (RangeDict(), RangeDict(), True),
        (RangeDict({"[1, 3)": 8}), RangeDict({"[1, 3)": 8}), True),
        (RangeDict({"[1, 3)": 8}), RangeDict((("[1, 3)", 8),)), True),
        (RangeDict({"[1, 3)": 8}), RangeDict((("[1, 4)", 8),)), False),
        (RangeDict({"[1, 3)": 8}), RangeDict((("[1, 2.9999999)", 8),)), False),
        (RangeDict({"[1, 3)": 8}), RangeDict({"[1, 2)": 8, "[2, 3)": 8}), True),
        (RangeDict({"[1, 3)": 8}), RangeDict({"[1, 3)": 9}), False),
        (RangeDict({"[1, 3)": 8, Range('a', 'c'): 9}), RangeDict({"[1, 3)": 8}), False),
        (RangeDict({"[1, 3)": 8, Range('a', 'c'): 9}), RangeDict({Range('a', 'c'): 8}), False),
        (RangeDict({"[1, 3)": 8, Range('a', 'c'): 9}), RangeDict({"[1, 3)": 8, Range('a', 'c'): 9}), True),
        (RangeDict({Range(): None}), RangeDict({"[-inf, inf)": None}), True),
    ]
)
def test_rangedict_equals(rngdict1, rngdict2, equal):
    # include .copy() also
    assert(rngdict1 == rngdict1.copy())
    assert(equal == (rngdict1 == rngdict2))
    assert(equal != (rngdict1 != rngdict2))


@pytest.mark.parametrize(
    "rngdict,expected", [
        (RangeDict(), []),
        (RangeDict({"[1, 3)": 1}), [RangeSet(Range(1, 3))]),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), [RangeSet(Range(1, 3)), RangeSet(Range(3, 5))]),
        (RangeDict({"[3, 5)": 2, "[1, 3)": 1}), [RangeSet(Range(1, 3)), RangeSet(Range(3, 5))]),
        (RangeDict({"[4, 6)": 1, Range('a', 'c'): 2, Range('d', 'f'): 3, "[1, 3)": 4}),
         [RangeSet("[1, 3)"), RangeSet("[4, 6)"), RangeSet(Range('a', 'c')), RangeSet(Range('d', 'f'))]),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         [RangeSet(Range(end=1), Range("[3, 5)"), Range(start=7)), RangeSet("[1, 3)", "[5, 7)"),
          RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g')), RangeSet(Range('a', 'c'), Range('e', 'g'))]),
    ]
)
def test_rangedict_ranges(rngdict, expected):
    # this doubles as a test of RangeDict's ordering mechanism
    assert(expected == rngdict.ranges())


@pytest.mark.parametrize(
    "rngdict,expected", [
        (RangeDict(), []),
        (RangeDict({"[1, 3)": 1}), [1]),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), [1, 2]),
        (RangeDict({"[3, 5)": 2, "[1, 3)": 1}), [2, 1]),
        (RangeDict({"[4, 6)": 1, Range('a', 'c'): 2, Range('d', 'f'): 3, "[1, 3)": 4}), [1, 2, 3, 4]),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         [1, 2]),
    ]
)
def test_rangedict_values(rngdict, expected):
    # this doubles as a test of RangeDict's ordering mechanism
    assert(expected == rngdict.values())


@pytest.mark.parametrize(
    "rngdict,expected", [
        (RangeDict(), []),
        (RangeDict({"[1, 3)": 1}), [([RangeSet(Range(1, 3))], 1)]),
        (RangeDict({"[1, 3)": 1, "[3, 5)": 2}), [([RangeSet(Range(1, 3))], 1), ([RangeSet(Range(3, 5))], 2)]),
        (RangeDict({"[3, 5)": 2, "[1, 3)": 1}), [([RangeSet(Range(3, 5))], 2), ([RangeSet(Range(1, 3))], 1)]),
        (RangeDict({"[4, 6)": 1, Range('a', 'c'): 2, Range('d', 'f'): 3, "[1, 3)": 4}),
         [([RangeSet("[4, 6)")], 1), ([RangeSet(Range('a', 'c'))], 2),
          ([RangeSet(Range('d', 'f'))], 3), ([RangeSet("[1, 3)")], 4)]),
        (RangeDict({("[1, 3)", "[5, 7)", Range('a', 'c'), Range('e', 'g')): 1,
                    (Range(end=1), "[3, 5)", Range(start=7), Range(end='a'), Range('c', 'e'), Range(start='g')): 2}),
         [([RangeSet("[1, 3)", "[5, 7)"), RangeSet(Range('a', 'c'), Range('e', 'g'))], 1),
          ([RangeSet(Range(end=1), Range("[3, 5)"), Range(start=7)),
            RangeSet(Range(end='a'), Range('c', 'e'), Range(start='g'))], 2)]),
    ]
)
def test_rangedict_items(rngdict, expected):
    assert(expected == rngdict.items())


def test_issue8():
    # issue: adding a Range to a RangeSet containing two non-overlapping ranges, such that the new range overlaps
    # with one but not the other, leads to a TypeError being raised.
    # cause: code was passing a Linked List Node instead of the node's value (a range)
    try:
        a = RangeSet()
        a.add(Range(100, 300))
        a.add(Range(400, 500))
        a.add(Range(500, 600))
        assert(str(a) == "{[100, 300), [400, 600)}")
        b = RangeSet()
        b.add(Range(400, 600))
        b.add(Range(200, 300))
        b.add(Range(100, 200))
        assert(str(b) == "{[100, 300), [400, 600)}")
    except TypeError:
        fail("RangeSet should not have an issue concatenating to the second range of two in a RangeSet")


def test_rangedict_docstring():
    a = RangeDict()
    assert(str(a) == "{}")
    assert(a.isempty())

    b = RangeDict(a)
    assert(b == a)
    assert(not (b is a))

    c = RangeDict({
        Range('a', 'h'): "First third of the lowercase alphabet",
        Range('h', 'p'): "Second third of the lowercase alphabet",
        Range('p', '{'): "Final third of the lowercase alphabet",
    })
    assert(c['brian'] == "First third of the lowercase alphabet")
    assert(c['king arthur'] == "Second third of the lowercase alphabet")
    assert(c['python'] == "Final third of the lowercase alphabet")

    d = RangeDict([
        (Range('A', 'H'), "First third of the uppercase alphabet"),
        (Range('H', 'P'), "Second third of the uppercase alphabet"),
        (Range('P', '['), "Final third of the uppercase alphabet"),
    ])
    assert(d['Flying Circus'] == "First third of the uppercase alphabet")
    assert(d['Holy Grail'] == "Second third of the uppercase alphabet")
    assert(d['Something Completely Different'] == "Final third of the uppercase alphabet")

    e = RangeDict({Range(include_end=True): "inquisition"})
    assert(str(e) == "{{[-inf, inf]}: inquisition}")  # {{[-inf, inf)}: 'inquisition'}
    assert(e.get(None) == "inquisition")  # inquisition
    assert(e.get(3) == "inquisition")  # inquisition
    assert(e.get("holy") == "inquisition")  # inquisition
    assert(e.get("spanish") == "inquisition")  # inquisition

    e[Range("a", "m")] = "grail"
    assert(str(e) == "{{[-inf, a), [m, inf]}: inquisition, {[a, m)}: grail}")
    assert(e.get("spanish") == "inquisition")  # inquisition
    assert(e.get("holy") == "grail")  # grail
    asserterror(KeyError, e.get, (3,))  # KeyError
    asserterror(KeyError, e.get, (None,))  # KeyError
