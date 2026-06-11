"""
Integration tests for the MiniPar Flask HTTP API.

Uses Flask's built-in test client — no live server required.
Run with:  .venv/bin/python -m pytest tests/test_integration_api.py -q
"""

import json
import os
import sys

import pytest

# Ensure the project root is importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from interface.compiler_api import flask_app  # type: ignore


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"ok": True}


# ---------------------------------------------------------------------------
# /compile — success cases
# ---------------------------------------------------------------------------

HELLO = 'print("Hello, World!")'

FACTORIAL = """
func fatorial(n: number) -> number {
    if (n == 0 || n == 1) { return 1 }
    else { return n * fatorial(n - 1) }
}
print("5! =", fatorial(5))
"""

OO_COUNTER = """
class Counter {
    var value: number = 0
    func inc() -> number {
        value = value + 1
        return value
    }
}
var c: Counter = new Counter()
c.inc()
"""


def _post_compile(client, source, **opts):
    payload = {"source": source, **opts}
    return client.post(
        "/compile",
        data=json.dumps(payload),
        content_type="application/json",
    )


def test_compile_hello(client):
    res = _post_compile(client, HELLO, show_tac=True)
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["errors"] == []
    assert data["tac"]  # TAC should be non-empty


def test_compile_factorial(client):
    res = _post_compile(client, FACTORIAL, show_tac=True)
    data = res.get_json()
    assert data["ok"] is True
    assert "FUNC_BEGIN" in data["tac"] or len(data["tac"]) > 0


def test_compile_oo(client):
    res = _post_compile(client, OO_COUNTER, show_tac=True)
    data = res.get_json()
    assert data["ok"] is True
    assert data["tac"]


def test_compile_with_ast(client):
    res = _post_compile(client, HELLO, show_ast=True, show_tac=False)
    data = res.get_json()
    assert data["ok"] is True
    assert data["ast"]


def test_compile_with_c_generation(client):
    res = _post_compile(client, HELLO, generate_c=True, show_tac=False)
    data = res.get_json()
    assert data["ok"] is True
    assert data["c_code"]


# ---------------------------------------------------------------------------
# /compile — error cases
# ---------------------------------------------------------------------------

def test_compile_empty_source(client):
    res = _post_compile(client, "")
    assert res.status_code == 400
    data = res.get_json()
    assert data["ok"] is False


def test_compile_syntax_error(client):
    res = _post_compile(client, "func broken( -> void {}")
    data = res.get_json()
    assert data["ok"] is False
    assert data["errors"]


# ---------------------------------------------------------------------------
# /generate
# ---------------------------------------------------------------------------

def _post_generate(client, source, target):
    payload = {"source": source, "target": target}
    return client.post(
        "/generate",
        data=json.dumps(payload),
        content_type="application/json",
    )


def test_generate_c(client):
    res = _post_generate(client, HELLO, "c")
    assert res.status_code == 200
    assert res.content_type.startswith("text/plain")
    assert "int main(" in res.get_data(as_text=True)


def test_generate_arm(client):
    res = _post_generate(client, HELLO, "arm")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert ".text" in body or "main:" in body


def test_generate_invalid_target(client):
    res = _post_generate(client, HELLO, "llvm")
    assert res.status_code == 400
    assert res.get_json()["ok"] is False


def test_generate_empty_source(client):
    res = _post_generate(client, "", "c")
    assert res.status_code == 400


