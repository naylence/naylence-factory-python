from naylence.fame.factory.expressions import Expressions, env


def test_env_accepts_non_string_defaults():
    assert Expressions.env("RETRIES", 3) == "${env:RETRIES:3}"
    assert Expressions.env("ENABLED", False) == "${env:ENABLED:False}"
    assert env("TIMEOUT", 12.5) == "${env:TIMEOUT:12.5}"
