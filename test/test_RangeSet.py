"""
Tests for RangeSet
"""
import pytest
from ranges import Range, RangeSet
import datetime
from .test_base import asserterror


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
    "rngset,expected", [
        # testcases from Range
        (RangeSet(Range()), RangeSet()),  # complement of an infinite range is a range with no elements
        (RangeSet(Range('(5..5)')), RangeSet(Range())),  # complement of an empty range is an infinite range
        (RangeSet(Range('(5..5]')), RangeSet(Range())),
        (RangeSet(Range('[5..5)')), RangeSet(Range())),
        (RangeSet(Range('[5..5]')), RangeSet(Range(end=5), Range(start=5, include_start=False))),  # single point
        (RangeSet(Range(1, 3)), RangeSet(Range(end=1), Range(start=3))),  # complement of normal range
        (RangeSet(Range('[2..3]')), RangeSet(Range('[-inf, 2)'), Range('(3, inf)'))),  # normal range, bounds-check
        (RangeSet(Range('(2..3)')), RangeSet(Range('[-inf, 2]'), Range('[3, inf)'))),
        (RangeSet(Range(end=-1)), RangeSet(Range(start=-1))),  # complement of one-side-infinite range
        (RangeSet(Range(end=-1, include_end=True)), RangeSet(Range(start=-1, include_start=False))),
        (RangeSet(Range(start=1, include_start=False)), RangeSet(Range(end=1, include_end=True))),
        (RangeSet(Range(start=1)), RangeSet(Range(end=1))),
        (RangeSet(Range('inquisition', 'spanish')), RangeSet(Range(end='inquisition'), Range(start='spanish'))),
        (RangeSet(Range('e', 'e', include_start=False)), RangeSet(Range())),
        # new testcases for RangeSet
        (RangeSet(), RangeSet(Range())),
        (RangeSet('[1, 2)', '[3, 4)', '(5, 6)'), RangeSet('[-inf, 1)', '[2, 3)', '[4, 5]', '[6, inf)')),
    ]
)
def test_rangeset_complement(rngset, expected):
    assert(expected == rngset.complement())
    assert(expected == ~rngset)
    rngset.popempty()
    assert(rngset == expected.complement())
    assert(rngset == ~expected)


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
