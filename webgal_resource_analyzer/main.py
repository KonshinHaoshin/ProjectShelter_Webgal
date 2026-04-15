#!/usr/bin/env python3
"""WebGAL Resource Analyzer - CLI entry point."""

import argparse
import sys
from pathlib import Path

from analyzer import ResourceAnalyzer, Reporter


def main():
    parser = argparse.ArgumentParser(
        description="WebGAL Resource Analyzer - Find unused resources in WebGAL projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py games/MJKNMZ
  python main.py games/MJKNMZ -v
  python main.py games/MJKNMZ -f json -o report.json
  python main.py games/MJKNMZ -f text -o report.txt
        """
    )

    parser.add_argument(
        'game_path',
        help="Path to the WebGAL game directory"
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose output"
    )

    parser.add_argument(
        '-f', '--format',
        choices=['json', 'text'],
        help="Output format (json or text)"
    )

    parser.add_argument(
        '-o', '--output',
        help="Output file path (requires -f/--format)"
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help="Disable colored output"
    )

    args = parser.parse_args()

    # Validate game path
    game_path = Path(args.game_path)
    if not game_path.exists():
        print(f"Error: Game path does not exist: {game_path}", file=sys.stderr)
        sys.exit(1)

    if not game_path.is_dir():
        print(f"Error: Game path is not a directory: {game_path}", file=sys.stderr)
        sys.exit(1)

    # Run analysis
    print(f"Analyzing: {game_path}")
    analyzer = ResourceAnalyzer(str(game_path))
    result = analyzer.analyze()

    # Create reporter
    use_color = not args.no_color and sys.stdout.isatty()
    reporter = Reporter(use_color=use_color)

    # Output report
    if args.format == 'json' and args.output:
        reporter.save_json_report(result, args.output)
    elif args.format == 'text' and args.output:
        reporter.save_text_report(result, args.output)
    else:
        reporter.print_report(result)

    # Exit with appropriate code
    if result.unused_count > 0:
        sys.exit(0)  # Analysis complete, resources found unused
    else:
        sys.exit(0)  # All resources used


if __name__ == '__main__':
    main()
