"""Data models for resource analysis."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Set


class ResourceType(Enum):
    """Resource type enumeration."""
    BACKGROUND = "background"
    BGM = "bgm"
    FIGURE = "figure"
    VOCAL = "vocal"
    ANIMATION = "animation"
    VIDEO = "video"
    TEXTURE = "tex"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ResourceFile:
    """Represents a resource file on disk."""
    path: str  # Relative path from game directory
    name: str  # Filename without extension
    extension: str
    resource_type: ResourceType

    @property
    def full_name(self) -> str:
        """Get full filename."""
        return f"{self.name}{self.extension}"


@dataclass(frozen=True)
class ResourceReference:
    """Represents a reference to a resource in code."""
    filename: str  # Referenced filename (without extension)
    reference_type: ResourceType
    source_file: str  # File containing the reference
    line_number: int = 0
    command: str = ""  # The command used (e.g., 'bgm:', 'changeBg:')


@dataclass
class AnalysisResult:
    """Result of resource analysis."""
    game_path: str
    resource_files: Set[ResourceFile] = field(default_factory=set)
    references: Set[ResourceReference] = field(default_factory=set)

    # Categorized results
    used_resources: Set[ResourceFile] = field(default_factory=set)
    unused_resources: Set[ResourceFile] = field(default_factory=set)
    referenced_but_missing: Set[ResourceReference] = field(default_factory=set)

    # Statistics
    total_resources: int = 0
    used_count: int = 0
    unused_count: int = 0
    missing_count: int = 0

    def summary(self) -> dict:
        """Get summary as dictionary."""
        return {
            "game_path": self.game_path,
            "total_resources": self.total_resources,
            "used_count": self.used_count,
            "unused_count": self.unused_count,
            "missing_count": self.missing_count,
        }