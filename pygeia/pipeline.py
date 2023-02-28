"""Constants"""

import sys
import unicodedata as ucd
from pandas import Series


def translate_ucd(ser: Series, **kwargs):
    """Maps unicode characters"""

    def make_map(category: str, repl: str, special: set):
        """Create dictionary for mapping"""

        return {
            i: repl.format(chr(i))
            for i in range(sys.maxunicode)
            if ucd.category(chr(i)).startswith(category) and chr(i) not in special
        }

    dct = make_map(**kwargs)
    return ser.apply(lambda s: s.translate(dct))


separator_ = punctuation_ = whitespace_ = translate_ucd


def map_patterns(ser: Series, iterable: dict):
    """Expand abbreviations based on input data patterns

    Parameters
    ----------
    ser : Series
        Pandas Series
    patterns : dict
        Abbreviation patterns
    """
    for pattern, value in iterable.items():
        ser = ser.str.replace(pattern, value)
    return ser.str.replace(r"\s+", " ", regex=True, case=False).str.strip("- .")


datetime_ = reference_ = hour_ = duration_ = tag_ = uom_ = map_patterns
