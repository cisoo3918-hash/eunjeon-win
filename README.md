# eunjeon-win

**Windows drop-in for `eunjeon` (Korean MeCab).** Makes `g2pkk` — and therefore **MeloTTS Korean** — work on Windows with plain `pip`, no C++ build tools.

윈도에서 MeloTTS 한국어(g2pkk)가 `you have to install eunjeon` 오류로 멈출 때 쓰는 대체 부품입니다. C++ 빌드 도구 없이 `pip` 한 줄이면 됩니다.

## The problem

- `g2pkk` imports `eunjeon` on Windows. The original `eunjeon` needs a C++ compiler and fails to install on modern Python.
- The working alternative, `python-mecab-ko`, ships a package folder named `mecab`. On Windows the file system is case-insensitive, so it **collides with `mecab-python3`'s `MeCab` folder** (MeloTTS imports Japanese → needs `MeCab`). Whichever installs last overwrites the other, and you get `No module named 'mecab'` or `Japanese requires mecab-python3`.

## The fix

`eunjeon-win` provides an `eunjeon` module with the KoNLPy-style `Mecab` class, built directly on `python-mecab-ko`'s compiled `_mecab` extension and `mecab-ko-dic`. It never imports the colliding `mecab` folder, so Korean and Japanese both work in the same environment.

```bash
pip install python-mecab-ko python-mecab-ko-dic
pip install git+https://github.com/cisoo3918-hash/eunjeon-win
# MeloTTS also imports Japanese — if `MeCab` got overwritten, repair it:
pip install --force-reinstall --no-deps mecab-python3
```

```python
from eunjeon import Mecab
m = Mecab()
m.pos("공이 잘 안 맞는다면, 맞는 순간 머리를 보세요.")
# [('공','NNG'), ('이','JKS'), ('잘','MAG'), ('안','MAG'), ('맞','VV'), ('는다면','EC'), ...]
m.morphs("..."); m.nouns("...")
```

## Tested

- Windows 10, Python 3.12, python-mecab-ko 1.3.7, MeloTTS 0.1.2 (`language='KR'`) → Korean speech generated (9.3 s sample).
- `tests/test_100.py`: 100 sentences, 0 failures (no exceptions; morphemes re-join to the input as g2pkk expects).
- Note: MeloTTS Korean also downloads `kykim/bert-kor-base` (~476 MB). If the download stalls, fetch it first with `huggingface_hub.hf_hub_download('kykim/bert-kor-base', 'pytorch_model.bin')` (resumes), then run with `HF_HUB_OFFLINE=1`.

## License

BSD-3-Clause. The wrapper logic is adapted from [python-mecab-ko](https://github.com/jonghwanhyeon/python-mecab-ko) © 2022 Jonghwan Hyeon (BSD-3-Clause, see `LICENSE-python-mecab-ko`). Not affiliated with the original `eunjeon` project.
