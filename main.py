"""CLI 러너 — ``uv run main.py problems/<문제>.py``.

단일 문제 파일을 로드해 모든 예시를 실행하고 결과를 보고한다.
종료코드: 전부 통과 0 / 실패 있음 1 / 설정 오류(규약 위반) 2.
"""

from __future__ import annotations

import sys

from runner import ExampleResult, ProblemError, run_problem


def _format(result: ExampleResult) -> str:
    label = f"예시 #{result.index + 1}" + (f" ({result.name})" if result.name else "")
    if result.passed:
        return f"  PASS  {label}"
    lines = [f"  FAIL  {label}"]
    if result.error:
        lines.append(f"        예외: {result.error}")
    else:
        lines.append(f"        기대: {result.expected!r}")
        lines.append(f"        실제: {result.actual!r}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("사용법: uv run main.py problems/<문제>.py", file=sys.stderr)
        return 2
    path = argv[0]
    try:
        results = run_problem(path)
    except ProblemError as exc:
        print(f"[설정 오류] {exc}", file=sys.stderr)
        return 2

    print(f"실행: {path}")
    for r in results:
        print(_format(r))
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n{passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
