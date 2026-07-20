# algorithm

파이썬 알고리즘 문제 풀이 저장소 + 예시 자동 실행 러너.

문제 하나 = 파일 하나. 각 문제 파일은 **예시(입력/기대출력)** 와 **솔루션 함수**를 함께 담는다.
`main.py`에 문제 경로를 주면 그 문제의 모든 예시에 대해 솔루션 함수를 자동 실행하고 결과를 비교한다.

```bash
uv run main.py problems/sum_return.py    # 반환값 모드 샘플
uv run main.py problems/sum_stdout.py    # stdout 모드 샘플
uv run pytest                            # 러너 단위 테스트
```

## 문제 파일 규약

문제 모듈은 두 심볼을 노출한다:

- `solve` — 솔루션 **callable**
- `EXAMPLES` — 비어있지 않은 예시 `list`. 각 예시는 `dict`.

**모드는 예시 dict의 키로 판별**하며, 한 파일의 모든 예시는 동일 모드여야 한다.

| 모드 | 판별 키 | 예시 필드 | 러너 동작 |
|---|---|---|---|
| 반환값 | `expected` | `args`(tuple, 기본 `()`), `kwargs`(dict, 기본 `{}`), `expected`, `name`(선택) | `solve(*args, **kwargs) == expected` |
| stdout | `output` | `input`(str, 기본 `""`), `output`, `name`(선택) | `input`을 stdin으로 주입, `solve()` 출력 캡처 후 문자열 비교 (후행 개행 무시) |

```python
# 반환값 모드
def solve(a, b):
    return a + b
EXAMPLES = [{"args": (1, 2), "expected": 3}]

# stdout 모드
import sys
def solve():
    a, b = map(int, sys.stdin.read().split())
    print(a + b)
EXAMPLES = [{"input": "1 2", "output": "3"}]
```

### 주의
- 문제 파일은 러너가 **import** 한다 — import 시점에 부수효과(입력 대기·즉시 실행)를 만들지 않는다.
- 문제 풀이 코드에 `print()` 디버그 문을 남기지 않는다 — stdout 모드의 출력 비교를 오염시킨다.
- `expected` 와 `output` 을 한 예시에 동시에 두지 않는다 (모드 모호 → 에러).

### 종료코드
`0` 전부 통과 · `1` 실패 있음 · `2` 설정 오류(규약 위반).

## 구조
```
main.py         # CLI 러너 (단일 문제 파일)
runner.py       # 순수 로직 (로드·검증·실행)
problems/       # 문제 파일 (1문제 = 1파일)
tests/          # 러너 단위 테스트 (pytest)
```

설계·계획은 워크스페이스의 `project-docs/algorithm/`을 참조.
