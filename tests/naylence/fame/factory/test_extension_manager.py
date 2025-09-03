"""
Tests for ExtensionManager.get_extensions_by_type() method.
"""

from typing import Any, Optional
from naylence.fame.factory import ResourceFactory, ResourceConfig, ExtensionManager
from naylence.fame.factory.extension_manager import _EXT_MANAGER_CACHE


class MockResource:
    """Mock resource type for testing."""

    def __init__(self, name: str):
        self.name = name


class MockResourceFactory(ResourceFactory[MockResource, ResourceConfig]):
    """Base factory interface for test resources."""

    pass


class TestFactory1(MockResourceFactory):
    """First test factory implementation."""

    type = "test1"
    is_default = False
    priority = 10

    async def create(
        self, config: Optional[ResourceConfig | dict[str, Any]] = None, **kwargs: Any
    ) -> MockResource:
        return MockResource("test1")


class TestFactory2(MockResourceFactory):
    """Second test factory implementation."""

    type = "test2"
    is_default = True
    priority = 20

    async def create(
        self, config: Optional[ResourceConfig | dict[str, Any]] = None, **kwargs: Any
    ) -> MockResource:
        return MockResource("test2")


class TestFactory3(MockResourceFactory):
    """Third test factory implementation."""

    type = "test3"
    is_default = False
    priority = 30

    async def create(
        self, config: Optional[ResourceConfig | dict[str, Any]] = None, **kwargs: Any
    ) -> MockResource:
        return MockResource("test3")


