from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_CODE_EXTENSIONS = {
    # Python and notebooks
    ".py", ".ipynb", ".pyc", ".pyo",
    # Web development
    ".html", ".css", ".js", ".jsx", ".ts", ".tsx",
    # Java, C-family
    ".java", ".c", ".cpp", ".h", ".hpp", ".cs",
    # Scripting
    ".sh", ".bash", ".ps1", ".bat",
    # Data and config for code projects
    ".json", ".yaml", ".yml", ".xml",
    # Other major languages
    ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".kts",
}


def is_relative_to_path(candidate: Path, other: Path) -> bool:
    try:
        candidate.relative_to(other)
        return True
    except ValueError:
        return False


@dataclass(frozen=True)
class SortConfig:
    """Container for sorter runtime options."""

    root: Path
    dest_dir: Path | str = Path(".")
    include_dotfiles: bool = False
    include_code: bool = False
    dry_run: bool = False
    interactive: bool = False

    @property
    def root_path(self) -> Path:
        return self.root.resolve()

    @property
    def destination_root(self) -> Path:
        dest_path = Path(self.dest_dir)
        if dest_path.is_absolute():
            return dest_path.resolve()
        return (self.root_path / dest_path).resolve()


def iter_files(
    root: Path,
    dest_root: Path,
    include_dotfiles: bool,
    include_code: bool,
    code_extensions: set[str] | None = None,
) -> Iterable[Path]:
    """Yield file paths under root while skipping the destination tree and optional filters."""
    root = root.resolve()
    dest_root = dest_root.resolve()
    code_extensions = code_extensions or DEFAULT_CODE_EXTENSIONS

    dest_is_root = dest_root == root

    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)

        # Remove the destination directory from traversal to avoid recursion when needed.
        if not dest_is_root:
            dirnames[:] = [
                d
                for d in dirnames
                if not is_relative_to_path((current_dir / d).resolve(), dest_root)
                and (current_dir / d).resolve() != dest_root
            ]

        for name in filenames:
            path = current_dir / name
            if not include_dotfiles and path.name.startswith("."):
                continue
            if not include_code and path.suffix.lower() in code_extensions:
                continue
            if path.parent.resolve() == root and path.name.lower() == "readme.md":
                # Preserve the root README for repo documentation.
                continue
            if not dest_is_root and is_relative_to_path(path.resolve(), dest_root):
                continue
            if dest_is_root:
                ext = path.suffix.lower().lstrip(".") or "no_ext"
                if path.parent.resolve() == (dest_root / ext).resolve():
                    # Already resting inside its extension bucket.
                    continue
            if path.is_file():
                yield path


def safe_destination(dest_dir: Path, filename: str) -> Path:
    """Return a non-colliding destination path by appending (n) if needed."""
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1
    while True:
        bumped = dest_dir / f"{stem} ({counter}){suffix}"
        if not bumped.exists():
            return bumped
        counter += 1


def move_file(src: Path, dest_root: Path, dry_run: bool = False) -> Path:
    ext = src.suffix.lower().lstrip(".") or "no_ext"
    dest_dir = dest_root / ext
    dest_dir.mkdir(parents=True, exist_ok=True)

    if src.parent.resolve() == dest_dir.resolve():
        print(f"Skipping (already grouped): {src}")
        return src

    dest = safe_destination(dest_dir, src.name)
    if dry_run:
        print(f"DRY-RUN: {src} -> {dest}")
        return dest

    print(f"Moving: {src} -> {dest}")
    shutil.move(str(src), str(dest))
    return dest


def sort_files(config: SortConfig) -> list[Path]:
    """Core sorting routine shared by the CLI and any programmatic callers."""
    root = config.root_path
    dest_root = config.destination_root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory does not exist or is not a directory: {root}")

    dest_root.mkdir(parents=True, exist_ok=True)
    files = list(iter_files(root, dest_root, config.include_dotfiles, config.include_code))

    if not files:
        print("No files to process with the current filters.")
        return []

    if not config.dry_run and not config.interactive:
        print(
            f"About to move {len(files)} file(s). "
            "Use --dry-run to preview without changes, or --interactive for guided setup."
        )

    for path in files:
        move_file(path, dest_root, dry_run=config.dry_run)

    print("\nDone." + (" (dry-run)" if config.dry_run else ""))
    print(f"Destination: {dest_root}")
    return files
