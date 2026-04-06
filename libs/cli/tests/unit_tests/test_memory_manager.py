"""Tests for the memory manager system."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from deepagents_cli.memory_manager import (
    DeveloperProfile,
    Entity,
    Learning,
    MemoryManager,
)


@pytest.fixture
def temp_memory_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for memory storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def memory_manager(temp_memory_dir: Path) -> MemoryManager:
    """Create a MemoryManager with a temporary directory."""
    return MemoryManager(memory_dir=temp_memory_dir)


class TestMemoryManager:
    """Test suite for MemoryManager."""

    def test_initialization(self, memory_manager: MemoryManager) -> None:
        """Test that MemoryManager initializes correctly."""
        assert memory_manager.memory_dir.exists()
        assert memory_manager.db_path.exists()

    def test_load_or_create_profile(self, memory_manager: MemoryManager) -> None:
        """Test loading or creating a developer profile."""
        profile = memory_manager.load_or_create_profile()

        assert isinstance(profile, dict)
        assert profile["name"] == "Developer"
        assert profile["role"] == "Software Developer"
        assert profile["experience_level"] == "mid"
        assert isinstance(profile["primary_languages"], list)

    def test_save_profile(self, memory_manager: MemoryManager) -> None:
        """Test saving a developer profile."""
        profile: DeveloperProfile = {
            "name": "John Doe",
            "role": "Backend Engineer",
            "experience_level": "senior",
            "primary_languages": ["python", "go"],
            "preferred_frameworks": ["fastapi", "django"],
            "code_style": {"indent": 2, "quotes": "single"},
            "updated_at": "2026-04-06T10:00:00",
        }

        memory_manager.save_profile(profile)

        loaded = memory_manager.load_or_create_profile()
        assert loaded["name"] == "John Doe"
        assert loaded["role"] == "Backend Engineer"

    def test_add_learning(self, memory_manager: MemoryManager) -> None:
        """Test adding a learning to memory."""
        learning_id = memory_manager.add_learning(
            content="Always use type hints in Python",
            source="user_feedback",
            category="best_practice",
            tags=["python", "typing"],
        )

        assert isinstance(learning_id, str)
        assert len(learning_id) > 0

    def test_search_learnings(self, memory_manager: MemoryManager) -> None:
        """Test searching for learnings."""
        # Add some test learnings
        memory_manager.add_learning(
            content="Use async/await for I/O operations",
            source="conversation",
            category="best_practice",
            tags=["python", "async"],
        )
        memory_manager.add_learning(
            content="Avoid nested callbacks",
            source="user_feedback",
            category="anti_pattern",
            tags=["javascript"],
        )

        # Search for learnings
        results = memory_manager.search_learnings("async", limit=10)

        assert len(results) >= 1
        assert any("async" in r["content"].lower() for r in results)

    def test_search_learnings_empty(self, memory_manager: MemoryManager) -> None:
        """Test searching with no results."""
        results = memory_manager.search_learnings("nonexistent", limit=10)
        assert len(results) == 0

    def test_search_learnings_with_filters(self, memory_manager: MemoryManager) -> None:
        """Test searching with category and source filters."""
        memory_manager.add_learning(
            content="Use list comprehensions",
            source="user_feedback",
            category="best_practice",
            tags=["python"],
        )
        memory_manager.add_learning(
            content="Global state is bad",
            source="correction",
            category="anti_pattern",
            tags=["general"],
        )

        # Search by category
        results = memory_manager.search_learnings(
            "use", category="best_practice", limit=10
        )
        assert all(r["category"] == "best_practice" for r in results)

        # Search by source
        results = memory_manager.search_learnings(
            "Python", source="user_feedback", limit=10
        )
        assert all(r["source"] == "user_feedback" for r in results)

    def test_add_entity(self, memory_manager: MemoryManager) -> None:
        """Test adding an entity to the knowledge graph."""
        memory_manager.add_entity(
            entity_id="project-deepagents",
            entity_type="project",
            name="Deep Agents",
            description="An AI agent framework",
            metadata={"github": "langchain-ai/deepagents"},
        )

        entity = memory_manager.get_entity("project-deepagents")
        assert entity is not None
        assert entity["name"] == "Deep Agents"
        assert entity["type"] == "project"

    def test_add_relationship(self, memory_manager: MemoryManager) -> None:
        """Test adding a relationship between entities."""
        # Create entities
        memory_manager.add_entity("lib-fastapi", "library", "FastAPI")
        memory_manager.add_entity("proj-api", "project", "My API")

        # Add relationship
        memory_manager.add_relationship(
            from_entity="proj-api",
            to_entity="lib-fastapi",
            relation_type="uses",
            context="Web framework for REST APIs",
        )

        # Check relationship
        related = memory_manager.get_related_entities("proj-api")
        assert len(related) >= 1
        assert any(e[0]["id"] == "lib-fastapi" for e in related)

    def test_get_memory_stats(self, memory_manager: MemoryManager) -> None:
        """Test retrieving memory statistics."""
        # Add some data
        memory_manager.add_learning(
            content="Test learning",
            source="user_feedback",
            category="best_practice",
        )
        memory_manager.add_entity("test-ent", "concept", "Test Entity")

        stats = memory_manager.get_memory_stats()

        assert "learnings_count" in stats
        assert "entities_count" in stats
        assert "relationships_count" in stats
        assert "learnings_by_category" in stats
        assert "learnings_by_source" in stats
        assert stats["learnings_count"] >= 1
        assert stats["entities_count"] >= 1

    def test_export_memory(self, temp_memory_dir: Path) -> None:
        """Test exporting memory to JSON."""
        manager = MemoryManager(memory_dir=temp_memory_dir)

        # Add some data
        manager.add_learning(
            content="Export test",
            source="conversation",
            category="knowledge",
        )

        # Export
        export_path = temp_memory_dir / "export.json"
        manager.export_memory(export_path)

        assert export_path.exists()

        # Verify content
        import json

        with open(export_path) as f:
            data = json.load(f)

        assert "profile" in data
        assert "learnings" in data
        assert "entities" in data
        assert len(data["learnings"]) >= 1
