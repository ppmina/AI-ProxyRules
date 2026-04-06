#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = ROOT / "source" / "providers"
DEFAULT_OUTPUT_DIR = ROOT / "publish"

DOMAIN_PATTERN = re.compile(
    r"^(?:\*\.)?(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)
SLUG_PATTERN = re.compile(r"^[a-z0-9-]+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build DOMAIN-SET TXT files from provider source lists."
    )
    parser.add_argument(
        "--source-dir",
        default=str(DEFAULT_SOURCE_DIR),
        help="Directory containing provider source TXT files.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where publishable TXT files should be written.",
    )
    return parser.parse_args()


def normalize_entries(lines: list[str]) -> list[str]:
    entries: list[str] = []
    seen: set[str] = set()

    for raw_line in lines:
        line = raw_line.strip().lower()
        if not line or line.startswith("#"):
            continue
        if not DOMAIN_PATTERN.fullmatch(line):
            raise ValueError(f"Invalid domain entry: {raw_line.rstrip()}")
        if line.startswith("*."):
            line = f".{line[2:]}"
        if line in seen:
            continue
        seen.add(line)
        entries.append(line)

    return entries


def build_provider_set(path: Path) -> tuple[str, list[str]]:
    slug = path.stem
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f"Invalid provider filename: {path.name}")
    entries = normalize_entries(path.read_text(encoding="utf-8").splitlines())
    return slug, entries


def collect_provider_sets(source_dir: Path) -> list[tuple[str, list[str]]]:
    if not source_dir.exists():
        raise SystemExit(f"Missing source directory: {source_dir}")

    provider_paths = sorted(source_dir.glob("*.txt"))
    if not provider_paths:
        raise SystemExit(f"No provider files found in {source_dir}")

    return [build_provider_set(path) for path in provider_paths]


def write_domainset(path: Path, entries: list[str]) -> None:
    if entries:
        content = "\n".join(entries) + "\n"
    else:
        content = ""
    path.write_text(content, encoding="utf-8")


def write_outputs(
    provider_sets: list[tuple[str, list[str]]],
    output_dir: Path,
) -> list[Path]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []
    aggregate_entries: list[str] = []
    aggregate_seen: set[str] = set()

    for slug, entries in provider_sets:
        provider_output = output_dir / f"{slug}.txt"
        write_domainset(provider_output, entries)
        written_files.append(provider_output)

        for entry in entries:
            if entry in aggregate_seen:
                continue
            aggregate_seen.add(entry)
            aggregate_entries.append(entry)

    aggregate_output = output_dir / "ai.txt"
    write_domainset(aggregate_output, aggregate_entries)
    written_files.append(aggregate_output)
    return written_files


def main() -> None:
    args = parse_args()
    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    provider_sets = collect_provider_sets(source_dir)
    written_files = write_outputs(provider_sets, output_dir)

    print(
        f"Built {len(provider_sets)} provider file(s) and ai.txt into {output_dir}"
    )
    print("Published files:")
    for path in written_files:
        print(f"- {path.name}")


if __name__ == "__main__":
    main()
