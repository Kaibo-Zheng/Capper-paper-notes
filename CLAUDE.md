# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A personal collection of research paper reading notes organized by topic. No build system, no test suite, no application code. Content is Markdown + PDFs + figures.

## Repository Layout

```
MLLM/         Multimodal Large Language Models (e.g., CLIP, DensingLaw)
VLA/          Vision-Language-Action / Embodied AI (e.g., pi0.6)
AI4S/         AI for Science (e.g., mRNABert, GEMORNA, UTR-LM, DNA-Diffusion)
NLP/          Natural Language Processing (e.g., Seq2Seq)
```

Each paper lives in `<Topic>/<PaperName>/` containing:
- `README.md` -- the reading notes
- `paper.pdf` -- the paper PDF
- Optional figures (`fig1.png`, etc.) referenced from the notes

## Note Format

Every paper note follows this structure:
1. **Paper Info** -- title, authors, venue, links
2. **Motivation** -- what problem the paper solves
3. **Method** -- core approach (often with subsections for architecture, training, etc.)
4. **Key Insights** -- personal analysis of results, with inline figures where available
5. **Limitations & Future Work** -- weaknesses and extensions

Notes are written in Chinese with English technical terms preserved inline. Keep this style when writing or editing notes.

## Conventions

- Paper PDFs are always named `paper.pdf` inside their folder.
- The root `README.md` has a reading list table per category -- update it when adding a new paper.
- Commit messages should use imperative form, optionally scoped: `docs: add VLA paper summary`.
- Only commit papers/assets you are allowed to redistribute; prefer linking over uploading copyrighted material.

## Useful Commands

```bash
git status -sb                    # quick view of changed files
git log --oneline -n 10           # recent history
rg -n "TODO|FIXME" README.md     # find unfinished sections
```
