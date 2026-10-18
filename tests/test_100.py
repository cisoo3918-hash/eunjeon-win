# -*- coding: utf-8 -*-
"""문장 100개: 예외 없음 + 형태소를 이으면 원문(띄어쓰기 뺀 것)과 같다(g2pkk annotate 가 기대하는 조건) + KoNLPy 꼴 (str, str)."""
import random

import eunjeon

base = [
    "공이 잘 안 맞는다면, 맞는 순간 머리를 보세요.", "투어 프로 장재형 선수의 아이언 스윙입니다.", "노란 선이 공 자리예요.",
    "드라이버도 똑같아요.", "머리가 공 뒤에 남아야 올려 치면서 멀리 갑니다.", "연습장에서 정면으로 찍어서 확인해 보세요.",
    "오늘 날씨가 정말 좋네요!", "값은 49,000원이고 내일까지 보내 드립니다.", "AI로 만든 영상 3편을 올렸어요.",
    "원주 똑딱똑딱골프아카데미 혁신점입니다.", "읽고 싶은 책이 많아요.", "닭이 울었다.", "밟고 넓은 길로 갔다.",
    "선생님께서 말씀하셨습니다.", "1등은 100점, 2등은 90점!", "Hello 세계, 반갑습니다.", "ㅋㅋㅋ 진짜요?", "",
]
words = ["골프", "스윙", "임팩트", "머리", "공", "드라이버", "아이언", "연습", "레슨", "선수", "프로", "비거리", "백스윙", "피니시"]
josa = ["이", "가", "을", "를", "은", "는", "에서", "으로", "의", "도", ""]
ends = ["합니다.", "해요.", "했어요?", "하세요!", "입니다.", "였다.", "할까요?"]
random.seed(1018)
sents = list(base)
while len(sents) < 100:
    n = random.randint(1, 5)
    sents.append(" ".join(random.choice(words) + random.choice(josa) for _ in range(n)) + " " + random.choice(ends))

m = eunjeon.Mecab()
bad = 0
for s in sents:
    try:
        p = m.pos(s)
        assert all(isinstance(a, str) and isinstance(b, str) for a, b in p)
        assert "".join(a for a, _ in p) == s.replace(" ", ""), (s, p)
        m.morphs(s); m.nouns(s)
    except Exception as e:  # noqa: BLE001
        bad += 1
        print("틀림", repr(s), e)
print(f"{len(sents)}문장 중 틀림 {bad}")
assert bad == 0
