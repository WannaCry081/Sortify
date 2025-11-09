from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .interactive import run_interactive
from .sorter import SortConfig, sort_files


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively group files by extension into a top-level folder.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=Path.cwd(),
        type=Path,
        help="Directory to start from (defaults to current directory)",
    )
    parser.add_argument(
        "--dest-dir",
        default="sorted_by_extension",
        help="Name of the destination folder that will be created inside the root",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned moves without changing anything",
    )
    parser.add_argument(
        "--include-dotfiles",
        action="store_true",
        help="Include hidden files (starting with a dot)",
    )
    parser.add_argument(
        "--include-code",
        action="store_true",
        help="Include common code files like .py, .ipynb (skipped by default to avoid moving this script)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode with guided prompts",
    )
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> SortConfig:
    root = args.root if isinstance(args.root, Path) else Path(args.root)
    return SortConfig(
        root=root,
        dest_dir=args.dest_dir,
        include_dotfiles=args.include_dotfiles,
        include_code=args.include_code,
        dry_run=args.dry_run,
        interactive=getattr(args, "interactive", False),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if getattr(args, "interactive", False):
        try:
            args = run_interactive(args.root if isinstance(args.root, Path) else Path(args.root))
        except KeyboardInterrupt:
            raise SystemExit("\nInterrupted.")

    config = build_config(args)
    sort_files(config)
    return 0
