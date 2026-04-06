"""Tests for dynamic subagent spawning functionality.

Tests the DynamicSubAgentRegistry and spawn_config support in task tool.
"""

import pytest
from unittest.mock import MagicMock, patch

from deepagents.middleware.subagents import (
    DynamicSubAgentRegistry,
    SpawnAgentConfig,
    TaskToolSchema,
)


class TestSpawnAgentConfig:
    """Tests for SpawnAgentConfig TypedDict."""

    def test_spawn_config_minimal(self) -> None:
        """Test minimal spawn configuration."""
        config: SpawnAgentConfig = {
            "name": "test-agent",
            "role": "Test role",
            "instructions": "Test instructions",
            "tools": ["read_file", "write_file"],
        }

        assert config["name"] == "test-agent"
        assert config["role"] == "Test role"
        assert config["instructions"] == "Test instructions"
        assert config["tools"] == ["read_file", "write_file"]

    def test_spawn_config_with_model(self) -> None:
        """Test spawn configuration with model override."""
        config: SpawnAgentConfig = {
            "name": "test-agent",
            "role": "Test role",
            "instructions": "Test instructions",
            "tools": ["read_file"],
            "model": "anthropic:claude-opus",
        }

        assert config["model"] == "anthropic:claude-opus"

    def test_spawn_config_empty_tools(self) -> None:
        """Test spawn configuration with empty tools list."""
        config: SpawnAgentConfig = {
            "name": "test-agent",
            "role": "Test role",
            "instructions": "Test instructions",
            "tools": [],
        }

        assert config["tools"] == []


class TestTaskToolSchema:
    """Tests for TaskToolSchema Pydantic model."""

    def test_schema_with_subagent_type(self) -> None:
        """Test schema with subagent_type parameter."""
        schema = TaskToolSchema(
            description="Test task",
            subagent_type="general-purpose",
        )

        assert schema.description == "Test task"
        assert schema.subagent_type == "general-purpose"

    def test_schema_with_spawn_config(self) -> None:
        """Test schema with spawn_config parameter."""
        spawn_config: SpawnAgentConfig = {
            "name": "custom-agent",
            "role": "Custom analyzer",
            "instructions": "Analyze data",
            "tools": ["analyze"],
        }

        schema = TaskToolSchema(
            description="Analyze the data",
            spawn_config=spawn_config,
        )

        assert schema.description == "Analyze the data"
        assert schema.spawn_config == spawn_config

    def test_schema_default_subagent_type(self) -> None:
        """Test schema with default empty subagent_type."""
        schema = TaskToolSchema(description="Test task")

        assert schema.subagent_type == ""


