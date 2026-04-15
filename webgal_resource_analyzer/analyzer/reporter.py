"""Reporter - generates analysis reports in various formats."""

import json
from pathlib import Path
from typing import Optional

from models.models import AnalysisResult, ResourceType


class Reporter:
    """Generates reports from analysis results."""

    # ANSI color codes
    COLOR_RESET = "\033[0m"
    COLOR_RED = "\033[91m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_BLUE = "\033[94m"
    COLOR_CYAN = "\033[96m"
    COLOR_BOLD = "\033[1m"

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def print_report(self, result: AnalysisResult) -> None:
        """Print a formatted report to console."""
        self._print_header(result)
        self._print_summary(result)
        self._print_unused_resources(result)
        self._print_missing_references(result)

    def _print_header(self, result: AnalysisResult) -> None:
        """Print report header."""
        print(f"\n{self._bold('='*60)}")
        print(f"{self._bold('WebGAL Resource Analyzer')}")
        print(f"{self._bold('='*60)}")
        print(f"Game: {result.game_path}")

    def _print_summary(self, result: AnalysisResult) -> None:
        """Print summary statistics."""
        print(f"\n{self._bold('Summary')}")
        print(f"  Total resources:   {result.total_resources}")
        print(f"  {self._green('Used resources:')}     {result.used_count}")
        print(f"  {self._red('Unused resources:')}   {result.unused_count}")
        print(f"  {self._yellow('Missing references:')} {result.missing_count}")

        if result.unused_count > 0:
            percentage = (result.unused_count / result.total_resources * 100) if result.total_resources > 0 else 0
            print(f"\n  {self._red('Warning:')} {percentage:.1f}% of resources are unused!")

    def _print_unused_resources(self, result: AnalysisResult) -> None:
        """Print unused resources grouped by type."""
        if not result.unused_resources:
            print(f"\n{self._green('No unused resources found!')}")
            return

        print(f"\n{self._bold('Unused Resources (by type)')}")

        # Group by type
        by_type: dict = {}
        for resource in result.unused_resources:
            rtype = resource.resource_type.value
            if rtype not in by_type:
                by_type[rtype] = []
            by_type[rtype].append(resource)

        for rtype, resources in sorted(by_type.items()):
            print(f"\n  {self._cyan(f'[{rtype.upper()}]')} ({len(resources)} files)")
            for res in sorted(resources, key=lambda x: x.name):
                print(f"    - {res.path}")

    def _print_missing_references(self, result: AnalysisResult) -> None:
        """Print references to missing files."""
        if not result.referenced_but_missing:
            return

        print(f"\n{self._bold('Referenced but Missing Files')}")
        for ref in sorted(result.referenced_but_missing, key=lambda x: x.source_file):
            print(f"  {self._yellow(ref.filename)}")
            print(f"    Source: {ref.source_file}:{ref.line_number}")
            print(f"    Command: {ref.command}")

    def save_json_report(self, result: AnalysisResult, output_path: str) -> None:
        """Save report as JSON file."""
        report = self._build_json_report(result)
        Path(output_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"\nJSON report saved to: {output_path}")

    def save_text_report(self, result: AnalysisResult, output_path: str) -> None:
        """Save report as text file."""
        lines = self._build_text_report_lines(result)
        Path(output_path).write_text('\n'.join(lines), encoding='utf-8')
        print(f"Text report saved to: {output_path}")

    def _build_json_report(self, result: AnalysisResult) -> dict:
        """Build JSON report structure."""
        return {
            "game_path": result.game_path,
            "summary": result.summary(),
            "unused_resources": [
                {"path": r.path, "name": r.name, "type": r.resource_type.value}
                for r in sorted(result.unused_resources, key=lambda x: (x.resource_type.value, x.name))
            ],
            "missing_references": [
                {
                    "filename": ref.filename,
                    "source": ref.source_file,
                    "line": ref.line_number,
                    "command": ref.command,
                }
                for ref in sorted(result.referenced_but_missing, key=lambda x: x.source_file)
            ],
        }

    def _build_text_report_lines(self, result: AnalysisResult) -> list:
        """Build text report lines."""
        lines = [
            "WebGAL Resource Analysis Report",
            "=" * 50,
            f"Game: {result.game_path}",
            "",
            "Summary",
            "-" * 30,
            f"Total resources: {result.total_resources}",
            f"Used: {result.used_count}",
            f"Unused: {result.unused_count}",
            f"Missing references: {result.missing_count}",
            "",
        ]

        if result.unused_resources:
            lines.append("Unused Resources")
            lines.append("-" * 30)
            for resource in sorted(result.unused_resources, key=lambda x: (x.resource_type.value, x.name)):
                lines.append(f"  [{resource.resource_type.value}] {resource.path}")

        if result.referenced_but_missing:
            lines.append("")
            lines.append("Missing References")
            lines.append("-" * 30)
            for ref in sorted(result.referenced_but_missing, key=lambda x: x.source_file):
                lines.append(f"  {ref.filename} (from {ref.source_file}:{ref.line_number})")

        return lines

    def _color(self, text: str, color: str) -> str:
        """Apply color if enabled."""
        if not self.use_color:
            return text
        return f"{color}{text}{self.COLOR_RESET}"

    def _bold(self, text: str) -> str:
        return self._color(text, self.COLOR_BOLD)

    def _red(self, text: str) -> str:
        return self._color(text, self.COLOR_RED)

    def _green(self, text: str) -> str:
        return self._color(text, self.COLOR_GREEN)

    def _yellow(self, text: str) -> str:
        return self._color(text, self.COLOR_YELLOW)

    def _blue(self, text: str) -> str:
        return self._color(text, self.COLOR_BLUE)

    def _cyan(self, text: str) -> str:
        return self._color(text, self.COLOR_CYAN)
