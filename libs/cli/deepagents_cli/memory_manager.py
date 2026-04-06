"""Structured memory management system for developers.

This module provides a comprehensive memory system that allows developers
to build and maintain a personal knowledge base throughout their interactions
with the Deep Agents CLI.

Features:
- Developer profile management
- Learning records and knowledge capture
- Entity relationship graph
- Memory search and retrieval
- Persistent storage via SQLite
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, NotRequired, TypedDict

logger = logging.getLogger(__name__)

# Memory database file location
MEMORY_DB_NAME = "memory.db"


class DeveloperProfile(TypedDict):
    """Developer profile information."""

    name: str
    """Developer's name or identifier."""

    role: str
    """Primary role (e.g., 'Backend Developer', 'Full Stack Engineer')."""

    experience_level: Literal["junior", "mid", "senior", "lead"]
    """Experience level."""

    primary_languages: list[str]
    """Primary programming languages (e.g., ['python', 'javascript'])."""

    preferred_frameworks: list[str]
    """Preferred frameworks and libraries."""

    code_style: dict[str, Any]
    """Code style preferences (indent, quotes, max_line_length, etc.)."""

    updated_at: str
    """ISO timestamp of last update."""


class Learning(TypedDict):
    """A captured learning or insight."""

    id: str
    """Unique identifier (UUID)."""

    content: str
    """The learning content/text."""

    source: Literal["user_feedback", "conversation", "correction", "discovery"]
    """How this learning was captured."""

    category: Literal["best_practice", "anti_pattern", "preference", "knowledge"]
    """Learning category."""

    tags: list[str]
    """Tags for organization and search."""

    session_id: str
    """Session ID where learning occurred."""

    created_at: str
    """ISO timestamp of creation."""

    confidence: float
    """Confidence level (0.0 - 1.0)."""


class Entity(TypedDict):
    """A concept or entity in the knowledge graph."""

    id: str
    """Unique identifier."""

    type: Literal["project", "library", "pattern", "person", "concept", "tool"]
    """Entity type."""

    name: str
    """Display name."""

    description: str
    """Entity description."""

    metadata: dict[str, Any]
    """Additional metadata."""

    created_at: str
    """ISO timestamp of creation."""

    last_accessed: str
    """ISO timestamp of last access."""


