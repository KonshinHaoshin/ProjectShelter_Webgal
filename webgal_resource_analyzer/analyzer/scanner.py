"""Resource file scanner - finds all resource files in game directory."""

import os
from pathlib import Path
from typing import Set, Optional

from models.models import ResourceFile, ResourceType
from config.patterns import (
    IMAGE_EXTENSIONS,
    AUDIO_EXTENSIONS,
    VIDEO_EXTENSIONS,
    ANIMATION_EXTENSIONS,
)


class ResourceScanner:
    """Scans game directory for resource files."""

    # Map directories to resource types
    DIRECTORY_TYPE_MAP = {
        'background': ResourceType.BACKGROUND,
        'bgm': ResourceType.BGM,
        'figure': ResourceType.FIGURE,
        'vocal': ResourceType.VOCAL,
        'animation': ResourceType.ANIMATION,
        'video': ResourceType.VIDEO,
        'tex': ResourceType.TEXTURE,
    }

    def __init__(self, game_path: str):
        self.game_path = Path(game_path)
        # Resolve to the actual game directory (may have game/ subdirectory)
        self._resource_base = self._find_game_dir(game_path)
        self._resource_files: Set[ResourceFile] = set()

    def _find_game_dir(self, path: str) -> Path:
        """Find the actual game directory (with game/ subdir or direct)."""
        base = Path(path)
        # If path/game exists and contains typical game subdirs, use game/
        game_subdir = base / 'game'
        if game_subdir.is_dir() and (game_subdir / 'scene').exists():
            return game_subdir
        # Otherwise use the path directly
        return base

    def scan(self) -> Set[ResourceFile]:
        """Scan the game directory for all resource files."""
        self._resource_files.clear()

        if not self._resource_base.exists():
            return self._resource_files

        # Scan each known subdirectory
        for subdir, resource_type in self.DIRECTORY_TYPE_MAP.items():
            dir_path = self._resource_base / subdir
            if dir_path.is_dir():
                self._scan_directory(dir_path, resource_type)

        # Also scan root game directory for any misplaced resources
        self._scan_directory(self._resource_base, ResourceType.UNKNOWN)

        return self._resource_files

    def _scan_directory(self, directory: Path, default_type: ResourceType) -> None:
        """Scan a single directory for resource files."""
        try:
            for entry in directory.iterdir():
                if entry.is_file():
                    resource_type = self._determine_resource_type(entry, default_type)
                    if resource_type != ResourceType.UNKNOWN:
                        rel_path = entry.relative_to(self._resource_base)
                        resource_file = ResourceFile(
                            path=str(rel_path),
                            name=entry.stem,
                            extension=entry.suffix.lower(),
                            resource_type=resource_type,
                        )
                        self._resource_files.add(resource_file)
        except PermissionError:
            pass

    def _determine_resource_type(self, file_path: Path, default_type: ResourceType) -> ResourceType:
        """Determine the resource type based on extension and path."""
        ext = file_path.suffix.lower()

        if ext in IMAGE_EXTENSIONS:
            # Check if it's in a known directory
            parts = file_path.parts
            if 'background' in parts:
                return ResourceType.BACKGROUND
            elif 'figure' in parts:
                return ResourceType.FIGURE
            elif 'tex' in parts:
                return ResourceType.TEXTURE
            return default_type

        elif ext in AUDIO_EXTENSIONS:
            if 'bgm' in file_path.parts:
                return ResourceType.BGM
            return ResourceType.VOCAL

        elif ext in VIDEO_EXTENSIONS:
            return ResourceType.VIDEO

        elif ext in ANIMATION_EXTENSIONS:
            return ResourceType.ANIMATION

        return ResourceType.UNKNOWN

    @property
    def resource_files(self) -> Set[ResourceFile]:
        """Get scanned resource files."""
        return self._resource_files.copy()
