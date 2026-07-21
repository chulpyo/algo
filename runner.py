"""예시 자동 실행 러너 — 순수 로직.

문제 모듈은 `solve`(callable)와 `EXAMPLES`(list[dict])를 노출한다.
예시 dict의 키로 모드를 판별한다:
  - `expected` 존재 → 반환값 모드: ``solve(*args, **kwargs) == expected``
  - `output` 존재   → stdout 모드: stdin=input 주입 후 ``solve()`` 의 출력을 캡처해 비교
한 파일의 모든 예시는 동일 모드여야 한다 (혼용/모호는 에러).

이 모듈은 부수효과가 없어 pytest에서 직접 import 한다.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


class ProblemError(Exception):
    """문제 파일이 규약을 위반했을 때 (설정 오류 — 종료코드 2)."""


@dataclass
class ExampleResult:
    index: int
    name: str | None
    passed: bool
    expected: Any
    actual: Any
    error: str | None = None  # solve 실행 중 예외 메시지 (있으면 실패)


def load_problem(path: str | Path) -> ModuleType:
    """파일 경로에서 문제 모듈을 로드한다 (import 시점 부수효과는 규약상 금지)."""
    p = Path(path)
    if not p.is_file():
        raise ProblemError(f"문제 파일을 찾을 수 없습니다: {p}")
    spec = importlib.util.spec_from_file_location(p.stem, p)
    if spec is None or spec.loader is None:
        raise ProblemError(f"모듈을 로드할 수 없습니다: {p}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise ProblemError(f"문제 파일 import 실패: {p}: {exc}") from exc
    return module


def _validate(module: ModuleType) -> tuple[Callable[..., Any], list]:
    solve = getattr(module, "solve", None)
    if not callable(solve):
        raise ProblemError("문제 파일에 callable `solve` 가 없습니다.")
    examples = getattr(module, "EXAMPLES", None)
    if not isinstance(examples, (list, tuple)):
        raise ProblemError("문제 파일에 list `EXAMPLES` 가 없습니다.")
    if len(examples) == 0:
        raise ProblemError("`EXAMPLES` 가 비어 있습니다.")
    return solve, list(examples)


def _mode_of(example: Any, index: int) -> str:
    pos = index + 1  # 사용자 대면 1-based
    if not isinstance(example, dict):
        raise ProblemError(f"예시 #{pos} 가 dict 가 아닙니다: {example!r}")
    has_expected = "expected" in example
    has_output = "output" in example
    if has_expected and has_output:
        raise ProblemError(
            f"예시 #{pos}: `expected`(반환값) 와 `output`(stdout) 을 동시에 가질 수 없습니다."
        )
    if has_expected:
        return "return"
    if has_output:
        return "stdout"
    raise ProblemError(
        f"예시 #{pos}: `expected`(반환값 모드) 또는 `output`(stdout 모드) 중 하나가 필요합니다."
    )


def _resolve_mode(examples: list) -> str:
    modes = {_mode_of(ex, i) for i, ex in enumerate(examples)}
    if len(modes) > 1:
        raise ProblemError(f"한 파일에서 모드를 혼용할 수 없습니다: {sorted(modes)}")
    return modes.pop()


def _run_return(solve: Callable[..., Any], example: dict, index: int) -> ExampleResult:
    args = example.get("args", ())
    kwargs = example.get("kwargs", {})
    expected = example["expected"]
    name = example.get("name")
    try:
        actual = solve(*args, **kwargs)
    except (Exception, SystemExit) as exc:  # solve의 exit()/sys.exit()도 격리 (KeyboardInterrupt는 전파)
        return ExampleResult(index, name, False, expected, None, error=f"{type(exc).__name__}: {exc}")
    return ExampleResult(index, name, actual == expected, expected, actual)


def _run_stdout(solve: Callable[..., Any], example: dict, index: int) -> ExampleResult:
    stdin_text = example.get("input", "")
    expected = str(example["output"]).rstrip("\n")  # 비교·표시에 동일한 정규화 값 사용
    name = example.get("name")
    buf = io.StringIO()
    saved_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(stdin_text)
        with contextlib.redirect_stdout(buf):
            solve()
    except (Exception, SystemExit) as exc:  # solve의 exit()/sys.exit()도 격리 (KeyboardInterrupt는 전파)
        actual = buf.getvalue().rstrip("\n")
        return ExampleResult(index, name, False, expected, actual, error=f"{type(exc).__name__}: {exc}")
    finally:
        sys.stdin = saved_stdin
    actual = buf.getvalue().rstrip("\n")
    return ExampleResult(index, name, actual == expected, expected, actual)


def run_examples(module: ModuleType) -> list[ExampleResult]:
    """검증된 문제 모듈의 모든 예시를 실행해 결과 리스트를 반환한다."""
    solve, examples = _validate(module)
    mode = _resolve_mode(examples)
    if mode == "return":
        run_one = _run_return
    elif mode == "stdout":
        run_one = _run_stdout
    else:  # 방어 — _resolve_mode는 두 모드만 반환하지만 향후 확장 시 조용한 오분기 방지
        raise ProblemError(f"알 수 없는 모드: {mode!r}")
    return [run_one(solve, ex, i) for i, ex in enumerate(examples)]


def run_problem(path: str | Path) -> list[ExampleResult]:
    """파일 경로 → 로드 → 실행. (설정 오류는 ProblemError)"""
    return run_examples(load_problem(path))
