# garmin-gcd-toolkit

**Parse, inspect, and extract resources from Garmin `.GCD` firmware container files — with the format documented in the open.**

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Status](https://img.shields.io/badge/status-active_reverse_engineering-orange)

Garmin ships firmware updates as `.GCD` container files. The format is undocumented. This project reverse-engineers it empirically — every claim validated against real hex bytes — and ships both:

- 📖 **[docs/FORMAT.md](docs/FORMAT.md)** — the `.GCD` format specification as we currently understand it: header layout, record structure, confirmed record types, and what's still unknown. Original work from byte-level observation; useful even if you never run the code.
- 🛠 **`gcd-tool`** — a Python CLI to inspect headers, walk records, extract embedded resources (PNG, gzip…), and analyze payloads (entropy, ARM Thumb detection, container classification).

## Quick start

```bash
git clone https://github.com/theodorebeaupre-prog/garmin-gcd-toolkit
cd garmin-gcd-toolkit
pip install -e .

gcd-tool inspect  GUPDATE.GCD                    # validate magic, show header
gcd-tool list     GUPDATE.GCD                    # walk and list all records
gcd-tool extract  GUPDATE.GCD --output ./out     # extract embedded resources
gcd-tool analyze  GUPDATE.GCD                    # entropy + payload classification
```

You supply your own legally obtained `.GCD` file (e.g. downloaded through Garmin Express for a device you own). **No firmware is distributed with this repository.**

## What works today

| Capability | Status |
|---|---|
| GCD magic + 4 KB header validation | ✅ Confirmed |
| Record walker (9-byte record headers, marker `01 00 01 00`) | ✅ Confirmed |
| Record types `0xDC`, `0x4C`, `0x64`, `0x67` mapped | ✅ Confirmed |
| Resource extraction (PNG with IEND validation, gzip) | ✅ Working |
| Payload analyzer — entropy, ARM Thumb heuristics | ✅ Working |
| Length encoding for types `0xDC`/`0x64` | 🔬 Under investigation |

Test suite: `pytest` (header parsing, record walking, extraction, analyzer).

## How it was reverse-engineered

Every hypothesis was validated against actual hex bytes before any code was written, under one strict rule:

> "Never guess field meanings. Show the hex bytes first.
> Propose a hypothesis. Test it. Only then write code."

The work was done with a multi-AI workflow — [Claude](https://claude.ai) for binary analysis and hypothesis formation, [Claude Code](https://claude.ai/code) for project architecture and guardrails, [Codex CLI](https://openai.com) and [Mistral Vibe](https://mistral.ai) as phase implementers. The discipline above was what kept the models from confidently hallucinating wrong binary structures — the findings in [FORMAT.md](docs/FORMAT.md) cite the evidence bytes for each claim.

## Contributing

The most valuable contributions are **new observations**:

- Run `gcd-tool list` / `analyze` on `.GCD` files from other devices and report record types we haven't mapped.
- Help crack the length encoding for record types `0xDC` and `0x64`.
- Add extractors for more embedded formats.

Open an issue with the hex evidence (never attach firmware files) and let's compare notes.

## Legal notice

**This project is independent and is not affiliated with, endorsed by, or connected to Garmin Ltd. or any of its subsidiaries.**

The format documentation in this repository is original work produced through empirical observation of binary data. No Garmin source code, internal specifications, or confidential materials were used or accessed. Reverse engineering for interoperability is permitted under the **Canadian Copyright Act §30.61**, **EU Directive 2009/24/EC Art. 6**, and **17 U.S.C. §107** (*Sega v. Accolade*).

No firmware files are distributed here; the `samples/` directory is gitignored. Software is provided "AS IS" without warranty. Modifying device firmware may void your warranty or damage your device.
