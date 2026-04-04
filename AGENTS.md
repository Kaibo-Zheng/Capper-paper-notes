# Repository Guidelines

## Project Structure & Module Organization
This repository is currently a lightweight research-notes project:

- `README.md`: project overview, note template, and reading-list sections.
- `mRNABert.pdf`: reference paper asset.
- `LICENSE`: MIT license text.

Keep new content organized by topic and paper. Prefer adding note files under a clear path such as `notes/<topic>/<paper-slug>.md` (for example, `notes/vlm/clip.md`) rather than placing many files at the root.

## Build, Test, and Development Commands
There is no build system or automated test pipeline yet. Use lightweight repo checks:

- `git status -sb`: quick view of changed files.
- `rg --files`: list repository files.
- `rg -n "TODO|FIXME" README.md`: find unfinished sections.
- `git log --oneline -n 10`: review recent history before committing.

If tooling is added later, document new commands in `README.md` and this file in the same PR.

## Coding Style & Naming Conventions
Use Markdown-first conventions:

- Write concise, scannable sections with `#`/`##` headings.
- Use fenced code blocks for commands and examples.
- Prefer descriptive lowercase file names with hyphens (for example, `vision-transformer-notes.md`).
- Keep line wrapping readable and avoid mixing languages in a single bullet unless needed for clarity.

## Testing Guidelines
No formal test framework is configured. Treat quality checks as manual review:

- Verify Markdown renders correctly (headings, tables, links).
- Confirm new references are accurate and non-duplicate.
- Re-open changed files to catch encoding issues before commit.

## Commit & Pull Request Guidelines
Current history uses short messages (`init`, `Initial commit`), but new contributions should be clearer:

- Use imperative commit subjects, optionally scoped (for example, `docs: add VLA paper summary`).
- Keep one logical change per commit.
- PRs should include: purpose, files changed, and any follow-up TODOs.
- Link related issues/discussions when applicable, and include screenshots only when rendering/layout changes matter.

## Security & Content Notes
Only commit papers or assets you are allowed to redistribute. For copyrighted material, prefer linking in notes instead of uploading binaries.
