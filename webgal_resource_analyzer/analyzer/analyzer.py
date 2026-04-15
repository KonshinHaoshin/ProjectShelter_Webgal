"""Resource analyzer - compares resources against references."""

from typing import Set, Dict

from models.models import ResourceFile, ResourceReference, AnalysisResult, ResourceType
from analyzer.scanner import ResourceScanner
from analyzer.parser import ReferenceParser


class ResourceAnalyzer:
    """Analyzes resource usage by comparing files against references."""

    def __init__(self, game_path: str):
        self.game_path = game_path
        self.scanner = ResourceScanner(game_path)
        self.parser = ReferenceParser(game_path)

    def analyze(self) -> AnalysisResult:
        """Perform full analysis and return results."""
        # Scan resources
        resource_files = self.scanner.scan()

        # Parse references
        references = self.parser.parse()

        # Create result object
        result = AnalysisResult(
            game_path=self.game_path,
            resource_files=resource_files,
            references=references,
        )

        # Analyze usage
        self._analyze_usage(result)

        return result

    def _analyze_usage(self, result: AnalysisResult) -> None:
        """Analyze which resources are used vs unused."""
        # Build a mapping from filename to resource files (case-insensitive)
        filename_to_resources: Dict[str, Set[ResourceFile]] = {}
        for resource in result.resource_files:
            key = resource.name.lower()
            if key not in filename_to_resources:
                filename_to_resources[key] = set()
            filename_to_resources[key].add(resource)

        # Track which resources are referenced
        used_resource_keys: Set[str] = set()
        referenced_filenames: Set[str] = set()

        for ref in result.references:
            ref_key = ref.filename.lower()
            referenced_filenames.add(ref_key)

            if ref_key in filename_to_resources:
                used_resource_keys.add(ref_key)

        # Categorize resources
        for resource in result.resource_files:
            key = resource.name.lower()
            if key in used_resource_keys:
                result.used_resources.add(resource)
            else:
                result.unused_resources.add(resource)

        # Find references to missing files
        for ref in result.references:
            ref_key = ref.filename.lower()
            if ref_key not in filename_to_resources:
                result.referenced_but_missing.add(ref)

        # Update statistics
        result.total_resources = len(result.resource_files)
        result.used_count = len(result.used_resources)
        result.unused_count = len(result.unused_resources)
        result.missing_count = len(result.referenced_but_missing)

    def get_unused_by_type(self, result: AnalysisResult) -> Dict[ResourceType, Set[ResourceFile]]:
        """Get unused resources grouped by type."""
        by_type: Dict[ResourceType, Set[ResourceFile]] = {}
        for resource in result.unused_resources:
            if resource.resource_type not in by_type:
                by_type[resource.resource_type] = set()
            by_type[resource.resource_type].add(resource)
        return by_type