class MemoryManager:
    """Manages structured memory for a developer."""

    def __init__(self, memory_dir: Path | None = None) -> None:
        """Initialize the memory manager.

        Args:
            memory_dir: Directory for memory storage. Defaults to
                       ~/.deepagents/memory/
        """
        if memory_dir is None:
            memory_dir = Path.home() / ".deepagents" / "memory"

        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.memory_dir / MEMORY_DB_NAME
        self.profile_path = self.memory_dir / "developer_profile.json"

        # Initialize database
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the memory database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Learnings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learnings (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT NOT NULL,
                session_id TEXT,
                created_at TEXT NOT NULL,
                confidence REAL DEFAULT 1.0
            )
        """)

        # Entities table (knowledge graph nodes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL
            )
        """)

        # Relationships table (knowledge graph edges)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                from_entity TEXT NOT NULL,
                to_entity TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                context TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (from_entity) REFERENCES entities(id),
                FOREIGN KEY (to_entity) REFERENCES entities(id)
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_learnings_source
            ON learnings(source)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_learnings_category
            ON learnings(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_type
            ON entities(type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relationships_from
            ON relationships(from_entity)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relationships_to
            ON relationships(to_entity)
        """)

        conn.commit()
        conn.close()

    def load_or_create_profile(self) -> DeveloperProfile:
        """Load developer profile or create default one.

        Returns:
            Developer profile dictionary.
        """
        if self.profile_path.exists():
            try:
                with open(self.profile_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Could not load profile: {e}")

        # Create default profile
        profile: DeveloperProfile = {
            "name": "Developer",
            "role": "Software Developer",
            "experience_level": "mid",
            "primary_languages": [],
            "preferred_frameworks": [],
            "code_style": {
                "indent": 4,
                "quotes": "double",
                "max_line_length": 88,
            },
            "updated_at": datetime.now().isoformat(),
        }

        self.save_profile(profile)
        return profile

    def save_profile(self, profile: DeveloperProfile) -> None:
        """Save developer profile.

        Args:
            profile: Developer profile to save.
        """
        profile["updated_at"] = datetime.now().isoformat()
        with open(self.profile_path, "w") as f:
            json.dump(profile, f, indent=2)
        logger.debug(f"Saved profile to {self.profile_path}")

    def add_learning(
        self,
        content: str,
        source: Literal["user_feedback", "conversation", "correction", "discovery"],
        category: Literal["best_practice", "anti_pattern", "preference", "knowledge"],
        tags: list[str] | None = None,
        session_id: str | None = None,
        confidence: float = 1.0,
    ) -> str:
        """Add a learning to the memory.

        Args:
            content: The learning content.
            source: How the learning was captured.
            category: Learning category.
            tags: Optional tags for organization.
            session_id: Optional session ID.
            confidence: Confidence level (0.0 - 1.0).

        Returns:
            Learning ID.
        """
        from uuid_utils import uuid7

        learning_id = str(uuid7())
        tags = tags or []

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO learnings
            (id, content, source, category, tags, session_id, created_at, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            learning_id,
            content,
            source,
            category,
            json.dumps(tags),
            session_id,
            datetime.now().isoformat(),
            confidence,
        ))

        conn.commit()
        conn.close()

        logger.debug(f"Added learning: {learning_id}")
        return learning_id

    def search_learnings(
        self,
        query: str,
        category: str | None = None,
        source: str | None = None,
        limit: int = 10,
    ) -> list[Learning]:
        """Search for learnings.

        Args:
            query: Search query (searches in content and tags).
            category: Optional category filter.
            source: Optional source filter.
            limit: Maximum results to return.

        Returns:
            List of matching learnings.
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = "SELECT * FROM learnings WHERE 1=1"
        params: list[Any] = []

        # Full-text search in content and tags
        sql += " AND (content LIKE ? OR tags LIKE ?)"
        search_pattern = f"%{query}%"
        params.extend([search_pattern, search_pattern])

        if category:
            sql += " AND category = ?"
            params.append(category)

        if source:
            sql += " AND source = ?"
            params.append(source)

        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append(Learning(
                id=row["id"],
                content=row["content"],
                source=row["source"],
                category=row["category"],
                tags=json.loads(row["tags"]),
                session_id=row["session_id"],
                created_at=row["created_at"],
                confidence=row["confidence"],
            ))

        return results

    def add_entity(
        self,
        entity_id: str,
        entity_type: Literal["project", "library", "pattern", "person", "concept", "tool"],
        name: str,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add an entity to the knowledge graph.

        Args:
            entity_id: Unique entity identifier.
            entity_type: Type of entity.
            name: Display name.
            description: Entity description.
            metadata: Additional metadata.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO entities
                (id, type, name, description, metadata, created_at, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entity_id,
                entity_type,
                name,
                description,
                json.dumps(metadata or {}),
                now,
                now,
            ))
            conn.commit()
        finally:
            conn.close()

        logger.debug(f"Added entity: {entity_id}")

    def add_relationship(
        self,
        from_entity: str,
        to_entity: str,
        relation_type: str,
        context: str = "",
        confidence: float = 1.0,
    ) -> None:
        """Add a relationship between entities.

        Args:
            from_entity: Source entity ID.
            to_entity: Target entity ID.
            relation_type: Type of relationship (e.g., 'uses', 'depends_on').
            context: Optional context/description.
            confidence: Confidence level (0.0 - 1.0).
        """
        from uuid_utils import uuid7

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO relationships
                (id, from_entity, to_entity, relation_type, confidence, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid7()),
                from_entity,
                to_entity,
                relation_type,
                confidence,
                context,
                datetime.now().isoformat(),
            ))
            conn.commit()
        finally:
            conn.close()

        logger.debug(f"Added relationship: {from_entity} -> {to_entity}")

    def get_entity(
        self,
        entity_id: str,
    ) -> Entity | None:
        """Get an entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            Entity if found, None otherwise.
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
            row = cursor.fetchone()

            if row:
                return Entity(
                    id=row["id"],
                    type=row["type"],
                    name=row["name"],
                    description=row["description"],
                    metadata=json.loads(row["metadata"]),
                    created_at=row["created_at"],
                    last_accessed=row["last_accessed"],
                )
            return None
        finally:
            conn.close()

    def get_related_entities(
        self,
        entity_id: str,
        relation_type: str | None = None,
    ) -> list[tuple[Entity, str]]:
        """Get entities related to a given entity.

        Args:
            entity_id: Source entity ID.
            relation_type: Optional filter by relation type.

        Returns:
            List of (entity, relation_type) tuples.
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            if relation_type:
                cursor.execute("""
                    SELECT e.*, r.relation_type
                    FROM relationships r
                    JOIN entities e ON r.to_entity = e.id
                    WHERE r.from_entity = ? AND r.relation_type = ?
                """, (entity_id, relation_type))
            else:
                cursor.execute("""
                    SELECT e.*, r.relation_type
                    FROM relationships r
                    JOIN entities e ON r.to_entity = e.id
                    WHERE r.from_entity = ?
                """, (entity_id,))

            rows = cursor.fetchall()
            results = []

            for row in rows:
                entity = Entity(
                    id=row["id"],
                    type=row["type"],
                    name=row["name"],
                    description=row["description"],
                    metadata=json.loads(row["metadata"]),
                    created_at=row["created_at"],
                    last_accessed=row["last_accessed"],
                )
                results.append((entity, row["relation_type"]))

            return results
        finally:
            conn.close()

    def export_memory(self, output_path: Path) -> None:
        """Export all memory data to a JSON file.

        Args:
            output_path: Path to write the exported memory.
        """
        profile = self.load_or_create_profile()

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all learnings
        cursor.execute("SELECT * FROM learnings ORDER BY created_at DESC")
        learnings = []
        for row in cursor.fetchall():
            learnings.append({
                "id": row["id"],
                "content": row["content"],
                "source": row["source"],
                "category": row["category"],
                "tags": json.loads(row["tags"]),
                "created_at": row["created_at"],
                "confidence": row["confidence"],
            })

        # Get all entities
        cursor.execute("SELECT * FROM entities")
        entities = []
        for row in cursor.fetchall():
            entities.append({
                "id": row["id"],
                "type": row["type"],
                "name": row["name"],
                "description": row["description"],
                "metadata": json.loads(row["metadata"]),
                "created_at": row["created_at"],
            })

        conn.close()

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "profile": profile,
            "learnings": learnings,
            "entities": entities,
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Exported memory to {output_path}")

    def get_memory_stats(self) -> dict[str, Any]:
        """Get statistics about the memory.

        Returns:
            Dictionary with memory statistics.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM learnings")
            learnings_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM entities")
            entities_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM relationships")
            relationships_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM learnings
                GROUP BY category
            """)
            learnings_by_category = dict(cursor.fetchall())

            cursor.execute("""
                SELECT source, COUNT(*) as count
                FROM learnings
                GROUP BY source
            """)
            learnings_by_source = dict(cursor.fetchall())

            return {
                "learnings_count": learnings_count,
                "entities_count": entities_count,
                "relationships_count": relationships_count,
                "learnings_by_category": learnings_by_category,
                "learnings_by_source": learnings_by_source,
                "memory_dir": str(self.memory_dir),
                "db_size_mb": self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0,
            }
        finally:
            conn.close()
