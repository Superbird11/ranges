# `python-ranges`

This module provides data structures for representing

- Continuous Ranges
- Non-continuous Ranges (i.e. sets of continous Ranges)
- `dict`-like structures that use ranges as keys

## Introduction

One curious missing feature in Python (and several other programming languages) is 
the absence of a Range data structure - a continuous set of values from some
starting point to some ending point. Instead, we have to make do with verbose
`if`/`else` comparisons:

```python
if value >= start and value < end:
    # do something
```

And to have a graded sequence of ranges with different behavior for each, we have
to chain these `if`/`elif`/`else` blocks together:

```python
# 2019 U.S. income tax brackets, filing Single
income = int(input("What is your income? $"))
if income < 9701:
    tax = 0.1 * income
elif 9701 <= income < 39476:
    tax = 970 + 0.12 * (income - 9700)
elif 39476 <= income < 84201:
    tax = 4543 + 0.22 * (income - 39475)
elif 84201 <= income < 160726:
    tax = 14382.5 + 0.24 * (income - 84200)
elif 160726 <= income < 204101:
    tax = 32748.5 + 0.32 * (income - 160725)
elif 204101 <= income < 510301:
    tax = 46628.5 + 0.35 * (income - 204100)
else:
    tax = 153798.5 + 0.37 * (income - 510300)
print(f"Your tax on that income is ${tax:.2f}")
```

This module, `ranges`, fixes this problem by introducing a data structure `Range` to
represent a continuous range, and a `dict`-like data structure `RangeDict` to map
ranges to values. This makes simple range checks more intuitive:

```python
if value in Range(start, end):
    # do something
```

and does away with the tedious `if`/`elif`/`else` blocks:

```python
# 2019 U.S. income tax brackets, filing Single
tax_info = RangeDict({
    Range(0, 9701):        (0,        0.10, 0),
    Range(9701,   39476):  (970,      0.12, 9700),
    Range(39476,  84201):  (4543,     0.22, 39475),
    Range(84201,  160726): (14382.2,  0.24, 84200),
    Range(160726, 204101): (32748.5,  0.32, 16072 5),
    Range(204101, 510301): (46628.5,  0.35, 204100),
    Range(start=510301):   (153798.5, 0.37, 510300),
})
income = int(input("What is your income? $"))
base, marginal_rate, bracket_floor = tax_info[income]
tax = base + marginal_rate * (income - bracket_floor)
print(f"Your tax on that income is ${tax:.2f}")
```

