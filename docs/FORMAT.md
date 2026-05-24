# Garmin .GCD Format — Reverse Engineering Notes

> **Status:** Phase 2 observations — confirmed from empirical byte analysis on:
> - `samples/GUPDATE.GCD` (50,201,232 bytes)
> - `samples/remotesw_090100.GCD` (36,972 bytes)
>
> Device context: nüvi 2455 (PN 006-B1371-00), Firmware 8.30

## Overall structure

| Region       | Offset range      | Size   | Status    |
|--------------|-------------------|--------|-----------|
| File header  | 0x0000-0x0FFF     | 4 KB   | Confirmed |
| Records      | 0x1000-EOF        | varies | Confirmed |

The file header is zero-padded to a 4 KB boundary.
Record parsing begins at 0x1000.

## File header (0x0000-0x0FFF)

0x0000  47 41 52 4d 49 4e 64 00   Magic: "GARMINd\0"
0x0008  01 00 01 00 dc 02 00 15   Record marker + type 0xDC
0x006E  01 00 01 00 4c 02 00 89   Record marker + type 0x4C
0x1000  start of records

## Confirmed record header (9 bytes)

| Offset | Size | Name    | Meaning                                      |
|--------|------|---------|----------------------------------------------|
| +0     | 4    | Marker  | Constant 01 00 01 00                         |
| +4     | 1    | Type    | Record type identifier                       |
| +5     | 2    | FieldA  | Unknown — subtype or flags                   |
| +7     | 2    | FieldB  | LE uint16 length for types 0x4C and 0x67;    |
|        |      |         | UNKNOWN encoding for types 0xDC and 0x64     |
| +9     | N    | Payload | N bytes of record payload                    |

## Confirmed record types

### 0xDC — header record 1
Offset 0x0008 in both files.
Evidence: 01 00 01 00 dc 02 00 15 00 00 00 00 00 00 00 00
FieldA=0x0002, FieldB=0x0015
Payload: 0x0011-0x006D (93 bytes, all zeros in remotesw)
Length encoding: UNKNOWN

### 0x4C — header record 2
Offset 0x006E in both files.
Evidence: 01 00 01 00 4c 02 00 89 0f 00 00 00 00 00 00 00
FieldA=0x0002, FieldB=0x0F89=3977
Formula CONFIRMED: next = offset + 9 + FieldB = 0x1000
Payload: 0x0077-0x0FFF (3977 bytes, all zeros in remotesw)

### 0x64 — main payload record
Offset 0x1000 in both files.
Evidence: 01 00 01 00 64 06 00 0a 00 0b 00 0a 00 0a 10 15
FieldA=0x0006, FieldB=0x000A
Payload: 0x1009-0x9062 (32858 bytes, ARM code/data)
Length encoding: UNKNOWN — do not use FieldB as length

### 0x67 — EOF trailer record
Evidence: 01 00 01 00 67 ff ff 00 00
FieldA=0xFFFF, FieldB=0x0000
Formula CONFIRMED: next = offset + 9 + 0 = EOF
Payload size: 0 bytes

## remotesw_090100.GCD record map

| Offset   | Type | Payload start | Next     | Payload size   |
|----------|------|---------------|----------|----------------|
| 0x0008   | 0xDC | 0x0011        | 0x006E   | 93 (0x5D)      |
| 0x006E   | 0x4C | 0x0077        | 0x1000   | 3977 (0xF89)   |
| 0x1000   | 0x64 | 0x1009        | 0x9063   | 32858 (0x805A) |
| 0x9063   | 0x67 | 0x906C        | EOF      | 0              |

## Length handling

Confirmed: types 0x4C and 0x67 → FieldB is LE uint16 payload length
Unknown:   types 0xDC and 0x64 → FieldB does NOT encode payload length

## Resource extraction results

- 20 PNG files were extracted from embedded payload regions and opened
  successfully. These appear to be bootloader UI assets.
- 6 `1f 8b` hits were found inside large payloads. Direct `gzip` decompression
  currently fails with "Unknown compression method", so their true content
  remains TBD.
- `BM` hits were false positives caused by ARM Thumb opcodes and nearby data.
  No valid standalone BMP files were confirmed.

## Additional record observations

- Type `0x43` begins with UTF-16 LE text and appears to store localization
  data.
- Type `0x30` begins with UTF-16 LE menu/path-style strings such as `1:/`.
- Internal strings (GARMIN, RGN, LBL, NET, NOD, MDR, SRT) are payload
  contents, not top-level container markers.
- 0xFF padding near EOF is consistent with flash memory storage.
- The file likely contains an embedded FAT filesystem image
  (strings "OS5.0", "FAT32", "FAT16" found at 0x3C6E9).

## Open questions for Phase 4

- What encodes payload length for types 0xDC and 0x64?
- Are other record types length-delimited or scan-delimited?
- Are the 6 `1f 8b` hits real compressed streams with a Garmin-specific wrapper
  or false positives similar to the BMP hits?
- What is the full type registry for GUPDATE.GCD (80+ types found)?
