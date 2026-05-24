# garmin-gcd-toolkit

Open-source Python toolkit for parsing and extracting resources from Garmin
`.GCD` firmware container files. Developed through empirical reverse engineering
for interoperability purposes.

## Status

Work in progress. Currently in Phase 1 (project bootstrap).

## Usage

```bash
pip install -e .
gcd-tool inspect path/to/GUPDATE.GCD
gcd-tool list   path/to/GUPDATE.GCD
gcd-tool extract path/to/GUPDATE.GCD --output ./output
```

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
