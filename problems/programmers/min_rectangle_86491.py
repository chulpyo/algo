"""프로그래머스 Lv.1 · 최소직사각형 (86491)
https://school.programmers.co.kr/learn/courses/30/lessons/86491

명함들을 모두 수납할 수 있는 가장 작은 지갑(직사각형)의 넓이를 구한다.
명함은 회전 가능하다 (가로/세로를 바꿔 넣어도 된다).

반환값 모드 — solve 가 가리키는 함수의 반환값을 EXAMPLES 의 expected 와 비교한다.
원본(solution)과 개선본(solution_v2)을 함께 보존한다.
"""


def solution(sizes):
    # 원본 제출본 — 명함마다 긴 변/짧은 변을 if로 분기해 max_w, max_h 갱신 (O(n), 1-pass)
    answer = 0
    max_w = 0
    max_h = 0

    for size in sizes:
        if size[0] > size[1]:
            if size[0] > max_w:
                max_w = size[0]
            if size[1] > max_h:
                max_h = size[1]
        else:
            if size[0] > max_h:
                max_h = size[0]
            if size[1] > max_w:
                max_w = size[1]

    answer = max_w * max_h

    return answer


def solution_v2(sizes):
    # 개선본 — 각 명함을 회전 정규화(긴 변=long, 짧은 변=short)한 뒤 max 로 간결화.
    # 동작·복잡도(O(n), O(1)) 동일, 순회 1회 유지.
    max_w = max_h = 0
    for a, b in sizes:
        long, short = (a, b) if a > b else (b, a)
        max_w = max(max_w, long)
        max_h = max(max_h, short)
    return max_w * max_h


# 러너 진입점 (규약: solve). 개선본을 검증한다.
# 원본을 검증하려면 solve = solution 으로 바꾸면 된다. 프로그래머스에는 둘 중 하나를 solution 으로 제출.
solve = solution_v2


# 입출력 예 (문제의 예제 그대로)
EXAMPLES = [
    {"args": ([[60, 50], [30, 70], [60, 30], [80, 40]],), "expected": 4000},
    {"args": ([[10, 7], [12, 3], [8, 15], [14, 7], [5, 15]],), "expected": 120},
    {"args": ([[14, 4], [19, 6], [6, 16], [18, 7], [7, 11]],), "expected": 133},
]
