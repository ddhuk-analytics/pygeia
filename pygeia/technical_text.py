"""Text Preprocessing"""

from dataclasses import dataclass, field
from pandas import Series
from pygeia import pipeline


@dataclass
class Abbreviation:
    category: str
    word: str
    expansion: str
    pattern: str


@dataclass
class TechnicalText:
    raw: str
    new: str = None
    atr: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        if not self.new:
            self.new = self.raw

    def __repr__(self):
        return f"#{len(self.atr)}({self.new})"


@dataclass
class TechnicalDoc:
    data: Series

    def run(self, pipe=dict):
        for func, kwargs in pipe.items():
            try:
                func = getattr(pipeline, func)
            except AttributeError:
                func = getattr(pipeline, func)
            except TypeError:
                pass
            if kwargs:
                self.data = self.data.pipe(func, **kwargs)
            else:
                self.data = self.data.pipe(func)
        return self


if __name__ == "__main__":
    pass
