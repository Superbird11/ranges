"""
Tests for github issues and bugfixes, specifically
"""
from pytest import fail
from ranges import Range, RangeSet, RangeDict


def test_issue4():
    # issue: a Range that exactly overlaps one exclusive border of a key in a RangeDict
    # does not register as contains
    # cause: Range._above_start() and ._below_end() were disregarding the other Range's inclusivity
    # by not treating the other Range as a Range
    rd = RangeDict({Range(0, 5, include_end=True): 'zero to five inclusive'})
    assert(Range(0, 5, include_end=True) in rd)
    assert(Range(0, 4) in rd)
    assert(Range(1, 4) in rd)
    assert(Range(1, 5, include_end=True) in rd)
    rd2 = RangeDict({Range(0, 5, include_start=False): 'zero to five exclusive'})
    assert(Range(0, 5, include_start=False) in rd2)
    assert(Range(0, 4, include_start=False) in rd2)
    assert(Range(1, 4) in rd2)
    assert(Range(1, 5) in rd2)


def test_issue6():
    # issue: cannot use unhashable types as the value in a RangeDict
    try:
        x = RangeDict({Range(0, 1): ["A", "B"]})
        assert(str(x) == "{{[0, 1)}: ['A', 'B']}")
    except TypeError:
        fail("RangeDict should not raise an error when value is unhashable")


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


def test_issue12():
    # issue: mutating a mutable RangeDict value also affected all keys set to equivalent values.
    # In other words, the RangeDict was compressing equal but not identical values into the same
    # rangekey values. To fix, added a toggle to use identity instead of equality.
    # The code in this test is now also contained in the docstring.
    f = RangeDict({Range(1, 2): {3}, Range(4, 5): {3}})
    assert(str(f) == '{{[1, 2), [4, 5)}: {3}}')
    f[Range(1, 2)] |= {4}
    assert(str(f) == '{{[1, 2), [4, 5)}: {3, 4}}')

    g = RangeDict({Range(1, 2): {3}, Range(4, 5): {3}}, identity=True)
    assert(str(g) == '{{[1, 2)}: {3}, {[4, 5)}: {3}}')

    h = RangeDict({Range(1, 2): {3}, Range(4, 5): {3}})
    assert(str(h) == '{{[1, 2), [4, 5)}: {3}}')
    h[Range(1, 2)] = h[Range(1, 2)] | {4}
    assert(str(h) == '{{[4, 5)}: {3}, {[1, 2)}: {3, 4}}')
