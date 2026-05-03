# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Nature

This is a **research notes repository**, not a software project. There is no build, lint, test, or package manager workflow. All work is documentation: Markdown notes, PDFs, and figure images. Treat tasks as editorial/curatorial unless told otherwise.

`AGENTS.md` already documents conventions for contributors and agents — read it before non-trivial edits. The points below are the non-obvious things to keep in mind on top of `AGENTS.md`.

## Layout Invariant

Every paper note is a folder under `paper/`, grouped by topic directory (`paper/MLLM/`, `paper/VLA/`, `paper/Agents/`, `paper/RL/`, `paper/NLP/`, `paper/AI4S/<subarea>/`) and contains:

- `README.md` — the note itself
- `paper.pdf` — the source paper
- `figures/` — extracted figures named `fig1.png`, `table1.png`, etc.

Note bodies follow a fixed section order: `Paper Info`, `Abstract`, `Motivation`, `Method`, `Key Insights`, `Limitations & Future Work`. Match this when adding or editing notes; don't introduce new top-level structures unilaterally.

## The Root README Is an Index — Keep It in Sync

`README.md` at the repo root is the canonical reading list. Whenever a paper folder is added, renamed, or moved, update the corresponding table row in the appropriate "Reading List" subsection. The `paper/AI4S/NucleicAcid/` table is ordered roughly chronologically (earlier work first) — preserve that ordering when inserting.

`paper/AI4S/` has its own subarea index pages (e.g. `paper/AI4S/NucleicAcid/README.md` documents shared mRNA metrics) — check whether a sibling index also needs updating.

## Working with Notes

- Prose is bilingual (Chinese + English). Save Markdown as UTF-8 and don't "normalize" mixed-language text.
- Use note-local relative paths such as `./paper.pdf` and `./figures/fig1.png`. Don't hardcode absolute paths.
- Don't rewrite existing notes for style alone — scope edits to what the task asks for.
- Don't commit OCR scratch, temporary exports, or private research data.

## Shell Note

The repo lives on Windows, but Claude Code uses bash here — use Unix syntax (`/dev/null`, forward slashes) in commands, not PowerShell. The `Get-ChildItem` example in `AGENTS.md` is for human contributors on PowerShell, not for use from this session.
