# Repository Guidelines

## Project Structure & Module Organization

This repository is a curated research note collection, not a code package. Paper notes live under `paper/`, with area folders such as `paper/MLLM/`, `paper/VLA/`, `paper/Agents/`, `paper/RL/`, `paper/NLP/`, and `paper/AI4S/`. Most paper entries live in their own folder, for example `paper/MLLM/RAG/`, with:

- `README.md` for the paper note.
- `paper.pdf` for the source paper.
- `figures/` for extracted figures and tables, named simply such as `fig1.png` or `table1.png`.

The root `README.md` is the index and reading list. Update it whenever adding, renaming, or moving a paper note.

## Build, Test, and Development Commands

There is no build or package manager workflow. Use repository checks instead:

- `rg --files` lists tracked note, PDF, and figure paths quickly.
- `git status --short` reviews changed files before committing.
- `Get-ChildItem -Path paper -Recurse -Filter README.md` checks note coverage on Windows PowerShell.

Preview Markdown locally before committing, especially notes with tables, formulas, images, or mixed Chinese/English text.

## Writing Style & Naming Conventions

Use Markdown headings with a consistent paper-note structure: `Paper Info`, `Abstract`, `Motivation`, `Method`, `Key Insights`, and `Limitations & Future Work` when applicable. Keep prose analytical and specific; prefer concise summaries plus personal interpretation over copying long passages from papers.

Name paper folders by the common paper or method name, such as `CLIP`, `DQN`, `ReAct`, or `LinearDesign`. Store the main paper as `paper.pdf`. Use note-local relative paths such as `./paper.pdf` and `./figures/fig1.png`. Save Markdown as UTF-8.

## Testing Guidelines

No automated test framework is configured. Manual validation should include:

- Confirm all relative links and image paths resolve.
- Ensure each new note has its `paper.pdf` or clearly documented external paper link.
- Check tables render correctly in Markdown preview.
- Verify the root reading list points to the new note path.

## Commit & Pull Request Guidelines

Recent history uses short lowercase messages such as `update`. Keep commits concise, but make them more traceable when possible, for example `MLLM: add CLIP figures` or `AI4S: update CodonFM note`.

Pull requests should summarize added or changed papers, list moved/renamed paths, and mention large PDFs or figure batches. Include screenshots only when a Markdown rendering issue or figure layout change needs review.

## Agent-Specific Instructions

Keep edits scoped to documentation and assets requested by the task. Do not rewrite existing notes for style alone. Avoid committing temporary exports, OCR scratch files, or private research data.
