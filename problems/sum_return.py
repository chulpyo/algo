"""두 수의 합 — 반환값 모드 샘플.

`solve` 는 값을 **반환**하고, 러너가 `expected` 와 `==` 비교한다.
"""


def solve(a, b):
    return a + b


EXAMPLES = [
    {"args": (1, 2), "expected": 3},
    {"args": (5, 7), "expected": 12, "name": "bigger"},
    {"args": (-3, 3), "expected": 0, "name": "zero"},
]
