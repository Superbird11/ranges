"""
Tests for RangeDict
"""
import pytest
from ranges import Range, RangeSet, RangeDict
import datetime
from .test_base import asserterror


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
        (RangeDict({"[1, 3)": 1}), Range(4, 4), 2, RangeDict({"[1, 3)": 1}), RangeDict({"[1, 3)": 1}), None),
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
        # adding an infinite range (should always replace the entire contents)
        (RangeDict(), Range(), 1, RangeDict(), RangeDict({Range(): 1}), None),  # to empty
        (RangeDict({"[1, 3)": 1}), Range(), 1, RangeDict({"[1, 3)": 1}), RangeDict({Range(): 1}), None),
        (RangeDict({"[1, 3)": 1}), Range(), 2, RangeDict({"[1, 3)": 1}), RangeDict({Range(): 2}), None),
        (RangeDict({Range('a', 'c'): 1}), Range(), 2, RangeDict({Range('a', 'c'): 1}), RangeDict({Range(): 2}), None),
        (RangeDict({"[1, 3)": 1, Range('a', 'c'): 2}), Range(), 3, RangeDict({"[1, 3)": 1, Range('a', 'c'): 2}),
         RangeDict({Range(): 3}), None),
        (RangeDict({"[1, 3)": 1, Range('a', 'c'): 2}), Range(), 2, RangeDict({"[1, 3)": 1, Range('a', 'c'): 2}),
         RangeDict({Range(): 2}), None),
        (RangeDict({Range(): 1}), Range(), 2, RangeDict({Range(): 1}), RangeDict({Range(): 2}),  None),
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
    "rngdict,rng,value,before,after,error_type", [
        # add from nothing (same as tests for add())
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
         RangeDict({"[1, 2)": 1}), RangeDict({("[1, 2)", "[3, 4)"): 1}), None),  # non-overlapping
        (RangeDict({"[1, 2)": 1}), Range(3, 4), 2,
         RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 1, "[3, 4)": 2}), None),
        (RangeDict({"[1, 2)": 1}), Range(2, 3), 1, RangeDict({"[1, 2)": 1}), RangeDict({"[1, 3)": 1}), None),
        (RangeDict({"[1, 2)": 1}), Range(1, 2), 1, RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 1}), None),
        (RangeDict({"[1, 2)": 1}), Range(1, 2), 2, RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 1}), None),
        (RangeDict({"[1, 3)": 1}), Range(2, 4), 2,
         RangeDict({"[1, 3)": 1}), RangeDict({"[1, 3)": 1, "[3, 4)": 2}), None),
        (RangeDict({"[1, 2)": 1}), Range('a', 'b'), 2,
         RangeDict({"[1, 2)": 1}), RangeDict({"[1, 2)": 1, Range('a', 'b'): 2}), None),
        (RangeDict({"[1, 2)": 1}), Range('a', 'b'), 1,
         RangeDict({"[1, 2)": 1}), RangeDict({("[1, 2)", Range('a', 'b')): 1}), None),
        # adddefault() to an already-infinite set should do nothing
        (RangeDict({Range(): 1}), Range(2, 3), 2, RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1}), None),
        (RangeDict({Range(): 1}), RangeSet("[2, 3)", "[4, 5)"), 2,
         RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1}), None),
        (RangeDict({Range(): 1}), Range("a", "b"), 2,
         RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1}), None),
        (RangeDict({Range(): 1}), RangeSet(Range("a", "b"), Range("c", "d")), 2,
         RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1}), None),
        # however, adddefault() to a set of infinite numbers and nothing else should work normally
        (RangeDict({Range(float('-inf'), float('inf')): 1}), Range("a", "b"), 2,
         RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1, Range('a', 'b'): 2}), None),
        (RangeDict({Range(float('-inf'), float('inf')): 1}), RangeSet(Range("a", "b"), Range("c", "d")), 2,
         RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1, (Range('a', 'b'), Range('c', 'd')): 2}), None),
        (RangeDict({Range(float('-inf'), float('inf')): 1}), Range(1, 2), 2,
         RangeDict({"[-inf, inf)": 1}), RangeDict({"[-inf, inf)": 1}), None),
        # adddefault() empty range should do nothing just as before
        (RangeDict({"[1, 3)": 1}), Range(2, 2), 2, RangeDict({"[1, 3)": 1}), RangeDict({"[1, 3)": 1}), None),
        (RangeDict({"[1, 3)": 1}), Range(4, 4), 2, RangeDict({"[1, 3)": 1}), RangeDict({"[1, 3)": 1}), None),
        # multiple-element RangeDicts
        (RangeDict({("[1, 3)", Range('a', 'c')): 1}), Range(4, 6), 2,
         RangeDict({("[1, 3)", Range('a', 'c')): 1}), RangeDict({("[1, 3)", Range('a', 'c')): 1, "[4, 6)": 2}),
         None),
        (RangeDict({("[1, 3)", Range('a', 'c')): 1}), Range(2, 6), 2,
         RangeDict({("[1, 3)", Range('a', 'c')): 1}), RangeDict({("[1, 3)", Range('a', 'c')): 1, "[3, 6)": 2}),
         None),
        (RangeDict({("[1, 4)", Range('a', 'c')): 1}), RangeSet("[0, 2]", "[3, 5]"), 2,
         RangeDict({("[1, 4)", Range('a', 'c')): 1}),
         RangeDict({("[1, 4)", Range('a', 'c')): 1, ("[0, 1)", "[4, 5]"): 2}), None),
        # adding an infinite range
        (RangeDict(), Range(), 1, RangeDict(), RangeDict({Range(): 1}), None),  # to empty
        (RangeDict({"[1, 3)": 1}), Range(), 1, RangeDict({"[1, 3)": 1}), RangeDict({Range(): 1}), None),  # match value
        (RangeDict({"[1, 3)": 1}), Range(), 2, RangeDict({"[1, 3)": 1}),
         RangeDict({"[1, 3)": 1, ("[-inf, 1)", "[3, inf)"): 2}), None),  # non-matching value, matching type
        (RangeDict({Range('a', 'c'): 1}), Range(), 2, RangeDict({Range('a', 'c'): 1}),
         RangeDict({Range('a', 'c'): 1, (Range(end='a'), Range(start='c')): 2}), None),
        (RangeDict({"[1, 3)": 1, Range('a', 'c'): 2}), Range(), 3, RangeDict({"[1, 3)": 1, Range('a', 'c'): 2}),
         RangeDict({"[1, 3)": 1, Range('a', 'c'): 2,   # should duplicate itself if necessary to fill the space
                    (Range(end=1), Range(start=3), Range(end='a'), Range(start='c')): 3}), None),
        (RangeDict({"[1, 3)": 1, Range('a', 'c'): 2}), Range(), 2, RangeDict({"[1, 3)": 1, Range('a', 'c'): 2}),
         RangeDict({"[1, 3)": 1, Range('a', 'c'): 2,   # should duplicate but also merge
                    (Range(end=1), Range(start=3)): 2, Range(end='a'): 2, Range(start='a'): 2}), None),
        (RangeDict({Range(): 1}), Range(), 2, RangeDict({Range(): 1}), RangeDict({Range(): 1}),  None),  # inf to inf
        # error conditions
        (RangeDict(), ["[1, 2)", Range('a', 'b')], 1, RangeDict(), "", TypeError),
        (RangeDict(), 1, 1, RangeDict(), "", ValueError),
        (RangeDict(), "1, 2", 1, RangeDict(), "", ValueError),
    ]
)
def test_rangedict_adddefault(rngdict, rng, value, before, after, error_type):
    assert(before == rngdict)
    if error_type is not None:
        asserterror(error_type, rngdict.adddefault, (rng, value))
        assert(before == rngdict)
    else:
        rngdict.adddefault(rng, value)
        assert(after == rngdict)


