# Garmin .GCD Format — Reverse Engineering Notes

> **Status:** Phase 1 skeleton — observations are empirical hypotheses, not confirmed spec.
> Device: nüvi 2455 (PN 006-B1371-00), Firmware 8.30, File: GUPDATE.GCD (50,201,232 bytes)

## Overall structure (hypothesis)

| Region         | Offset range        | Size   | Notes                          |
|----------------|---------------------|--------|--------------------------------|
| File header    | 0x00000 – 0x00FFF   | 4 KB   | Zero-padded to page boundary  |
| Data records   | 0x01000 – EOF       | ~48 MB | TBD in Phase 2–3               |

## Header (0x00 – 0x0FFF)

Observed bytes — first 128 (the rest is null padding):

```
0x00  47 41 52 4d 49 4e 64 00   Magic: "GARMINd\0"
0x08  01 00 01 00               [?] Two LE uint16, both = 1
0x0C  dc 02 00 15               [?] Unknown — 4 bytes
0x10  [22 × 0x00]               Reserved
0x26  03 00                     [?] LE uint16 = 3
0x28  09 00                     [?] LE uint16 = 9
0x2A  10 d4 5c 13               [?] 4 bytes — timestamp? checksum?
0x2E  04 45 0d 14 41 05 00      [?] 7 bytes — unknown
0x35  37 00                     [HYP] LE uint16 = 0x37 — offset to copyright string?
0x37  43 6f 70 79 ...           ASCII: "Copyright 1996-2013 by Garmin Ltd.
                                 or its subsidiaries." (55 bytes, null-term at 0x6E)
0x64  01 00 01 00               [?] Repeats 0x08 pattern — another record start?
0x68  4b 02                     [?] LE uint16 = 587
0x6A  00 89 0f 00               [?] 4 bytes — unknown
0x6E  [0x0F92 × 0x00]           Zero padding to 0x1000
```

## Known embedded content types

- gzip streams (magic: `1f 8b`) — many present
- PNG images (magic: `89 50 4e 47`) — hundreds present
- SQLite schemas
- Bitstream fonts
- SoundClear DSP firmware
- VoCon 3200 speech engine
- CRC32 tables (LE and BE)
- SHA256 constants

## Internal Garmin source paths (leaked in binary)

```
gpk\gps_st\garminos\os20\gps_st_os20_semaphore.c
gpk\gps_st\garminos\os20\gps_st_os20_task.c
```

Target architecture: ARM. OS: GarminOS (proprietary) based on OS20 RTOS (STMicro).

## Open questions (Phase 2)

- What do bytes 0x08–0x0F encode? (version fields?)
- Is 0x35–0x36 really an offset pointer or a length?
- What is the record structure starting at 0x1000?
- Is there a Table of Contents, or are records inline with headers?
- What algorithm protects the file? (CRC32? SHA256? none?)