class TestGetExtensionsByType:
    """Test cases for ExtensionManager.get_extensions_by_type() method."""

    def setUp(self):
        """Clear the extension manager cache before each test."""
        # Clear the cache to ensure tests are isolated
        _EXT_MANAGER_CACHE.clear()

    def test_get_extensions_by_type_returns_dict(self):
        """Test that get_extensions_by_type returns a dictionary."""
        self.setUp()

        # Get extensions by type - should return empty dict for unused base type
        extensions = ExtensionManager.get_extensions_by_type(MockResourceFactory)

        # Verify it returns a dictionary
        assert isinstance(extensions, dict)

    def test_get_extensions_by_type_contains_registered_factories(self):
        """Test that get_extensions_by_type returns all registered factories."""
        self.setUp()

        # Use lazy_init to get the manager that get_extensions_by_type will use
        mgr = ExtensionManager.lazy_init(
            group="naylence.MockResourceFactory", base_type=MockResourceFactory
        )

        # Manually register some test factories
        mgr._registry["test1"] = TestFactory1
        mgr._registry["test2"] = TestFactory2
        mgr._registry["test3"] = TestFactory3

        # Get extensions by type
        extensions = ExtensionManager.get_extensions_by_type(MockResourceFactory)

        # Verify all registered factories are present
        assert "test1" in extensions
        assert "test2" in extensions
        assert "test3" in extensions

        # Verify the factory classes are correct
        assert extensions["test1"] == TestFactory1
        assert extensions["test2"] == TestFactory2
        assert extensions["test3"] == TestFactory3

    def test_get_extensions_by_type_returns_readonly_copy(self):
        """Test that get_extensions_by_type returns a copy that doesn't affect the original registry."""
        self.setUp()

        # Use lazy_init to get the manager that get_extensions_by_type will use
        mgr = ExtensionManager.lazy_init(
            group="naylence.MockResourceFactory", base_type=MockResourceFactory
        )

        # Manually register some test factories
        mgr._registry["test1"] = TestFactory1
        mgr._registry["test2"] = TestFactory2

        # Get extensions by type
        extensions = ExtensionManager.get_extensions_by_type(MockResourceFactory)

        # Store original registry size and content
        original_size = len(mgr._registry)
        original_keys = set(mgr._registry.keys())

        # Modify the returned dictionary
        extensions["test3"] = TestFactory3
        extensions.pop("test1", None)

        # Verify the original registry is unchanged
        assert len(mgr._registry) == original_size
        assert set(mgr._registry.keys()) == original_keys
        assert "test1" in mgr._registry
        assert "test2" in mgr._registry
        assert "test3" not in mgr._registry

    def test_get_extensions_by_type_with_empty_registry(self):
        """Test that get_extensions_by_type works with empty registry."""
        self.setUp()

        # Get extensions by type for a base type with no registered factories
        extensions = ExtensionManager.get_extensions_by_type(MockResourceFactory)

        # Verify it returns an empty dictionary
        assert isinstance(extensions, dict)
        assert len(extensions) == 0

    def test_get_extensions_by_type_isolation_between_calls(self):
        """Test that multiple calls to get_extensions_by_type return independent copies."""
        self.setUp()

        # Use lazy_init to get the manager that get_extensions_by_type will use
        mgr = ExtensionManager.lazy_init(
            group="naylence.MockResourceFactory", base_type=MockResourceFactory
        )

        # Manually register some test factories
        mgr._registry["test1"] = TestFactory1
        mgr._registry["test2"] = TestFactory2

        # Get extensions by type twice
        extensions1 = ExtensionManager.get_extensions_by_type(MockResourceFactory)
        extensions2 = ExtensionManager.get_extensions_by_type(MockResourceFactory)

        # Verify they are separate objects
        assert extensions1 is not extensions2

        # Modify one copy
        extensions1["test3"] = TestFactory3
        extensions1.pop("test1", None)

        # Verify the other copy is unchanged
        assert "test1" in extensions2
        assert "test2" in extensions2
        assert "test3" not in extensions2
        assert len(extensions2) == 2

    def test_get_extensions_by_type_with_different_base_types(self):
        """Test that get_extensions_by_type works correctly with different base types."""
        self.setUp()

        # Define a different base type
        class AnotherMockResource:
            def __init__(self, value: int):
                self.value = value

        class AnotherMockResourceFactory(
            ResourceFactory[AnotherMockResource, ResourceConfig]
        ):
            pass

        class AnotherTestFactory(AnotherMockResourceFactory):
            type = "another"

            async def create(
                self,
                config: Optional[ResourceConfig | dict[str, Any]] = None,
                **kwargs: Any,
            ) -> AnotherMockResource:
                return AnotherMockResource(42)

        # Use lazy_init to get the managers that get_extensions_by_type will use
        mgr1 = ExtensionManager.lazy_init(
            group="naylence.MockResourceFactory", base_type=MockResourceFactory
        )
        mgr1._registry["test1"] = TestFactory1

        mgr2 = ExtensionManager.lazy_init(
            group="naylence.AnotherMockResourceFactory",
            base_type=AnotherMockResourceFactory,
        )
        mgr2._registry["another"] = AnotherTestFactory

        # Get extensions for each base type
        extensions1 = ExtensionManager.get_extensions_by_type(MockResourceFactory)
        extensions2 = ExtensionManager.get_extensions_by_type(
            AnotherMockResourceFactory
        )

        # Verify they return different registries
        assert "test1" in extensions1
        assert "another" not in extensions1

        assert "another" in extensions2
        assert "test1" not in extensions2

    def test_get_extensions_by_type_preserves_registry_content(self):
        """Test that the content of the returned dictionary matches the registry exactly."""
        self.setUp()

        # Use lazy_init to get the manager that get_extensions_by_type will use
        mgr = ExtensionManager.lazy_init(
            group="naylence.MockResourceFactory", base_type=MockResourceFactory
        )

        # Manually register some test factories
        expected_registry = {
            "test1": TestFactory1,
            "test2": TestFactory2,
            "test3": TestFactory3,
        }
        mgr._registry.update(expected_registry)

        # Get extensions by type
        extensions = ExtensionManager.get_extensions_by_type(MockResourceFactory)

        # Verify the content matches exactly
        assert extensions == expected_registry

        # Verify each key-value pair
        for name, factory_class in expected_registry.items():
            assert name in extensions
            assert extensions[name] is factory_class

    def test_get_extensions_by_type_uses_lazy_init_correctly(self):
        """Test that get_extensions_by_type uses lazy_init with correct parameters."""
        self.setUp()

        # Call get_extensions_by_type to trigger lazy_init
        ExtensionManager.get_extensions_by_type(MockResourceFactory)

        # Verify that a manager was created with the expected group and base_type
        expected_key = ("naylence.MockResourceFactory", MockResourceFactory)
        assert expected_key in _EXT_MANAGER_CACHE

        # Verify the cached manager has the correct properties
        cached_mgr = _EXT_MANAGER_CACHE[expected_key]
        assert cached_mgr._group == "naylence.MockResourceFactory"
        assert cached_mgr._base_type == MockResourceFactory

    def test_get_extensions_by_type_caching_behavior(self):
        """Test that get_extensions_by_type properly uses the cached manager."""
        self.setUp()

        # Use lazy_init to get the manager that get_extensions_by_type will use
        mgr = ExtensionManager.lazy_init(
            group="naylence.MockResourceFactory", base_type=MockResourceFactory
        )
        mgr._registry["test1"] = TestFactory1

        # First call should return the registry content
        extensions1 = ExtensionManager.get_extensions_by_type(MockResourceFactory)
        assert "test1" in extensions1

        # Add more factories to the cached manager
        mgr._registry["test2"] = TestFactory2

        # Second call should return updated registry content
        extensions2 = ExtensionManager.get_extensions_by_type(MockResourceFactory)
        assert "test1" in extensions2
        assert "test2" in extensions2

        # But the original returned dict should be unchanged (it's a copy)
        assert "test2" not in extensions1

    def test_get_extensions_by_type_alternative_immutable_implementation(self):
        """Test showing the alternative MappingProxyType implementation for truly immutable results."""
        import types

        self.setUp()

        # Use lazy_init to get the manager
        mgr = ExtensionManager.lazy_init(
            group="naylence.MockResourceFactory", base_type=MockResourceFactory
        )
        mgr._registry["test1"] = TestFactory1
        mgr._registry["test2"] = TestFactory2

        # Alternative implementation that returns truly immutable view
        def get_immutable_extensions_by_type(base_type):
            mgr = ExtensionManager.lazy_init(
                group="naylence." + base_type.__name__, base_type=base_type
            )
            return types.MappingProxyType(mgr._registry)

        # Get immutable extensions
        immutable_extensions = get_immutable_extensions_by_type(MockResourceFactory)

        # Verify it has the correct content
        assert "test1" in immutable_extensions
        assert "test2" in immutable_extensions
        assert immutable_extensions["test1"] == TestFactory1

        # Verify it's truly immutable - these should raise TypeError
        try:
            immutable_extensions["test3"] = TestFactory3  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected

        try:
            immutable_extensions.pop("test1")  # type: ignore
            assert False, "Should have raised AttributeError"
        except AttributeError:
            pass  # Expected - MappingProxyType doesn't have pop()

        # Verify original registry is still intact
        assert "test1" in mgr._registry
        assert "test2" in mgr._registry
