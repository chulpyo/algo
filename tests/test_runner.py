"""러너 단위 테스트. 임시 문제 파일을 작성해 규약·실행·에러 처리를 검증한다."""

from pathlib import Path

import pytest

from runner import ProblemError, run_problem


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "prob.py"
    p.write_text(body, encoding="utf-8")
    return p


# --- 반환값 모드 ---------------------------------------------------------------

def test_return_mode_all_pass(tmp_path):
    p = _write(tmp_path, """
def solve(a, b):
    return a + b
EXAMPLES = [
    {"args": (1, 2), "expected": 3},
    {"args": (2, 2), "expected": 4},
]
""")
    results = run_problem(p)
    assert len(results) == 2
    assert all(r.passed for r in results)


def test_return_mode_failure(tmp_path):
    p = _write(tmp_path, """
def solve(a, b):
    return a - b
EXAMPLES = [{"args": (1, 2), "expected": 3}]
""")
    results = run_problem(p)
    assert results[0].passed is False
    assert results[0].actual == -1
    assert results[0].expected == 3


def test_return_mode_kwargs(tmp_path):
    p = _write(tmp_path, """
def solve(a, b=10):
    return a + b
EXAMPLES = [{"args": (1,), "kwargs": {"b": 5}, "expected": 6}]
""")
    assert run_problem(p)[0].passed


# --- stdout 모드 ---------------------------------------------------------------

def test_stdout_mode_pass(tmp_path):
    p = _write(tmp_path, """
import sys
def solve():
    a, b = map(int, sys.stdin.read().split())
    print(a + b)
EXAMPLES = [{"input": "1 2", "output": "3"}]
""")
    assert run_problem(p)[0].passed


def test_stdout_trailing_newline_normalized(tmp_path):
    p = _write(tmp_path, """
def solve():
    print("hi")
EXAMPLES = [{"output": "hi"}]
""")
    assert run_problem(p)[0].passed


def test_stdout_mode_failure(tmp_path):
    p = _write(tmp_path, """
def solve():
    print("nope")
EXAMPLES = [{"output": "yes"}]
""")
    assert not run_problem(p)[0].passed


def test_stdin_isolated_between_examples(tmp_path):
    p = _write(tmp_path, """
import sys
def solve():
    print(sys.stdin.read().strip().upper())
EXAMPLES = [
    {"input": "a", "output": "A"},
    {"input": "b", "output": "B"},
]
""")
    results = run_problem(p)
    assert all(r.passed for r in results)


# --- 규약 위반 (설정 오류) -----------------------------------------------------

def test_mixed_mode_errors(tmp_path):
    p = _write(tmp_path, """
def solve(a=0):
    return a
EXAMPLES = [{"args": (1,), "expected": 1}, {"output": "x"}]
""")
    with pytest.raises(ProblemError):
        run_problem(p)


def test_missing_solve(tmp_path):
    p = _write(tmp_path, 'EXAMPLES = [{"expected": 1}]')
    with pytest.raises(ProblemError):
        run_problem(p)


def test_missing_examples(tmp_path):
    p = _write(tmp_path, "def solve():\n    return 1\n")
    with pytest.raises(ProblemError):
        run_problem(p)


def test_empty_examples(tmp_path):
    p = _write(tmp_path, "def solve():\n    return 1\nEXAMPLES = []\n")
    with pytest.raises(ProblemError):
        run_problem(p)


def test_ambiguous_example_no_keys(tmp_path):
    p = _write(tmp_path, 'def solve():\n    return 1\nEXAMPLES = [{"args": ()}]\n')
    with pytest.raises(ProblemError):
        run_problem(p)


def test_expected_and_output_both(tmp_path):
    p = _write(tmp_path, 'def solve():\n    return 1\nEXAMPLES = [{"expected": 1, "output": "1"}]\n')
    with pytest.raises(ProblemError):
        run_problem(p)


def test_missing_file(tmp_path):
    with pytest.raises(ProblemError):
        run_problem(tmp_path / "does_not_exist.py")


# --- 예외 격리 -----------------------------------------------------------------

def test_solve_exception_isolated(tmp_path):
    p = _write(tmp_path, """
def solve(x):
    return 10 // x
EXAMPLES = [
    {"args": (0,), "expected": 0},
    {"args": (2,), "expected": 5},
]
""")
    results = run_problem(p)
    assert results[0].passed is False
    assert results[0].error is not None
    assert results[1].passed is True  # 앞 예시의 예외가 뒤 예시를 막지 않는다


def test_solve_sys_exit_isolated(tmp_path):
    # solve가 exit()/SystemExit을 던져도 러너가 죽지 않고 해당 예시만 실패 격리
    p = _write(tmp_path, """
def solve(x):
    if x == 0:
        raise SystemExit(1)
    return x
EXAMPLES = [
    {"args": (0,), "expected": 0},
    {"args": (2,), "expected": 2},
]
""")
    results = run_problem(p)
    assert results[0].passed is False
    assert results[0].error is not None
    assert results[1].passed is True


def test_stdout_expected_int_normalized_for_display(tmp_path):
    # output이 int여도 정규화된 문자열로 저장돼 표시가 비교와 일치
    p = _write(tmp_path, """
def solve():
    print("3")
EXAMPLES = [{"output": 3}]
""")
    r = run_problem(p)[0]
    assert r.passed is True
    assert r.expected == "3"  # int 원본이 아니라 정규화 문자열
