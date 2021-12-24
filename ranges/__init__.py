"""
The `ranges` module contains the data structures Range, RangeSet,
and RangeDict.

See http://pypi.org/project/python-ranges for information.

See http://github.com/superbird11/ranges for source code.
"""

from .Range import Range
from .RangeSet import RangeSet
from .RangeDict import RangeDict
from ._helper import Inf, Rangelike, RangelikeString

__all__ = ["Range", "RangeSet", "RangeDict", "Inf", "Rangelike", "RangelikeString"]
name = "ranges"
