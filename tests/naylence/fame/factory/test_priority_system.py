"""
Simple test to verify the priority-based default selection system works.
"""

from typing import Any, Optional
from naylence.fame.factory import ResourceFactory
from naylence.fame.factory import ResourceConfig
from naylence.fame.factory import ExtensionManager


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


def test_priority_selection():
    """Test that the priority system selects the highest priority default."""

    # Create a test extension manager
    mgr = ExtensionManager(
        group="test.MockResourceFactory", base_type=MockResourceFactory
    )

    # Manually register our test factories (simulating entry point loading)
    mgr._registry["basic"] = BasicTestFactory
    mgr._registry["advanced"] = AdvancedTestFactory

    # Test the best default selection
    result = mgr.get_best_default_instance()

    assert result is not None, "No default found"
    factory_instance, factory_type = result

    # Should select the advanced factory due to higher priority
    assert factory_type == "advanced", (
        f"Selected wrong factory (type: {factory_type}), expected 'advanced'"
    )
    print(f"✅ Correctly selected advanced factory (type: {factory_type})")


def test_only_basic_available():
    """Test that basic factory is selected when advanced is not available."""

    # Create a test extension manager with only basic factory
    mgr = ExtensionManager(group="test.BasicOnlyFactory", base_type=MockResourceFactory)
    mgr._registry["basic"] = BasicTestFactory

    # Test the best default selection
    result = mgr.get_best_default_instance()

    assert result is not None, "No default found"
    factory_instance, factory_type = result

    # Should select the basic factory since it's the only one available
    assert factory_type == "basic", (
        f"Selected wrong factory (type: {factory_type}), expected 'basic'"
    )
    print(
        f"✅ Correctly selected basic factory when only option (type: {factory_type})"
    )


def test_fallback_compatibility():
    """Test that the old method still works for backward compatibility."""

    # Create a test extension manager
    mgr = ExtensionManager(group="test.FallbackFactory", base_type=MockResourceFactory)
    mgr._registry["basic"] = BasicTestFactory
    mgr._registry["advanced"] = AdvancedTestFactory

    # Test the old default selection method
    result = mgr.get_default_instance()

    assert result is not None, "No default found via legacy method"
    factory_instance, factory_type = result

    # Should find a default (may warn about multiple)
    assert factory_type in [
        "basic",
        "advanced",
    ], f"Legacy method failed (type: {factory_type})"
    print(f"✅ Legacy method found default factory (type: {factory_type})")
