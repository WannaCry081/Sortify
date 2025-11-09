# Sortify 🗂️

Sortify is a friendly command-line utility that sweeps through a directory tree and groups every file by extension into a tidy destination folder. It is perfect for taming messy project roots or backup drives without losing track of what moved where.

## Highlights ✨
- **Guided interactive mode** with ANSI colors, ASCII art, and section dividers that feel like a classic Linux tool.
- **Safety-first sorting**: dry-run previews, hidden-file toggles, and automatic protection for the root `README.md` so your docs stay put.
- **Smart grouping**: extensions are summarized with counts and percentages before you commit.
- **Code-aware filters** keep Python notebooks, scripts, and other source files in place unless you explicitly include them.

## Quick Start 🚀
```bash
python -m venv .venv && source .venv/bin/activate  # optional but recommended
pip install -r requirements.txt  # if you have dependencies
python main.py --help
```

To jump straight into the guided wizard:
```bash
python main.py --interactive
```

## Interactive Walkthrough 📟
When you launch interactive mode, Sortify greets you with a neon banner, then walks you through four stages:
1. **Source & Destination** – confirm the root path and pick a destination folder name.
2. **Filters** – decide whether to include dotfiles or code files.
3. **Preview** – see how many files will move plus a neat table of the top extensions (with percentages) so there are no surprises.
4. **Safety Checks** – choose a dry run and confirm before anything is touched.

All prompts adapt to your answers, and the summary table mirrors what you would expect from an ncurses-style Linux utility.

## Usage Examples 🧭
```bash
# Preview moves without touching anything
python main.py --dry-run

# Point to another directory and create a custom destination folder
python main.py /Volumes/ExternalDrive --dest-dir sorted_archive

# Include hidden files but keep code untouched
python main.py --include-dotfiles
```

## Safeguards 🛡️
- The destination folder is skipped while walking the tree to avoid self moves.
- The repository's root `README.md` is never moved, ensuring GitHub renders your documentation after every run.
- Dry runs and interactive confirmations help you verify before committing changes.

## Contributing 🤝
Issues and pull requests are welcome! If you spot a case where the sorter could be smarter—or have ideas for new interactive flourishes—open a ticket and let's collaborate.

Enjoy keeping your workspace spotless!
