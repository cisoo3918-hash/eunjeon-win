"""eunjeon (Windows drop-in) — `from eunjeon import Mecab` that actually works on Windows.

Why: g2pkk (used by MeloTTS Korean) imports `eunjeon` on Windows, but the original `eunjeon`
package needs a C++ build and fails to install on modern Python. The working alternative,
python-mecab-ko, ships a Python package named `mecab`, and on Windows (case-insensitive
file system) that folder collides with mecab-python3's `MeCab` (needed by MeloTTS Japanese),
so one overwrites the other.

This package talks to python-mecab-ko's compiled `_mecab` extension and `mecab_ko_dic`
directly and never imports the colliding `mecab` package. API follows KoNLPy/eunjeon:
`Mecab().pos()`, `.morphs()`, `.nouns()`, `.parse()`.

Wrapper code adapted from python-mecab-ko (Copyright 2022 Jonghwan Hyeon, BSD-3-Clause);
see LICENSE-python-mecab-ko.
"""
from __future__ import annotations

import os
import sys
import sysconfig
from pathlib import Path
from typing import NamedTuple, Optional, Union

__version__ = "0.1.0"
__all__ = ["Mecab", "MeCabError", "Morpheme"]


def _add_dll_dirs():
    # python-mecab-ko is built with delvewheel: libmecab-*.dll sits in site-packages (platlib).
    seen = set()
    for p in [sysconfig.get_paths().get("platlib"), *sys.path]:
        if not p or p in seen or not os.path.isdir(p):
            continue
        seen.add(p)
        if any(n.lower().startswith("libmecab") and n.lower().endswith(".dll") for n in os.listdir(p)):
            try:
                os.add_dll_directory(p)
            except (AttributeError, OSError):
                pass


if os.name == "nt":
    _add_dll_dirs()

try:
    import _mecab  # compiled extension from python-mecab-ko (top-level, no name clash)
    import mecab_ko_dic
except ImportError as e:  # pragma: no cover
    raise ImportError("eunjeon (Windows drop-in) needs: pip install python-mecab-ko python-mecab-ko-dic") from e

PathLike = Union[str, Path]
_MECABRC = Path(__file__).absolute().parent / "mecabrc"


class MeCabError(Exception):
    pass


class Morpheme(NamedTuple):
    surface: str
    pos: str
    feature: str
    start: int
    end: int


class Mecab:
    """KoNLPy/eunjeon-compatible Korean morpheme analyzer (mecab-ko-dic)."""

    def __init__(self, dicpath: Optional[PathLike] = None, user_dictionary_path: Optional[Union[PathLike, list]] = None):
        dicpath = dicpath or mecab_ko_dic.dictionary_path
        opts = ["--rcfile", str(_MECABRC), "--dicdir", str(dicpath)]
        if user_dictionary_path:
            paths = user_dictionary_path if isinstance(user_dictionary_path, list) else [user_dictionary_path]
            opts += ["--userdic", ",".join(f'"{p}"' for p in paths)]
        self._tagger = _mecab.Tagger(opts)

    def parse(self, sentence: str) -> list:
        lattice = _mecab.Lattice()
        lattice.add_request_type(_mecab.MECAB_ALLOCATE_SENTENCE)
        lattice.set_sentence(sentence)
        if not self._tagger.parse(lattice):
            raise MeCabError(self._tagger.what())
        out = []
        for (s, e), node in lattice:
            out.append(Morpheme(node.surface, node.feature.split(",")[0], node.feature, s, e))
        return out

    def pos(self, phrase: str, flatten: bool = True, join: bool = False):
        """[(surface, tag), ...] like KoNLPy. join=True → ['surface/tag', ...]."""
        res = [(m.surface, m.pos) for m in self.parse(phrase)]
        if join:
            return [f"{s}/{t}" for s, t in res]
        return res

    def morphs(self, phrase: str) -> list:
        return [m.surface for m in self.parse(phrase)]

    def nouns(self, phrase: str) -> list:
        return [m.surface for m in self.parse(phrase) if m.pos.startswith("N")]


# eunjeon/KoNLPy spell it `Mecab`; python-mecab-ko spells it `MeCab` — accept both.
MeCab = Mecab
