"""File-based 3-layer memory management system.

Implements the three memory layers required for long-term knowledge retention:

- Layer 1 ``user/profile``: Developer preferences and habits.
  Stored in ``~/.deepagents/agent/AGENTS.md``. Injected every session.

- Layer 2 ``project/context``: Project-specific rules and decisions.
  Stored in ``{cwd}/.deepagents/AGENTS.md``. Injected per project.

- Layer 3 ``domain/knowledge``: Accumulated domain knowledge.
  Stored in ``~/.deepagents/agent/skills/{name}/SKILL.md``.
  Loaded by SkillsMiddleware when relevant.

All three layers are plain markdown files that the existing CLI infrastructure
(``agent.py``, ``local_context.py``, ``SkillsMiddleware``) already reads and
injects into the system prompt automatically — no separate injection code needed.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Section headers used in AGENTS.md files
_USER_PROFILE_SECTION = "## User Preferences"
_PROJECT_CONTEXT_SECTION = "## Project Context"
_DOMAIN_KNOWLEDGE_SECTION = "## Domain Knowledge"

# Default global agent directory name
_AGENT_DIR = "agent"


def _deepagents_home() -> Path:
    """Return the base ~/.deepagents directory."""
    return Path.home() / ".deepagents"


def _now_iso() -> str:
    """Return current timestamp in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


class UserProfileMemory:
    """Layer 1: Developer preferences, habits, and personal guidelines.

    Stored in ``~/.deepagents/agent/AGENTS.md``.
    This file is automatically loaded by ``agent.py`` and injected into the
    system prompt at every session start.

    What to store:
        - Preferred languages, frameworks, coding style
        - Output format preferences (language, verbosity)
        - Persistent feedback ("always use type hints")

    When to store: User provides preference or feedback about AI behavior.
    When to load: Every session (automatic via agent.py).
    Correction policy: Replace conflicting entry with newer one using `correct()`.
    """

    def __init__(self, assistant_id: str = _AGENT_DIR) -> None:
        """Initialize user profile memory.

        Args:
            assistant_id: Agent directory name under ~/.deepagents/.
        """
        self._path = _deepagents_home() / assistant_id / "AGENTS.md"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        """Path to the AGENTS.md file."""
        return self._path

    def load(self) -> str:
        """Load the full AGENTS.md content.

        Returns:
            File content as string, or empty string if file does not exist.
        """
        if not self._path.exists():
            return ""
        return self._path.read_text(encoding="utf-8")

    def append(self, entry: str) -> None:
        """Append an entry under the User Preferences section.

        Creates the file and section header if they do not exist.

        Args:
            entry: Preference or guideline to add (single line or short paragraph).
        """
        content = self.load()
        timestamp = _now_iso()
        bullet = f"- [{timestamp}] {entry.strip()}"

        if _USER_PROFILE_SECTION in content:
            # Insert after the section header
            lines = content.splitlines()
            insert_idx = next(
                (i + 1 for i, line in enumerate(lines) if line.strip() == _USER_PROFILE_SECTION),
                len(lines),
            )
            lines.insert(insert_idx, bullet)
            new_content = "\n".join(lines) + "\n"
        else:
            # Create section at the end
            separator = "\n" if content and not content.endswith("\n\n") else ""
            new_content = content + separator + f"\n{_USER_PROFILE_SECTION}\n{bullet}\n"

        self._path.write_text(new_content, encoding="utf-8")
        logger.debug("Added user preference entry to %s", self._path)

    def search(self, query: str) -> list[str]:
        """Search for entries matching a query string.

        Args:
            query: Case-insensitive search term.

        Returns:
            List of matching lines.
        """
        query_lower = query.lower()
        return [
            line.strip()
            for line in self.load().splitlines()
            if query_lower in line.lower() and line.strip().startswith("-")
        ]

    def correct(self, old_text: str, new_text: str) -> bool:
        """Replace an existing entry with updated content.

        Use this when a preference changes — the newer evidence replaces the old.

        Args:
            old_text: Exact text to find (partial match allowed).
            new_text: Replacement text.

        Returns:
            `True` if a replacement was made, `False` if `old_text` was not found.
        """
        content = self.load()
        if old_text not in content:
            return False
        updated = content.replace(old_text, new_text, 1)
        self._path.write_text(updated, encoding="utf-8")
        logger.debug("Corrected user profile entry in %s", self._path)
        return True

    def stats(self) -> dict[str, Any]:
        """Return statistics for this layer.

        Returns:
            Dict with path, exists, size_bytes, and entry_count.
        """
        exists = self._path.exists()
        return {
            "layer": "user/profile",
            "path": str(self._path),
            "exists": exists,
            "size_bytes": self._path.stat().st_size if exists else 0,
            "entry_count": len(self.search("")) if exists else 0,
        }


