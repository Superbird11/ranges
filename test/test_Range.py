"""
Testing the Range class
"""
import pytest
from ranges import Range, RangeSet, Inf
import numbers
from decimal import Decimal
import datetime
from .test_base import asserterror


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
        (Range(-3, 3), Range(1, 3), True, "[-3, 3)", "Range[-3, 3)"),  # changed, see issue #4
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
        (Range(1, 2), Range(2, 3), None, None),  # Behavior changed: issue #7
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
        

@pytest.mark.parametrize(
    "rng,expected", [
        (Range(), RangeSet()),  # complement of an infinite range is a range with no elements
        (Range('(5..5)'), RangeSet(Range())),  # complement of an empty range is an infinite range
        (Range('(5..5]'), RangeSet(Range())),
        (Range('[5..5)'), RangeSet(Range())),
        (Range('[5..5]'), RangeSet(Range(end=5), Range(start=5, include_start=False))),  # complement of single point
        (Range(1, 3), RangeSet(Range(end=1), Range(start=3))),  # complement of normal range
        (Range('[2..3]'), RangeSet(Range('[-inf, 2)'), Range('(3, inf)'))),  # complement of normal range, bounds-check
        (Range('(2..3)'), RangeSet(Range('[-inf, 2]'), Range('[3, inf)'))),
        (Range(end=-1), RangeSet(Range(start=-1))),  # complement of one-side-infinite range
        (Range(end=-1, include_end=True), RangeSet(Range(start=-1, include_start=False))),
        (Range(start=1, include_start=False), RangeSet(Range(end=1, include_end=True))),
        (Range(start=1), RangeSet(Range(end=1))),
        (Range('inquisition', 'spanish'), RangeSet(Range(end='inquisition'), Range(start='spanish'))),  # non-numeric
        (Range('e', 'e', include_start=False), RangeSet(Range())),
    ]
)
def test_range_complement(rng, expected):
    assert(expected == rng.complement())
    assert(expected == ~rng)


@pytest.mark.parametrize(
    "rng,value,expected,error_type", [
        # normal tests and boundary-value tests
        (Range(1, 5), 3, 3, None),
        (Range(1, 5), 1, 1, None),
        (Range(1, 5), 5, 5, None),
        (Range(1, 5), 0, 1, None),
        (Range(1, 5), 6, 5, None),
        (Range(1, 5), -Inf, 1, None),
        (Range(1, 5), Inf, 5, None),
        (Range('c', 'f'), 'depo', 'depo', None),
        (Range('c', 'f'), 'caesium', 'caesium', None),
        (Range('c', 'f'), 'frozen', 'f', None),
        (Range('c', 'f'), 'b', 'c', None),
        # infinite range tests
        (Range(), 9173, 9173, None),
        (Range(), 'apples', 'apples', None),
        (Range(), None, None, None),  # the infinity object is great, it doesn't error with non-comparable types
        (Range(), Inf, Inf, None),  # non-comparable type (None)
        # error tests
        (Range(1, 5), 'apple', None, TypeError),  # non-compatible type (int vs string)
        (Range(end=1), None, None, TypeError),   # adding 1 makes it non-comparable despite being infinite
    ]
)
def test_range_clamp(rng, value, expected, error_type):
    if error_type is not None:
        asserterror(error_type, rng.clamp, (value,))
    else:
        assert(expected == rng.clamp(value))


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