The `Range` data structure also accepts strings, dates, and any other data type, so
long as the start value is less than the end value (and so long as checking that
doesn't raise an error). 

See [the in-depth documentation]() for more details.

## Installation

Install `python-ranges` via [pip](https://pip.pypa.io/en/stable/):

```bash
$ pip install python-ranges
```

Due to use of format strings in the code, this module will only work with
**python 3.6 or higher**.

## Usage

Simply import `ranges` like any other python package, or import the `Range`, 
`RangeSet`, and `RangeDict` classes from it:

```python
import ranges

my_range = ranges.Range("anaconda", "viper")
```

```python
from ranges import Range

my_range = Range("anaconda", "viper")
```

Then, you can use these data types however you like.

### `Range`

To make a Range, simply call `Range()` with start and end values. Both of these
work:

```python
rng1 = Range(1.5, 7)
rng2 = Range(start=4, end=8.5)
```

You can also use the `include_start` and `include_end` keyword arguments to specify
whether or not each end of the range should be inclusive. By default, the start
is included and the end is excluded, just like python's built-in `range()` function.

If you use keyword arguments and don't specify either the `start` or the `end` of
the range, then the `Range`'s bounds will be negative or positive infinity,
respectively. `Range` uses a special notion of infinity that's compatible with
non-numeric data types - so `Range(start="journey")` will include *any string* 
that's lexicographically greater than "journey", and 
`Range(end=datetime.date(1989, 10, 4))` will include any date before October 4,
1989, despite neither `str` nor `datetime` having any built-in notion of infinity.

If you're making a range of numbers, then you can also use a single string as an
argument, with circle-brackets `()` meaning "exclusive" and square-brackets `[]`
meaning "inclusive":

```python
rng3 = Range("[1.5, 7)")
rng4 = Range("[1.5 .. 7)")
```

`Range`'s interface is similar to the built-in `set`, and the following methods
all act exactly how you'd expect:

```python
print(rng1.union(rng2))  # [1.5, 8.5)
print(rng1.intersection(rng2))  # [4, 7)
print(rng1.difference(rng2))  # [1.5, 4)
print(rng1.symmetric_difference(rng2))  # {[1.5, 4), [7, 8.5)}
```

Of course, the operators `|`, `&`, `-`, and `^` can be used in place of those
methods, just like for python's built-in `set`s.

See [the documentation]() for more details.

### `RangeSet`

A `RangeSet` is just an ordered set of `Range`s, all of the same kind. Like `Range`,
its interface is similar to the built-in `set`. Unlike `Range`, which isn't
mutable, `RangeSet` can be modified just like `set` can, with the methods
`.add()`, `.extend()`, `.discard()`, etc.

To construct a `RangeSet`, just call `RangeSet()` with a bunch of ranges (or
iterables containing ranges) as positional arguments:

```python
rngset1 = RangeSet("[1, 4.5]", "(6.5, 10)")
rngset2 = RangeSet([Range(2, 3), Range(7, 8)])
```

`Range` and `RangeSet` objects are mutually compatible for things like `union()`,
`intersection()`, `difference()`, and `symmetric_difference()`. If you give these
methods a range-like object, it'll get automatically converted:

```python
print(rngset1.union(Range(3, 8)))  # {[1, 10)}
print(rngset1.intersect("[3, 8)"))  # {[3, 4.5], (6.5, 8)}
print(rngset1.symmetric_difference("[3, 8)"))  # {[1, 3), (4.5, 6], [8, 10)}
```

Of course, `RangeSet`s can operate with each other, too:

```python
print(rngset1.difference(rngset2))  # {[1, 2), [3, 4.5], (6.5, 7), [8, 10)}
```

The operators `|`, `&`, `^`, and `-` all work with `RangeSet` as they do with `set`,
as do their associated assignment operators `|=`, `&=`, `^=`, and `-=`. 

Finally, you can iterate through a `RangeSet` to get all of its component ranges:

```python
for rng in rngset1:
    print(rng):
# [1, 4.5]
# (6.5, 10)
```

See [the documentation]() for more details.

### ` RangeDict`

This data structure is analagous to python's built-in `dict` data structure, except
it uses `Range`s/`RangeSet`s as keys. As shown above, you can use `RangeDict` to
concisely express different behavior depending on which range a value falls into.

To make a `RangeDict`, call `RangeDict()` with an either a `dict` or an iterable
of 2-tuples corresponding `Range`s or `RangeSet`s with values. You can also use
a tuple of `Range`s as a key.  
A `RangeDict` can handle any type of `Range`, or even multiple different types of 
`Range`s all at once:

```python
advisors = RangeDict([
    (Range(end="I"), "Gilliam"),
    (Range("I", "Q"), "Jones"),
    (Range(start="Q"), "Chapman"),
])

mixmatch = RangeDict({
    (Range(0, 8),     Range("A", "I")): "Gilliam",
    (Range(8, 16),    Range("I", "Q")): "Jones",
    (Range(start=16), Range(start="Q")): "Chapman",
})
```

See [the documentation]() for more details.

## Support / Contributing

If you spot any bugs in this module, please submit an issue detailing what you
did, what you were expecting, and what you saw, and I'll make a prompt effort
to isolate the root cause and fix it. The error should be reproducible. 

If, looking through the code, you spot any other improvements that could be
made, then feel free to submit issues detailing those as well. Also feel free
to submit a pull request with improvements to the code.

This module is extensively unit-tested. All code contributions should be
accompanied by thorough unit tests for every conceivable use case of the new
functionality. If you spot any use cases that aren't currently covered by the
unit test suite, feel free to either submit a GitHub issue detailing them, or
simply add them yourself and submit a pull request.

### Possible To-Do List:

- Add a notion of a `PermissiveRangeSet` (name pending) which allows multiple types 
of `Range`s that are not necessarily mutually comparable. In the initial design I
considered a number of ways to implement this, but ran into conceptual difficulties,
mainly in terms of handling performance and algorithms. If you can build a 
`PermissiveRangeSet` or similar class that implements this functionality, along with
a suitable set of unit tests, then feel free to do so and submit a pull request (if
you do, please include the reasoning for your design decisions).
- Rewrite `RangeSet.intersection()` to use a pair-stepping
algorithm (akin to the "merge" part of MergeSort - iterate through the two 
`_LinkedList` data structures simultaneously and only advance one element of one
list at a time) instead of the current "compare every element with every other 
element" solution. Adding short-circuiting to this (returning early from the method
once it's clear that there is no longer work to be done, even if the entire list
has not yet been iterated through) would also be useful, and the two approaches
synergize nicely. This won't lower the complexity class below its current
worst-case `O(n^2)`, but it could drastically improve performance.
- Rewrite `RangeSet.isdisjoint()` to use pair-stepping and short-circuiting. The
reasoning here is the same as for `RangeSet.intersection()`.

Any open issues or bugs are also fair game for contribution. See 
[above](#errors--contributing) for directions.

## License

[MIT License](LICENSE.txt). Feel free to use `ranges` however you like.
