# garmin-gcd-toolkit

Open-source Python toolkit for parsing and extracting resources from Garmin
`.GCD` firmware container files. Developed through empirical reverse engineering
for interoperability purposes.

## Status

Phase 2 complete: record structure confirmed and walker implemented.

## Features

- GCD magic validation
- Record walking via `gcd-tool list`
- 19 records mapped in `GUPDATE.GCD`
- 8 tests passing

## Usage

```bash
pip install -e .
gcd-tool inspect path/to/GUPDATE.GCD
gcd-tool list   path/to/GUPDATE.GCD
gcd-tool extract path/to/GUPDATE.GCD --output ./output
```

## AI Workflow

This project was built using a multi-AI development workflow:

| Tool | Role |
|------|------|
| **[Claude](https://claude.ai)** | Research partner — binary analysis, hypothesis formation, hex dump interpretation, legal review |
| **[Claude Code](https://claude.ai/code)** | Project architect — bootstrap, safety guardrails, git workflow, pytest structure |
| **[Codex CLI](https://openai.com)** | Phase 2-3 implementer — binary walker, record parser, resource extractor |
| **[Mistral Vibe](https://mistral.ai)** | Phase 3-4 implementer — extractor.py, analyzer.py, CLI integration |

### Methodology

Every hypothesis was validated against actual hex bytes before
any code was written. Each AI was explicitly instructed:

> "Never guess field meanings. Show the hex bytes first.
> Propose a hypothesis. Test it. Only then write code."

This discipline was critical — without it, the models would
have confidently hallucinated wrong binary structures.

## Legal Notice

**This project is independent and is not affiliated with, endorsed by, or
connected to Garmin Ltd. or any of its subsidiaries.**

The `.GCD` format documentation contained in this repository (`docs/FORMAT.md`)
is original work produced through empirical observation of binary data. No
Garmin source code, internal specifications, or confidential materials were
used or accessed.

Reverse engineering for the purpose of achieving interoperability with
independently created software is permitted under:
- **Canadian Copyright Act, §30.61** (interoperability exception)
- **EU Directive 2009/24/EC, Article 6** (decompilation for interoperability)
- **17 U.S.C. §107** (fair use) and *Sega v. Accolade* precedent

**No firmware files are distributed with this repository.** You must supply
your own legally obtained `.GCD` file. The `samples/` directory is gitignored.

Software is provided "AS IS" without warranty of any kind. Use at your own
risk. Modifying device firmware may void your warranty or damage your device.
