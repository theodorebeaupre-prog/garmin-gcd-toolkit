#!/usr/bin/env bash
# Pre-commit safety check: refuse commits containing Garmin firmware or PII files.
set -euo pipefail

DANGER_PATTERNS=(
    "\.gcd$"
    "\.GCD$"
    "\.img$"
    "\.bin$"
    "GarminDevice\.xml"
    "GUPDATE"
    "gmapprom"
    "gmapbmap"
    "\.gpx$"
    "\.gma$"
    "\.unl$"
)

STAGED=$(git diff --cached --name-only 2>/dev/null || true)

if [ -z "$STAGED" ]; then
    echo "[safety] No staged files."
    exit 0
fi

FOUND=0
for pattern in "${DANGER_PATTERNS[@]}"; do
    matches=$(echo "$STAGED" | grep -iE "$pattern" || true)
    if [ -n "$matches" ]; then
        echo "[safety] BLOCKED — dangerous file(s) staged:"
        echo "$matches" | sed 's/^/  /'
        FOUND=1
    fi
done

if [ "$FOUND" -eq 1 ]; then
    echo "[safety] Commit aborted. Remove these files from staging and try again."
    exit 1
fi

echo "[safety] OK — no sensitive files detected."
exit 0