class ProjectContextMemory:
    """Layer 2: Project-specific rules, decisions, and constraints.

    Stored in ``{project_dir}/.deepagents/AGENTS.md``.
    This file is automatically detected and injected by ``local_context.py``
    and ``agent.py`` when the CLI runs in that project directory.

    What to store:
        - Architecture decisions (e.g., "use FastAPI, not Flask")
        - Naming conventions and coding standards
        - Forbidden libraries, required test rules
        - Key file structure decisions

    When to store: User states a project constraint or rule.
    When to load: Automatically when working in the project directory.
    Correction policy: Replace outdated rule with `correct()`.
    """

    def __init__(self, project_dir: Path | None = None) -> None:
        """Initialize project context memory.

        Args:
            project_dir: Project root directory. Defaults to current directory.
        """
        base = project_dir or Path.cwd()
        self._path = base / ".deepagents" / "AGENTS.md"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        """Path to the project AGENTS.md file."""
        return self._path

    def load(self) -> str:
        """Load the project AGENTS.md content.

        Returns:
            File content as string, or empty string if file does not exist.
        """
        if not self._path.exists():
            return ""
        return self._path.read_text(encoding="utf-8")

    def append(self, entry: str) -> None:
        """Append an entry under the Project Context section.

        Args:
            entry: Project rule or decision to record.
        """
        content = self.load()
        timestamp = _now_iso()
        bullet = f"- [{timestamp}] {entry.strip()}"

        if _PROJECT_CONTEXT_SECTION in content:
            lines = content.splitlines()
            insert_idx = next(
                (i + 1 for i, line in enumerate(lines) if line.strip() == _PROJECT_CONTEXT_SECTION),
                len(lines),
            )
            lines.insert(insert_idx, bullet)
            new_content = "\n".join(lines) + "\n"
        else:
            separator = "\n" if content and not content.endswith("\n\n") else ""
            new_content = content + separator + f"\n{_PROJECT_CONTEXT_SECTION}\n{bullet}\n"

        self._path.write_text(new_content, encoding="utf-8")
        logger.debug("Added project context entry to %s", self._path)

    def search(self, query: str) -> list[str]:
        """Search for entries matching a query string.

        Args:
            query: Case-insensitive search term.

        Returns:
            List of matching lines.
        """
        query_lower = query.lower()
        return [
            line.strip()
            for line in self.load().splitlines()
            if query_lower in line.lower() and line.strip().startswith("-")
        ]

    def correct(self, old_text: str, new_text: str) -> bool:
        """Replace an existing project rule with updated content.

        Args:
            old_text: Exact text to find (partial match allowed).
            new_text: Replacement text.

        Returns:
            `True` if a replacement was made, `False` if `old_text` was not found.
        """
        content = self.load()
        if old_text not in content:
            return False
        updated = content.replace(old_text, new_text, 1)
        self._path.write_text(updated, encoding="utf-8")
        logger.debug("Corrected project context entry in %s", self._path)
        return True

    def stats(self) -> dict[str, Any]:
        """Return statistics for this layer.

        Returns:
            Dict with path, exists, size_bytes, and entry_count.
        """
        exists = self._path.exists()
        return {
            "layer": "project/context",
            "path": str(self._path),
            "exists": exists,
            "size_bytes": self._path.stat().st_size if exists else 0,
            "entry_count": len(self.search("")) if exists else 0,
        }


