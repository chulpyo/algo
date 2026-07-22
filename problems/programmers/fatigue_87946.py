"""프로그래머스 Lv.2 · 피로도 (87946)
https://school.programmers.co.kr/learn/courses/30/lessons/87946

현재 피로도 k로 던전들을 탐험할 때 탐험 가능한 최대 던전 수를 구한다.
각 던전은 [최소 필요 피로도, 소모 피로도]. 현재 피로도 >= 최소 필요 피로도면 탐험 가능,
탐험하면 소모 피로도만큼 감소한다. 던전 수 <= 8 이라 순서를 바꿔가며 완전탐색할 수 있다.

반환값 모드 — solve 가 가리키는 함수의 반환값을 EXAMPLES 의 expected 와 비교한다.
"""


from collections import deque
from itertools import permutations


# --- 원본 1: 내가 작성한 상태 BFS -------------------------------------------
def solution(k, dungeons):
    max_visit = 0
    visited = set()
    for idx, dungeon in enumerate(dungeons):

        q = deque([(idx, set(), k)])

        while q:
            node = q.popleft()
            now = dungeons[node[0]]
            fatigue = node[2]
            if now[0] <= fatigue:
                visited = node[1].union([node[0]])
                fatigue -= now[1]
                for nxt, nxt_dungeon in enumerate(dungeons):
                    if nxt not in visited:
                        q.append((nxt, visited, fatigue))
        max_visit = max(len(visited), max_visit)

    return max_visit


# --- 원본 2: 순열 완전탐색 버전 ---------------------------------------------
def solution(k, dungeons):
    answer = 0
    for perm in permutations(dungeons):
        fatigue, cnt = k, 0
        for need, cost in perm:
            if fatigue >= need:
                fatigue -= cost
                cnt += 1
        answer = max(answer, cnt)
    return answer


# --- 개선본: 원본 1(BFS) 검수 반영 -----------------------------------------
# max를 루프 안 상태마다 갱신 + seen으로 중복 상태 제거 + 미사용 변수 제거.
def solution_v2(k, dungeons):
    answer = 0
    start = (k, frozenset())
    q = deque([start])
    seen = {start}
    while q:
        fatigue, visited = q.popleft()
        answer = max(answer, len(visited))
        for i, (need, cost) in enumerate(dungeons):
            if i not in visited and fatigue >= need:
                nxt = (fatigue - cost, visited | {i})
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
    return answer


# 러너 진입점 (규약: solve). 개선본을 검증한다.
# 원본을 확인하려면 solve = solution 으로 바꾸면 된다 (단, 위 solution 두 개 중
# 뒤엣것(순열)이 살아있음 — 파이썬은 같은 이름 뒤 정의가 앞을 덮는다).
solve = solution_v2


# 입출력 예
EXAMPLES = [
    # 공식 예제 — [80,20],[30,10],[50,40] 순서에서 3개 달성 (순서 바꿔야 최대)
    {"args": (80, [[80, 20], [50, 40], [30, 10]]), "expected": 3},
    # 엣지 — 첫 던전도 시작 불가 (49 < 50)
    {"args": (49, [[50, 10]]), "expected": 0},
]
