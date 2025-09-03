import pytest
from typing import Any, Optional
from naylence.fame.factory import (
    ExtensionManager,
    ResourceFactory,
    ResourceConfig,
    create_default_resource,
)


class MockResource:
    """Mock resource type for testing."""

    def __init__(self, name: str):
        self.name = name


class MockResourceFactory(ResourceFactory[MockResource, ResourceConfig]):
    """Base factory interface for test resources."""

    pass


class BasicTestFactory(MockResourceFactory):
    """Basic implementation with lower priority."""

    type = "basic"
    is_default = True
    priority = 10

    async def create(
        self, config: Optional[ResourceConfig | dict[str, Any]] = None, **kwargs: Any
    ) -> MockResource:
        return MockResource("basic")


class AdvancedTestFactory(MockResourceFactory):
    """Advanced implementation with higher priority."""

    type = "advanced"
    is_default = True
    priority = 100

    async def create(
        self, config: Optional[ResourceConfig | dict[str, Any]] = None, **kwargs: Any
    ) -> MockResource:
        return MockResource("advanced")


@pytest.mark.asyncio
async def test_create_default_resource():
    """Test that create_default_resource uses priority-based selection."""

    # Set up the extension manager
    mgr = ExtensionManager.lazy_init(
        group="naylence.MockResourceFactory", base_type=MockResourceFactory
    )

    # Manually register our test factories (simulating entry point loading)
    mgr._registry["basic"] = BasicTestFactory
    mgr._registry["advanced"] = AdvancedTestFactory

    # Test the create_default_resource function
    resource = await create_default_resource(MockResourceFactory)

    # Should select the advanced factory due to higher priority
    assert resource is not None, "create_default_resource returned None"
    assert resource.name == "advanced", (
        f"create_default_resource selected wrong factory (resource.name: {resource.name}), expected 'advanced'"
    )
    print(
        f"✅ create_default_resource correctly selected advanced factory (resource.name: {resource.name})"
    )


@pytest.mark.asyncio
async def test_create_default_resource_with_config():
    """Test that create_default_resource works with additional config."""

    # Set up the extension manager
    mgr = ExtensionManager.lazy_init(
        group="naylence.MockResourceFactoryWithConfig", base_type=MockResourceFactory
    )

    # Manually register our test factories
    mgr._registry["basic"] = BasicTestFactory
    mgr._registry["advanced"] = AdvancedTestFactory

    # Test with config
    config = {"some_setting": "value"}
    resource = await create_default_resource(MockResourceFactory, config=config)

    # Should still select the advanced factory
    assert resource is not None, "create_default_resource with config returned None"
    assert resource.name == "advanced", (
        f"create_default_resource with config selected wrong factory (resource.name: {resource.name}), expected 'advanced'"
    )
    print(
        f"✅ create_default_resource with config correctly selected advanced factory (resource.name: {resource.name})"
    )
