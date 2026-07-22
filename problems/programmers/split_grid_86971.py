"""프로그래머스 Lv.2 · 전력망을 둘로 나누기 (86971)
https://school.programmers.co.kr/learn/courses/30/lessons/86971

n개의 송전탑이 전선(wires)으로 트리처럼 연결돼 있다. 전선 하나를 끊으면 전력망이
두 개로 나뉜다. 두 전력망의 송전탑 개수 차이가 최소가 되도록 전선 하나를 끊을 때,
그 최소 차이를 반환한다. (n <= 100, 입력은 항상 트리)

반환값 모드 — solution(n, wires) 의 반환값을 EXAMPLES 의 expected 와 비교한다.
"""

from collections import deque
from collections import defaultdict

def solution(n, wires):
    answer = n-2
    g = defaultdict(set)
    for wire in wires:
        a, b = wire
        g[a].add(b)
        g[b].add(a)

    for wire in wires:
        a, b = wire
        q = deque([a])        
        t = set()
        g[a].remove(b)
        t.add(a)

        while q:
            node = q.popleft()
            # t.add(node)
            for connected_node in list(g[node]):
                if (node != a or (node == a and connected_node != b)) and connected_node not in t:
                    q.append(connected_node)
                    t.add(connected_node)
        tmp =  abs(n - 2*len(t))
        if answer > tmp:
            answer = tmp
        g[a].add(b)
    return answer


# ── 평가: 압축 대안 (참고용, solve로는 쓰지 않음) ─────────────────────────────
# 슬라이싱으로 간선 i를 빼고(wires[i+1:]+wires[:i]), 남은 첫 간선을 시드로
# relaxation을 len(sub)번 돌려 한쪽 컴포넌트를 키운 뒤 |2*len(s)-n|의 최소를 취함.
# 평가:
#   + 아이디어가 영리하고, n>=3에서 위 BFS와 결과 일치(공식 3/3 + 랜덤 대조 OK).
#   ⚠ n=2(간선 1개) → sub=[] → set(sub[0]) 에서 IndexError (경계 미처리).
#   - 부수효과용 리스트컴프리헨션은 안티패턴(버릴 리스트 생성·가독성 저하).
#   - 복잡도 ~O(n^3)로 BFS의 O(n^2)보다 느림 (n<=100이라 통과는 함).
def solution_compact(n, wires):
    ans = n
    for sub in (wires[i + 1:] + wires[:i] for i in range(len(wires))):
        s = set(sub[0])
        [s.update(v) for _ in sub for v in sub if set(v) & s]
        ans = min(ans, abs(2 * len(s) - n))
    return ans


# 러너 진입점 (규약: solve). 정확하고 n=2 경계도 처리하는 BFS(solution)를 사용.
# 프로그래머스에는 solution 을 그대로 제출하면 된다.
solve = solution


# 입출력 예 (공식)
EXAMPLES = [
    {"args": (9, [[1, 3], [2, 3], [3, 4], [4, 5], [4, 6], [4, 7], [7, 8], [7, 9]]), "expected": 3},
    {"args": (4, [[1, 2], [2, 3], [3, 4]]), "expected": 0},
    {"args": (7, [[1, 2], [2, 7], [3, 7], [3, 4], [4, 5], [6, 7]]), "expected": 1},
    # 경계·엣지 보강
    {"args": (2, [[1, 2]]), "expected": 0},                              # 간선 1개 (n=2 경계)
    {"args": (5, [[1, 2], [1, 3], [1, 4], [1, 5]]), "expected": 3},      # 스타(중심 1) → 최소 3
    {"args": (6, [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]), "expected": 0},  # 경로(짝수) → 0
]
