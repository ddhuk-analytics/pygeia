"""Contains all input data objects needed for cleaning the data"""

import re
from pathlib import Path
from dataclasses import dataclass
from collections import UserDict
from pandas import read_csv, notna, Series, concat


def add_boundaries(text: str, bound: str):
    """Add boundary (\b) to the regular expression string

    Parameters
    ----------
    text : str
        Regular Expression
    bound : str
        Boundary; both, left or right
    """
    bounds = {
        "both": rf"\b{text}\b",
        "left": rf"\b{text}",
        "right": rf"{text}\b",
        "none": text,
    }
    return bounds[bound.lower()] if bound else text


def text_to_dict(text: str, sep: str = "="):
    """Turn text into a dictionary using the sep argument

    Parameters
    ----------
    text : str
        Regular Expression
    sep : str, optional
        Separartor used in data, by default '='
    """
    if notna(text):
        return dict(tuple(pair.strip().split(sep)) for pair in text.split())
    return {}


def build_patttern(
    dct: dict,
    pattern: str,
    placeholder: str,
    boundary: str,
    flags: re.RegexFlag = re.NOFLAG,
):
    """_summary_

    Parameters
    ----------
    dct : dict
        Record information
    pattern : str
        Regular Expression pattern
    placeholder : str
        Additional information for regular expression
    boundary : str
        Column name for word boundary type
    """
    rgx = dct[pattern].format(**text_to_dict(dct[placeholder]))
    return re.compile(add_boundaries(rgx, dct[boundary]), flags=flags)


@dataclass(frozen=True)
class Abbreviation:
    category: str
    index: int
    initial: str
    word: str
    expansion: str
    pattern: str


class Abbreviations(UserDict):
    """Abbreviation mappings to clean the data"""

    SEQUENCE = (
        "symbol",
        "uom",
        "time",
        "misspelling",
        "noun",
        "noun_fix",
        "verb_fix",
        "object",
        "special",
    )

    def __missing__(self, key):
        if key not in self.SEQUENCE:
            raise KeyError(f"Category not in {self.__class__.__name__} object: {key}")
        return self[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    @property
    def patterns(self):
        dct = {}
        for seq in self.SEQUENCE:
            for abv in self[seq]:
                dct[abv.pattern] = f" {abv.expansion} "
        return dct

    @classmethod
    def from_csv(
        cls,
        path: str,
        category: str,
        abbreviation: str,
        pattern: str,
        placeholder: str,
        boundary: str,
        expansion: str,
        sequence: tuple = None,
        encoding: str = "utf8",
    ):
        """Alternative constructor to build a dictionary from a csv file

        Parameters
        ----------
        path : str
            Path to the abbreviation file.
        grp_col : str
            Column for grouping the category, which must contain all sequence categories
        idx_col : str
            Column for key of the inner dictionary, which must contain regular expression patterns
        sequence : tuple, optional
            Ranked categories for the mapping sequence in the text, by default None
        encoding : str, optional
            Text encoding, by default "utf8"
        """
        path = Path(path)
        if sequence:
            cls.SEQUENCE = tuple(sequence)
        category = str(category)

        tmp = {}
        for cat, grp in read_csv(path, encoding=encoding).groupby(category):
            lst = []
            for dct in grp.reset_index().to_dict(orient="records"):
                abb = Abbreviation(
                    cat,
                    dct["index"],
                    dct[pattern][0].lower()
                    if dct[pattern][0].isalnum() and dct[boundary] in ["left", "both"]
                    else "#",
                    dct[abbreviation],
                    dct[expansion],
                    build_patttern(dct, pattern, placeholder, boundary, re.I),
                )
                lst.append(abb)
            tmp[cat] = lst

        return cls(tmp)


class Fragment:
    def __init__(self, storage_name) -> None:
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if self.storage_name == "name":
            instance.__dict__[self.storage_name] = value.capitalize()
        elif self.storage_name in ["letter", "section"]:
            instance.__dict__[self.storage_name] = value.upper()
        elif self.storage_name == "well":
            instance.__dict__[self.storage_name] = str(value).zfill(2)
        else:
            raise ValueError("Attribute not found")


class Location:
    name = Fragment("name")
    letter = Fragment("letter")
    well = Fragment("well")
    section = Fragment("section")

    def __init__(self, name="", letter="", well="", section=""):
        self.name = name
        self.letter = letter
        self.well = well
        self.section = section

    @property
    def tag(self):
        if self.section != "":
            return " ".join(
                [
                    f"<LOC: {self.name}|{self.letter}|{self.well}{sec}>"
                    for sec in self.section
                ]
            )
        return f"<LOC: {self.name}|{self.letter}|{self.well}{self.section}>"

    def __bool__(self):
        return self.name != ""


def location_(ser: Series, fac: Series, facilities: dict):
    lines = {}
    event_col, fac_col = ser.name, fac.name

    loc_ahr = re.compile(
        r"(\b(?:gu|sm|je|[pld]a|t[aeu]|ib|bi)(?:abc|[a-frq]x?)?)", flags=re.I
    )
    loc_rgx = re.compile(
        r"(gu|sm|je|[pld]a|t[aeu]|ib|bi)((?:abc|[a-frq]x?)?)", flags=re.I
    )

    wll_ahr = re.compile(r"(<[^>]+>)")
    wll_rgx = re.compile(
        (
            r"((?:abc|[a-frq]x?)?)[-/\s\\.,]*"
            r"([0-5]?\d)[-/\s\\.,]*(?!(?:[%>]|:\d+))"
            r"((?:[uil]+[-/\s\\and&]*[ul]?)?)\b[-/\s\\.,]*(?:and|&)?"
        ),
        flags=re.I,
    )

    df = concat([ser, fac], axis=1).sort_index()

    for line in df.itertuples():
        loc = Location()
        ftxt = ""

        for txt in wll_ahr.split(getattr(line, event_col)):
            if wll_ahr.match(txt):
                ftxt += txt
                continue

            stxt = loc_ahr.split(txt)
            i, n = 0, len(stxt)

            while i < n:
                try:
                    curr, subsq = stxt[i], stxt[i + 1]
                except IndexError:
                    curr, subsq = stxt[i], ""

                lm = loc_rgx.match(curr)
                if lm:
                    if re.match(r"[a-z]{3,}|st|h", subsq):
                        lm = None
                    else:
                        loc.name, loc.letter = lm.group(1), lm.group(2)
                    wtxt = curr + subsq
                    i += 2
                else:
                    loc.name, loc.letter = facilities[getattr(line, fac_col)].split()
                    wtxt = curr
                    i += 1

                wm = wll_rgx.search(wtxt)
                if not wm:
                    ftxt += wtxt
                    continue

                while wm:
                    l = wm.group(1)
                    if l and l.upper() != loc.letter.upper():
                        loc.letter = l
                    loc.well = wm.group(2)
                    ul = re.sub(r"[-/\s\\.,and&]*", "", wm.group(3))
                    loc.section = ul

                    try:
                        ftxt += f" {wtxt[:lm.start()]} {loc.tag} {wtxt[lm.end():wm.start()]} "
                    except AttributeError:
                        ftxt += f" {wtxt[:wm.start()]} {loc.tag} "

                    wtxt = wtxt[wm.end() :]

                    wm = wll_rgx.search(wtxt)

                ftxt += wtxt

        lines[line.Index] = ftxt

    return (
        Series(lines, name=event_col)
        .str.replace(r"\s+", " ", regex=True, case=False)
        .str.strip("- .")
    )


if __name__ == "__main__":
    pass