class DomainKnowledgeMemory:
    """Layer 3: Accumulated domain knowledge organized as skills.

    Each knowledge domain is stored in its own skill file:
    ``~/.deepagents/agent/skills/{skill_name}/SKILL.md``.

    This directory is automatically loaded by ``SkillsMiddleware`` and injected
    into the system prompt when the agent determines the skill is relevant to
    the current task.

    What to store:
        - Business rules and domain terms
        - API contracts and data schemas
        - Operational procedures and workflows
        - Domain-specific terminology

    When to store: User inputs domain-specific knowledge.
    When to load: Automatically by SkillsMiddleware when relevant.
    Correction policy: Replace conflicting rule with `correct()` on the skill file.
    """

    def __init__(self, assistant_id: str = _AGENT_DIR) -> None:
        """Initialize domain knowledge memory.

        Args:
            assistant_id: Agent directory name under ~/.deepagents/.
        """
        self._skills_dir = _deepagents_home() / assistant_id / "skills"
        self._skills_dir.mkdir(parents=True, exist_ok=True)

    @property
    def skills_dir(self) -> Path:
        """Path to the skills directory."""
        return self._skills_dir

    def skill_path(self, skill_name: str) -> Path:
        """Return the SKILL.md path for a given skill name.

        Args:
            skill_name: Domain skill identifier (e.g., 'payment', 'billing').

        Returns:
            Path to the SKILL.md file.
        """
        return self._skills_dir / skill_name / "SKILL.md"

    def append(self, skill_name: str, entry: str) -> Path:
        """Append a domain knowledge entry to a skill file.

        Creates the skill file with proper SKILL.md frontmatter if it does not exist.

        Args:
            skill_name: Domain skill identifier (e.g., 'payment-rules').
            entry: Domain knowledge fact to append.

        Returns:
            Path to the updated skill file.
        """
        skill_file = self.skill_path(skill_name)
        skill_file.parent.mkdir(parents=True, exist_ok=True)

        timestamp = _now_iso()
        bullet = f"- [{timestamp}] {entry.strip()}"

        if skill_file.exists():
            content = skill_file.read_text(encoding="utf-8")
            if _DOMAIN_KNOWLEDGE_SECTION in content:
                lines = content.splitlines()
                insert_idx = next(
                    (i + 1 for i, line in enumerate(lines) if line.strip() == _DOMAIN_KNOWLEDGE_SECTION),
                    len(lines),
                )
                lines.insert(insert_idx, bullet)
                new_content = "\n".join(lines) + "\n"
            else:
                new_content = content.rstrip() + f"\n\n{_DOMAIN_KNOWLEDGE_SECTION}\n{bullet}\n"
        else:
            # Create new skill file with proper frontmatter
            new_content = (
                f"---\n"
                f"name: {skill_name}\n"
                f'description: "Domain knowledge for {skill_name}. '
                f'Use when working with {skill_name}-related tasks."\n'
                f"---\n\n"
                f"# {skill_name.replace('-', ' ').title()}\n\n"
                f"{_DOMAIN_KNOWLEDGE_SECTION}\n"
                f"{bullet}\n"
            )

        skill_file.write_text(new_content, encoding="utf-8")
        logger.debug("Added domain knowledge to %s", skill_file)
        return skill_file

    def load(self, skill_name: str) -> str:
        """Load the content of a domain skill file.

        Args:
            skill_name: Domain skill identifier.

        Returns:
            File content as string, or empty string if not found.
        """
        skill_file = self.skill_path(skill_name)
        if not skill_file.exists():
            return ""
        return skill_file.read_text(encoding="utf-8")

    def list_skills(self) -> list[str]:
        """List all domain skill names.

        Returns:
            Sorted list of skill directory names.
        """
        if not self._skills_dir.exists():
            return []
        return sorted(
            d.name for d in self._skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        )

    def search(self, query: str) -> list[tuple[str, str]]:
        """Search across all domain skill files.

        Args:
            query: Case-insensitive search term.

        Returns:
            List of (skill_name, matching_line) tuples.
        """
        query_lower = query.lower()
        results: list[tuple[str, str]] = []
        for skill_name in self.list_skills():
            content = self.load(skill_name)
            for line in content.splitlines():
                if query_lower in line.lower() and line.strip().startswith("-"):
                    results.append((skill_name, line.strip()))
        return results

    def correct(self, skill_name: str, old_text: str, new_text: str) -> bool:
        """Replace an entry in a specific skill file.

        When domain rules conflict, replace the old rule with the newer evidence.

        Args:
            skill_name: Domain skill identifier.
            old_text: Text to find and replace.
            new_text: Replacement text.

        Returns:
            `True` if replacement was made, `False` if `old_text` was not found.
        """
        skill_file = self.skill_path(skill_name)
        if not skill_file.exists():
            return False
        content = skill_file.read_text(encoding="utf-8")
        if old_text not in content:
            return False
        updated = content.replace(old_text, new_text, 1)
        skill_file.write_text(updated, encoding="utf-8")
        logger.debug("Corrected domain knowledge in %s", skill_file)
        return True

    def stats(self) -> dict[str, Any]:
        """Return statistics for the domain knowledge layer.

        Returns:
            Dict with skills_dir, skill_count, skills list, and total entries.
        """
        skills = self.list_skills()
        total_entries = sum(
            len([
                line for line in self.load(s).splitlines()
                if line.strip().startswith("-")
            ])
            for s in skills
        )
        return {
            "layer": "domain/knowledge",
            "skills_dir": str(self._skills_dir),
            "skill_count": len(skills),
            "skills": skills,
            "total_entries": total_entries,
        }


