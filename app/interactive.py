from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .sorter import iter_files


PALETTE = {
    "cyan": "36",
    "magenta": "35",
    "green": "32",
    "yellow": "33",
    "blue": "34",
}


ASCII_BANNER = r"""
    _________              __  .__  _____       
 /   _____/ ____________/  |_|__|/ ____\__.__.
 \_____  \ /  _ \_  __ \   __\  \   __<   |  |
 /        (  <_> )  | \/|  | |  ||  |  \___  |
/_______  /\____/|__|   |__| |__||__|  / ____|
        \/                             \/      
"""


def colorize(text: str, color: str | None = None, *, bold: bool = False) -> str:
    if not _supports_color():
        return text
    parts: list[str] = []
    if bold:
        parts.append("1")
    if color and color in PALETTE:
        parts.append(PALETTE[color])
    if not parts:
        return text
    prefix = f"\033[{';'.join(parts)}m"
    return f"{prefix}{text}\033[0m"


def _supports_color() -> bool:
    term = os.environ.get("TERM", "")
    return sys.stdout.isatty() and term not in {"dumb", ""}


def print_banner(default_root: Path) -> None:
    banner = colorize(ASCII_BANNER, "cyan", bold=True)
    tagline = colorize("Sortify :: Recursive extension-based sorter", "magenta", bold=True)
    default_line = colorize(f"Default root -> {default_root.resolve()}", "yellow")
    print("\n" + banner)
    print(tagline)
    print(default_line)
    print(colorize("-" * 60, "blue"))


def print_section(title: str) -> None:
    pad_title = f"[ {title} ]"
    width = 60
    print()
    print(colorize("=" * width, "blue"))
    print(colorize(pad_title.center(width), "green", bold=True))
    print(colorize("=" * width, "blue"))


def render_summary_table(summary: dict[str, int], total: int) -> str:
    header = "+-----------------+-------+--------+"
    lines = [header, "| Extension       | Count |   %    |", header]
    for ext, count in summary.items():
        pct = (count / total) * 100 if total else 0
        pretty_ext = (ext or "no_ext")[:15]
        lines.append(f"| {pretty_ext:<15} | {count:>5} | {pct:>5.1f}% |")
    lines.append(header)
    return "\n".join(lines)


def prompt_yes_no(prompt: str, default: bool | None = None) -> bool:
    suffix = " [y/n]" if default is None else (" [Y/n]" if default else " [y/N]")
    while True:
        response = input(f"{prompt}{suffix}: ").strip().lower()
        if not response and default is not None:
            return default
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        print("Please answer 'y' or 'n'.")


def prompt_path(prompt: str, default: Path) -> Path:
    raw_value = input(f"{prompt} [{default}]: ").strip()
    return Path(raw_value) if raw_value else default


def prompt_text(prompt: str, default: str) -> str:
    raw_value = input(f"{prompt} [{default}]: ").strip()
    return raw_value or default


def summarize_extensions(files: list[Path]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in files:
        ext = path.suffix.lower().lstrip(".") or "no_ext"
        counts[ext] = counts.get(ext, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def run_interactive(default_root: Path) -> argparse.Namespace:
    print_banner(default_root)

    print_section("Source & Destination")
    root = prompt_path("Start directory", default_root.resolve())
    dest_dir = prompt_text(
        "Destination folder ('.' keeps files beside their source root)",
        ".",
    )

    print_section("Filters")
    include_dotfiles = prompt_yes_no("Include hidden files (dotfiles)?", default=False)
    include_code = prompt_yes_no("Include code files (.py, .ipynb, etc.)?", default=False)

    print_section("Preview")
    dest_root_preview = (root / dest_dir).resolve()
    files = list(iter_files(root, dest_root_preview, include_dotfiles, include_code))
    total = len(files)
    print(colorize(f"Found {total} file(s) to process.", "yellow", bold=True))
    if total:
        summary = summarize_extensions(files)
        preview_slice = dict(list(summary.items())[:20])
        table = render_summary_table(preview_slice, total)
        print(table)
        if len(summary) > 20:
            remaining = len(summary) - 20
            print(colorize(f"...and {remaining} more extension group(s)", "magenta"))
    else:
        print(colorize("No files detected with the current filters.", "magenta"))

    print_section("Safety Checks")
    dry_run = prompt_yes_no("Do a dry run first (no changes)?", default=True)

    proceed = prompt_yes_no("Proceed with the operation?", default=bool(total))
    if not proceed:
        raise SystemExit(colorize("Cancelled by user.", "magenta", bold=True))

    return argparse.Namespace(
        root=root,
        dest_dir=dest_dir,
        dry_run=dry_run,
        include_dotfiles=include_dotfiles,
        include_code=include_code,
        interactive=True,
    )
