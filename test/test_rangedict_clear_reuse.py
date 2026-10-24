import pytest

from ranges import Range, RangeDict


@pytest.mark.parametrize('identity', [False, True])
@pytest.mark.parametrize('value', [['new'], {'new'}, {'new': 1}])
def test_clear_can_reuse_unhashable_values(identity, value):
    mapping = RangeDict({Range(0, 1): ['old']}, identity=identity)
    mapping.clear()
    mapping.clear()
    assert mapping.isempty()
    assert mapping.values() == []

    mapping[Range(2, 3)] = value
    assert mapping[2] is value
    assert mapping.values() == [value]
    assert mapping.get(0, None) is None


def test_clear_preserves_identity_comparison():
    mapping = RangeDict(identity=True)
    mapping[Range(0, 1)] = ['old']
    mapping.clear()
    first = ['equal']
    second = ['equal']
    mapping[Range(2, 3)] = first
    mapping[Range(4, 5)] = second
    first.append('changed')
    assert mapping[2] is first
    assert mapping[4] is second
    assert second == ['equal']


def test_clear_preserves_equality_comparison():
    mapping = RangeDict({Range(0, 1): 'old'})
    mapping.clear()
    first = ['equal']
    second = ['equal']
    mapping[Range(2, 3)] = first
    mapping[Range(4, 5)] = second
    assert mapping[2] is first
    assert mapping[4] is first
