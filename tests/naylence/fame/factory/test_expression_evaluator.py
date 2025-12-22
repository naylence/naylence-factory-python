import pytest

from naylence.fame.factory.expression_evaluator import (
    ExpressionEvaluator,
    ExpressionRecursionError,
)


def _nested_default_expression(depth: int) -> str:
    expression = "default"
    for _ in range(depth):
        expression = f"${{env:MISSING:{expression}}}"
    return expression


def test_nested_env_defaults(monkeypatch):
    monkeypatch.setenv("FALLBACK", "from_fallback")

    result = ExpressionEvaluator.evaluate(
        "${env:PRIMARY:${env:FALLBACK:default_value}}"
    )
    assert result == "from_fallback"

    monkeypatch.delenv("FALLBACK", raising=False)
    result = ExpressionEvaluator.evaluate(
        "${env:PRIMARY:${env:FALLBACK:default_value}}"
    )
    assert result == "default_value"


def test_nested_default_recursion_limit():
    expression = _nested_default_expression(12)
    with pytest.raises(ExpressionRecursionError):
        ExpressionEvaluator.evaluate(expression)
