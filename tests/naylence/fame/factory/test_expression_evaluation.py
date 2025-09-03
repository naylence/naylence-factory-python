import pytest
import os
from naylence.fame.factory import ExpressionEvaluationPolicy, ResourceConfig


class JwtAuthorizer(ResourceConfig):
    """Example JWT authorizer configuration."""

    type: str = "JwtAuthorizer"
    issuer: str
    audience: str
    required_scopes: str


def test_expression_evaluation():
    # Set up environment variables for testing
    os.environ["AUTH_ISSUER"] = "https://auth.prod.example.com"
    os.environ["AUTH_AUD"] = "naylence-production"
    # Note: AUTH_SCOPES is not set, so default will be used

    config_data = {
        "type": "JwtAuthorizer",
        "issuer": "${env:AUTH_ISSUER:https://auth.dev.local}",
        "audience": "${env:AUTH_AUD:naylence-node}",
        "required_scopes": "${env:AUTH_SCOPES:fabric.read fabric.write}",
    }

    # Test EVALUATE policy (default)
    config = JwtAuthorizer.model_validate(config_data)
    assert isinstance(config, JwtAuthorizer)
    assert config.issuer == "https://auth.prod.example.com"
    assert config.audience == "naylence-production"
    assert config.required_scopes == "fabric.read fabric.write"

    # Test LITERAL policy
    config_literal = JwtAuthorizer.model_validate(
        config_data,
        context={"expression_evaluation_policy": ExpressionEvaluationPolicy.LITERAL},
    )
    assert isinstance(config_literal, JwtAuthorizer)
    assert config_literal.issuer == "${env:AUTH_ISSUER:https://auth.dev.local}"
    assert config_literal.audience == "${env:AUTH_AUD:naylence-node}"
    assert (
        config_literal.required_scopes == "${env:AUTH_SCOPES:fabric.read fabric.write}"
    )

    # Test ERROR policy
    with pytest.raises(Exception):
        JwtAuthorizer.model_validate(
            config_data,
            context={"expression_evaluation_policy": ExpressionEvaluationPolicy.ERROR},
        )

    # Test backward compatibility with old disable flag
    config_compat = JwtAuthorizer.model_validate(
        config_data, context={"disable_expression_evaluation": True}
    )
    assert isinstance(config_compat, JwtAuthorizer)
    assert config_compat.issuer == "${env:AUTH_ISSUER:https://auth.dev.local}"
    assert config_compat.audience == "${env:AUTH_AUD:naylence-node}"
    assert (
        config_compat.required_scopes == "${env:AUTH_SCOPES:fabric.read fabric.write}"
    )

    # Test string policy values
    config_str_literal = JwtAuthorizer.model_validate(
        config_data, context={"expression_evaluation_policy": "literal"}
    )
    assert config_str_literal.issuer == "${env:AUTH_ISSUER:https://auth.dev.local}"

    # Serialization test
    serialized = config.model_dump()
    assert isinstance(serialized, dict)
    assert serialized["issuer"] == "https://auth.prod.example.com"