class MemoryManager:
    """Unified access point for all three memory layers.

    Provides a single interface to read, write, search, and correct
    entries across user/profile, project/context, and domain/knowledge layers.

    Storage structure::

        ~/.deepagents/agent/AGENTS.md          ← user/profile
        {cwd}/.deepagents/AGENTS.md            ← project/context
        ~/.deepagents/agent/skills/*/SKILL.md  ← domain/knowledge

    All files are automatically injected into the system prompt by the
    existing CLI infrastructure — no extra injection code needed.
    """

    def __init__(
        self,
        assistant_id: str = _AGENT_DIR,
        project_dir: Path | None = None,
    ) -> None:
        """Initialize all three memory layers.

        Args:
            assistant_id: Agent directory name under ~/.deepagents/.
            project_dir: Project root for the project/context layer.
                Defaults to the current working directory.
        """
        self.user = UserProfileMemory(assistant_id)
        self.project = ProjectContextMemory(project_dir)
        self.domain = DomainKnowledgeMemory(assistant_id)

    def search_all(self, query: str) -> dict[str, list[str]]:
        """Search across all three layers.

        Args:
            query: Case-insensitive search term.

        Returns:
            Dict with keys ``user``, ``project``, and ``domain`` containing
            matching entries from each layer.
        """
        domain_hits = self.domain.search(query)
        return {
            "user": self.user.search(query),
            "project": self.project.search(query),
            "domain": [f"[{skill}] {line}" for skill, line in domain_hits],
        }

    def all_stats(self) -> list[dict[str, Any]]:
        """Return statistics for all three layers.

        Returns:
            List of stat dicts from each layer.
        """
        return [
            self.user.stats(),
            self.project.stats(),
            self.domain.stats(),
        ]
