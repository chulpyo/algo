"""두 수의 합 — stdout 모드 샘플 (백준/코테식).

`solve` 는 stdin 을 읽어 결과를 **출력**하고, 러너가 캡처한 출력을 `output` 과 비교한다.
"""

import sys


def solve():
    a, b = map(int, sys.stdin.read().split())
    print(a + b)


EXAMPLES = [
    {"input": "1 2", "output": "3"},
    {"input": "5 7", "output": "12", "name": "bigger"},
]
