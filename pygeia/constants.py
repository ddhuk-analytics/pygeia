"""Constants"""

import re

facilities = {
    "Guntong ABC": "Gu ABC",
    "Guntong D": "Gu D",
    "Guntong F": "Gu F",
    "Irong Barat A": "Ib A",
    "Palas": "Pa A",
    "Semangkok A ": "Sm A",
    "Tabu": "Tu X",
    "Tapis": "Ta X",
    "Tapis B": "Ta B",
}


def compile_rgx(pattern: str, flags: re.RegexFlag = re.I):
    """Turn a string patter into a compiled regex

    Parameters
    ----------
    pattern : str
        Pattern string
    flags : re.RegexFlag, optional
        Regular Expression flag, by default re.I
    """
    return re.compile(pattern, flags=flags)


date_format_p = (
    r"\b(31|[123]0|[012]?[1-9])\s*[-/.]+\s*(0?\d|1[012])\s*[-/.]?\s*((?:2[01]|1[89])?\d\d)\b(?!\s+[%hk])",
    r"\b(31|[123]0|[012]?[1-9])\s*(?:st|nd|rd|th)?[-/.\s]*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)[-/.,\s]*((?:2[01]|1[89])?\d\d)\b(?!\s+[%hk])",
    r"\b(?<!<\w{3}:\s)(31|[123]0|[012]?[1-9])\s*(?:st|nd|rd|th)?[-/.\s]*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)(?!\s+[%hk])",
    r"\b(?<!<\w{3}:\s\d\d/)(?<!<\w{3}:\s\d/)((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)[-/.\s]*((?:2[01]|1[89])?\d\d)(?!\s+[%hk])",
    r"\b(?<!<\w{3}:\s\d\d/)(?<!<\w{3}:\s\d/)(?<!<\w{3}:\sdd/)((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)[-/.\s]*(31|[123]0|[012]?[1-9])\s*(?:st|nd|rd|th)?(?!\s+[%hk])",
)
date_format_v = (
    " <DTM: " + r"\1/\2/\3" + "> ",
    " <DTM: " + r"\1/\2/\3" + "> ",
    " <DTM: " + r"\1/\2/yyyy" + "> ",
    " <DTM: " + r"dd/\1/\2" + "> ",
    " <DTM: " + r"\2/\1/yyyy" + "> ",
)
date_format = dict(zip(map(compile_rgx, date_format_p), date_format_v))

ref_format_p = (
    r"\b(?:s[hut]{,3}d[own]{,3})[\-/._\s]*((?:2[01]|1[89])\d\d)",
    r"\b(?<=remaining)[-/._\s]*(\d?\d)\b",
    r"\b([jtkm]-?[12359][05]?)\b",
    r"\b(nr_[-/._\s]*2|pdm1|pd[-\s]+m1|[ep]sd[-\s]*[12])\b",
)
ref_format_v = (
    " <ABV: SD" + r"\1" + "> ",
    " <REF: " + r"\1" + "> ",
    " <REF: " + r"\1" + "> ",
    " <REF: " + r"\1" + "> ",
)
ref_format = dict(zip(map(compile_rgx, ref_format_p), ref_format_v))

hrs_format_p = (
    r"(?<![a-qt-z]-)\b([01][0-9]|2[0-3])[.\s]*([0-5][0-9])(?:\s*h[ou]{,2}rs?)?\b(?!>|\s+[%hk])",
)
hrs_format_v = (" <HRS: " + r"\1:\2" + "> ",)
hrs_format = dict(zip(map(compile_rgx, hrs_format_p), hrs_format_v))

tag_format_p = (
    r"\b((?:tg|gt)g?|[lhipmge][cg]?[fdxbvist]|v|g|[lpfems][aswldoc][hlwdv][hlp]?)[-#\s]*(\d{3,4}-?(?:[-/\s]*[a-f]+)*)(?:\s|$|\.)(?![%hk])",
)
tag_format_v = (" <TAG: " + r"\1-\2" + "> ",)
tag_format = dict(zip(map(compile_rgx, tag_format_p), tag_format_v))

dur_format_p = (r"\b(?<!-)(\d\d?(?:\s*[-\.,]\s*\d+)?)(?!-)\s*(?:h[ou]{,2}rs?)",)
dur_format_v = (" <DUR: " + r"\1" + " hrs> ",)
dur_format = dict(zip(map(compile_rgx, dur_format_p), dur_format_v))

uom_format_p = (r"\b(\d+\s*oo\s*\d+)[.\s]*(?:(turns?)?)\b",)
uom_format_v = (" <UOM: " + r"\1\2" + "> ",)
uom_format = dict(zip(map(compile_rgx, uom_format_p), uom_format_v))
