"""Reference parser - parses WebGAL scripts to find resource references."""

import re
from pathlib import Path
from typing import Set

from models.models import ResourceReference, ResourceType
from config.patterns import (
    BGM_PATTERN,
    BG_PATTERN,
    FIGURE_PATTERN,
    EFFECT_PATTERN,
    ANIMATION_PATTERN,
    VOCAL_PATTERN,
)


class ReferenceParser:
    """Parses WebGAL scripts to extract resource references."""

    # Pattern info: (compiled_pattern, command_name)
    PATTERNS = [
        (BGM_PATTERN, 'bgm:', ResourceType.BGM),
        (BG_PATTERN, 'changeBg:', ResourceType.BACKGROUND),
        (FIGURE_PATTERN, 'changeFigure:', ResourceType.FIGURE),
        (EFFECT_PATTERN, 'playEffect:', ResourceType.VOCAL),
        (ANIMATION_PATTERN, 'setAnimation:', ResourceType.ANIMATION),
        (VOCAL_PATTERN, 'vocal/语音:', ResourceType.VOCAL),
    ]

    def __init__(self, game_path: str):
        self.game_path = Path(game_path)
        # Resolve to the actual game directory (may have game/ subdirectory)
        self._script_base = self._find_game_dir(game_path)
        self._references: Set[ResourceReference] = set()
        self._compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), cmd, rtype)
            for pattern, cmd, rtype in self.PATTERNS
        ]

    def _find_game_dir(self, path: str) -> Path:
        """Find the actual game directory (with game/ subdir or direct)."""
        base = Path(path)
        # If path/game exists and contains scene subdir, use game/
        game_subdir = base / 'game'
        if game_subdir.is_dir() and (game_subdir / 'scene').exists():
            return game_subdir
        # Otherwise use the path directly
        return base

    def parse(self) -> Set[ResourceReference]:
        """Parse all script files in the game directory."""
        self._references.clear()

        if not self._script_base.exists():
            return self._references

        # Parse scene files (*.txt in scene/ or root)
        # Try both 'scene' and 'scenes' directory names
        for scene_dir_name in ['scene', 'scenes']:
            scene_dir = self._script_base / scene_dir_name
            if scene_dir.is_dir():
                self._parse_directory(scene_dir)

        # Also check root for config.txt
        config_file = self._script_base / 'config.txt'
        if config_file.is_file():
            self._parse_file(config_file)

        # Parse any txt files in game root
        for txt_file in self._script_base.glob('*.txt'):
            if txt_file.is_file() and txt_file.name != 'config.txt':
                self._parse_file(txt_file)

        return self._references

    def _parse_directory(self, directory: Path) -> None:
        """Parse all txt files in a directory."""
        try:
            for file_path in directory.rglob('*.txt'):
                self._parse_file(file_path)
        except PermissionError:
            pass

    def _parse_file(self, file_path: Path) -> None:
        """Parse a single script file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                self._parse_line(line, str(file_path), line_num)
        except (PermissionError, OSError):
            pass

    def _parse_line(self, line: str, source_file: str, line_num: int) -> None:
        """Parse a single line for resource references."""
        for compiled_pattern, command, ref_type in self._compiled_patterns:
            # Try to find all matches in the line
            for match in compiled_pattern.finditer(line):
                filename = match.group(1).strip()
                # Remove extension if present
                if filename:
                    filename = self._clean_filename(filename)

                    reference = ResourceReference(
                        filename=filename,
                        reference_type=ref_type,
                        source_file=source_file,
                        line_number=line_num,
                        command=command,
                    )
                    self._references.add(reference)

    def _clean_filename(self, filename: str) -> str:
        """Clean the extracted filename."""
        # Remove leading/trailing whitespace and common punctuation
        filename = filename.strip()
        filename = filename.rstrip(';,-')

        # Remove file extension if present
        if '.' in filename:
            filename = Path(filename).stem

        return filename

    @property
    def references(self) -> Set[ResourceReference]:
        """Get parsed references."""
        return self._references.copy()