def test_rangedict_multi_infinity():
    # add() and adddefault() shenanigans that can lead to multiple infinite ranges being present
    rngdict = RangeDict({
        Range(1, 3): 1,
        Range('a', 'c'): 2,
        Range((1,), (3,)): 2,
    })
    rngdict.adddefault(Range(), 2)
    assert("{{[1, 3)}: 1, {[-inf, inf), [-inf, inf), [-inf, 1), [3, inf)}: 2}" == str(rngdict))
    rngdict2 = RangeDict({
        Range(end=3): 1,
        Range(end='c'): 2,
        Range(end=(3,)): 2,
    })
    rngdict2.add(Range(start='c'), 2)
    rngdict2.add(Range(start=(3,)), 2)
    assert("{{[-inf, 3)}: 1, {[-inf, inf), [-inf, inf)}: 2}" == str(rngdict2))
    rngdict2[Range(start=3)] = 2
    assert("{{[-inf, 3)}: 1, {[-inf, inf), [-inf, inf), [3, inf)}: 2}" == str(rngdict2))
    rngdict2[Range(end=3)] = 2
    assert("{{[-inf, inf), [-inf, inf), [-inf, inf)}: 2}" == str(rngdict2))


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
    "rngdict,key,expected", [
        (RangeDict(), Range(), []),  # empty rangedict, Range argument
        (RangeDict(), None, []),  # empty rangedict, non-Range argument - should not throw an error
        (RangeDict({Range(1, 3): 2}), Range(2, 4),  # single-element rangedict, Range argument
            [([RangeSet(Range(1, 3))], RangeSet(Range(1, 3)), 2)]),
        (RangeDict({Range(1, 3): 2}), "[2..4)",  # single-element rangedict, Rangelike but non-Range argument
            [([RangeSet(Range(1, 3))], RangeSet(Range(1, 3)), 2)]),
        (RangeDict({Range(1, 3): 2}), 2, ValueError),  # single-element rangedict, non-rangelike argument
        (RangeDict({Range(1, 3): 2}), Range(5, 6), []),  # single-element rangedict, no intersections
        (RangeDict({Range(1, 3): 2}), Range('a', 'b'), []),  # single-element rangedict, wrong type of Rangekey
        (RangeDict({Range(1, 3): 2, Range(5, 7): 6}), Range(2, 4),  # two-element rangedict, one intersection
            [([RangeSet(Range(1, 3))], RangeSet(Range(1, 3)), 2)]),
        (RangeDict({Range(1, 3): 2, Range(5, 7): 6}), Range(2, 6),  # two-element rangedict, two intersections
            [([RangeSet(Range(1, 3))], RangeSet(Range(1, 3)), 2),
             ([RangeSet(Range(5, 7))], RangeSet(Range(5, 7)), 6)]),
        (RangeDict({Range(1, 3): 2, Range(5, 7): 6}), Range(8, 9), []),  # two-element rangedict, no intersections
        (RangeDict({Range(1, 3): 2, Range('a', 'c'): 'b'}), Range(2, 4),  # two types of ranges, one intersection
            [([RangeSet(Range(1, 3))], RangeSet(Range(1, 3)), 2)]),
        (RangeDict({Range(1, 3): 2, Range('a', 'c'): 'b'}), Range(),  # two types of ranges, two intersections
            [([RangeSet(Range(1, 3))], RangeSet(Range(1, 3)), 2),
             ([RangeSet(Range('a', 'c'))], RangeSet(Range('a', 'c')), 'b')]),
        (RangeDict({Range(1, 3): 2, Range(5, 7): 6, Range('a', 'c'): 2}), Range(2, 4),  # multiple rngtypes, same value
            [([RangeSet(Range(1, 3)), RangeSet(Range('a', 'c'))], RangeSet(Range(1, 3)), 2)]),
        (RangeDict({Range(1, 3): 2, Range(3, 5): 4, Range(5, 7): 2}), Range(2, 4),  # interspersed ranges 1
            [([RangeSet(Range(1, 3), Range(5, 7))], RangeSet(Range(1, 3), Range(5, 7)), 2),  # (two keys one rangeset)
             ([RangeSet(Range(3, 5))], RangeSet(Range(3, 5)), 4)]),
        (RangeDict({Range(1, 3): 2, Range(3, 5): 4, Range(5, 7): 2}), Range(3.5, 4.5),  # interspersed ranges 2
            [([RangeSet(Range(3, 5))], RangeSet(Range(3, 5)), 4)]),
        (RangeDict({Range(1, 3): 2, Range(5, 7): 6, Range('a', 'c'): 2}), Range(),  # multiple hits
            [([RangeSet(Range(1, 3)), RangeSet(Range('a', 'c'))], RangeSet(Range(1, 3)), 2),
             ([RangeSet(Range(5, 7))], RangeSet(Range(5, 7)), 6),
             ([RangeSet(Range(1, 3)), RangeSet(Range('a', 'c'))], RangeSet(Range('a', 'c')), 2)]),
    ]
)
def test_rangedict_getoverlap(rngdict, key, expected):
    if isinstance(expected, type):
        asserterror(expected, rngdict.getoverlapitems, (key,))
        asserterror(expected, rngdict.getoverlap, (key,))
        asserterror(expected, rngdict.getoverlapranges, (key,))
        asserterror(expected, rngdict.getoverlaprangesets, (key,))
    else:
        assert(expected == rngdict.getoverlapitems(key))
        assert([e[0] for e in expected] == rngdict.getoverlaprangesets(key))
        assert([e[1] for e in expected] == rngdict.getoverlapranges(key))
        assert([e[2] for e in expected] == rngdict.getoverlap(key))


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