class TestDynamicSubAgentRegistry:
    """Tests for DynamicSubAgentRegistry class."""

    def test_registry_init(self) -> None:
        """Test registry initialization."""
        backend = MagicMock()
        registry = DynamicSubAgentRegistry(
            backend=backend,
            parent_model="openai:gpt-4o",
        )

        assert registry._backend == backend
        assert registry._parent_model == "openai:gpt-4o"
        assert registry._spawned_agents == {}
        assert registry._parent_tools == []

    def test_registry_list_active_empty(self) -> None:
        """Test listing active agents when empty."""
        backend = MagicMock()
        registry = DynamicSubAgentRegistry(backend=backend)

        assert registry.list_active() == []

    def test_registry_get_nonexistent(self) -> None:
        """Test retrieving a non-existent agent."""
        backend = MagicMock()
        registry = DynamicSubAgentRegistry(backend=backend)

        result = registry.get("nonexistent")

        assert result is None

    @patch("deepagents.middleware.subagents.create_agent")
    @patch("deepagents.middleware.subagents.resolve_model")
    def test_registry_spawn_basic(self, mock_resolve_model, mock_create_agent) -> None:
        """Test spawning a basic subagent."""
        backend = MagicMock()
        mock_model = MagicMock()
        mock_resolve_model.return_value = mock_model
        mock_runnable = MagicMock()
        mock_create_agent.return_value = mock_runnable

        registry = DynamicSubAgentRegistry(backend=backend)

        config: SpawnAgentConfig = {
            "name": "test-agent",
            "role": "Test",
            "instructions": "Do something",
            "tools": [],
        }

        name, runnable = registry.spawn(config)

        assert name == "test-agent"
        assert runnable == mock_runnable
        assert "test-agent" in registry.list_active()

    @patch("deepagents.middleware.subagents.create_agent")
    @patch("deepagents.middleware.subagents.resolve_model")
    def test_registry_spawn_with_model_override(
        self, mock_resolve_model, mock_create_agent
    ) -> None:
        """Test spawning with model override."""
        backend = MagicMock()
        mock_model = MagicMock()
        mock_resolve_model.return_value = mock_model
        mock_runnable = MagicMock()
        mock_create_agent.return_value = mock_runnable

        registry = DynamicSubAgentRegistry(backend=backend, parent_model="openai:gpt-4o")

        config: SpawnAgentConfig = {
            "name": "test-agent",
            "role": "Test",
            "instructions": "Do something",
            "tools": [],
            "model": "anthropic:claude-opus",
        }

        name, runnable = registry.spawn(config)

        mock_resolve_model.assert_called_once_with("anthropic:claude-opus")
        assert name == "test-agent"

    @patch("deepagents.middleware.subagents.create_agent")
    @patch("deepagents.middleware.subagents.resolve_model")
    def test_registry_spawn_caching(self, mock_resolve_model, mock_create_agent) -> None:
        """Test that spawned agents are cached."""
        backend = MagicMock()
        mock_model = MagicMock()
        mock_resolve_model.return_value = mock_model
        mock_runnable = MagicMock()
        mock_create_agent.return_value = mock_runnable

        registry = DynamicSubAgentRegistry(backend=backend)

        config: SpawnAgentConfig = {
            "name": "test-agent",
            "role": "Test",
            "instructions": "Do something",
            "tools": [],
        }

        # First spawn
        name1, runnable1 = registry.spawn(config)
        # Second spawn (should return cached)
        name2, runnable2 = registry.spawn(config)

        assert name1 == name2
        assert runnable1 == runnable2
        # create_agent should only be called once
        mock_create_agent.assert_called_once()

    def test_registry_resolve_tools_by_name_empty(self) -> None:
        """Test resolving tool names with empty parent tools."""
        backend = MagicMock()
        registry = DynamicSubAgentRegistry(backend=backend, parent_tools=[])

        result = registry._resolve_tools_by_name(["read_file", "write_file"])

        assert result == []

    def test_registry_resolve_tools_by_name_matching(self) -> None:
        """Test resolving tool names with matching tools."""
        backend = MagicMock()

        # Create mock tools
        read_tool = MagicMock()
        read_tool.name = "read_file"
        write_tool = MagicMock()
        write_tool.name = "write_file"

        registry = DynamicSubAgentRegistry(
            backend=backend,
            parent_tools=[read_tool, write_tool],
        )

        result = registry._resolve_tools_by_name(["read_file", "write_file"])

        assert result == [read_tool, write_tool]

    def test_registry_resolve_tools_by_name_partial(self) -> None:
        """Test resolving tool names with partial matches."""
        backend = MagicMock()

        # Create mock tools
        read_tool = MagicMock()
        read_tool.name = "read_file"
        write_tool = MagicMock()
        write_tool.name = "write_file"

        registry = DynamicSubAgentRegistry(
            backend=backend,
            parent_tools=[read_tool, write_tool],
        )

        # Request only read_file and non-existent tool
        result = registry._resolve_tools_by_name(["read_file", "nonexistent"])

        assert result == [read_tool]


class TestTaskToolSchemaValidation:
    """Tests for TaskToolSchema validation."""

    def test_schema_requires_description(self) -> None:
        """Test that description is required."""
        with pytest.raises(Exception):  # Pydantic validation error
            TaskToolSchema(subagent_type="general-purpose")  # type: ignore

    def test_schema_spawn_config_optional(self) -> None:
        """Test that spawn_config is optional."""
        schema = TaskToolSchema(
            description="Test task",
            subagent_type="general-purpose",
        )

        assert not hasattr(schema, "spawn_config") or schema.spawn_config is None

    def test_schema_both_parameters_allowed(self) -> None:
        """Test that both subagent_type and spawn_config can be provided."""
        spawn_config: SpawnAgentConfig = {
            "name": "custom",
            "role": "Role",
            "instructions": "Do it",
            "tools": [],
        }

        schema = TaskToolSchema(
            description="Test",
            subagent_type="general-purpose",
            spawn_config=spawn_config,
        )

        assert schema.subagent_type == "general-purpose"
        assert schema.spawn_config == spawn_config


class TestSpawnAgentConfigTypes:
    """Tests for SpawnAgentConfig type validation."""

    def test_config_tools_must_be_list(self) -> None:
        """Test that tools must be a list."""
        config: SpawnAgentConfig = {
            "name": "test",
            "role": "test",
            "instructions": "test",
            "tools": ["tool1", "tool2"],
        }

        assert isinstance(config["tools"], list)

    def test_config_name_must_be_string(self) -> None:
        """Test that name must be a string."""
        config: SpawnAgentConfig = {
            "name": "test-agent",
            "role": "test",
            "instructions": "test",
            "tools": [],
        }

        assert isinstance(config["name"], str)

    def test_config_instructions_must_be_string(self) -> None:
        """Test that instructions must be a string."""
        config: SpawnAgentConfig = {
            "name": "test",
            "role": "test",
            "instructions": "Detailed instructions here",
            "tools": [],
        }

        assert isinstance(config["instructions"], str)
