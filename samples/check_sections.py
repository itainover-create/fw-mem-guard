#!/usr/bin/env python3
"""Independently compare F411 allocated section addresses/sizes using GNU objdump.

No FW Mem Guard imports or third-party Python dependencies. Exit 0: match;
exit 1: invalid input or mismatch. ELF byte identity is deliberately not claimed.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

FIELDS = ['build', 'section', 'memory', 'kind', 'address', 'size_bytes']
HEADER = re.compile(r'^\s*\d+\s+(\S+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+2\*\*\d+\s*$')


def inside(address, size, start, capacity):
    return start <= address and address + size <= start + capacity


def sections(text, build):
    rows, seen = [], set()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = HEADER.match(line)
        if not match:
            continue
        name = match[1]
        size, vma, lma = (int(match[n], 16) for n in (2, 3, 4))
        if i + 1 == len(lines):
            raise ValueError('Missing section flags')
        flags = {s.strip() for s in lines[i + 1].split(',')}
        if not size or 'ALLOC' not in flags:
            continue
        if name in seen:
            raise ValueError('Duplicate allocated section: ' + name)
        seen.add(name)
        if 'LOAD' in flags:
            if not inside(lma, size, 0x08000000, 524288):
                raise ValueError('Unexpected Flash load range: ' + name)
            rows.append((build, name, 'FLASH', 'load_image', lma, size))
        if inside(vma, size, 0x20000000, 114688):
            kind = 'reservation' if name in ('.heap', '.stack') else 'runtime'
            rows.append((build, name, 'RAM', kind, vma, size))
        elif not inside(vma, size, 0x08000000, 524288):
            raise ValueError('Unexpected allocated VMA: ' + name)
        elif 'LOAD' not in flags:
            raise ValueError('Unexpected non-loadable Flash section: ' + name)
    if not rows:
        raise ValueError('No allocated sections parsed')
    return rows


def reference_rows(path):
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError('Unexpected reference CSV columns')
        result = []
        for row in reader:
            if row['build'] not in ('baseline', 'current') or row['memory'] not in ('FLASH', 'RAM'):
                raise ValueError('Unexpected reference build or memory')
            result.append((*[row[k] for k in FIELDS[:4]], int(row['address'], 16), int(row['size_bytes'])))
    if len(result) != 18 or len({r[:4] for r in result}) != 18:
        raise ValueError('Expected exactly 18 unique reference records')
    return result


def verify(pair, reference, output, objdump):
    output.mkdir(parents=True, exist_ok=True)
    version = subprocess.check_output([objdump, '--version'], text=True).splitlines()[0]
    if not version.startswith('GNU objdump'):
        raise ValueError('GNU objdump is required')
    expected = reference_rows(reference)
    actual, hashes = [], {}
    for build in ('baseline', 'current'):
        elf = pair / build / 'firmware.elf'
        text = subprocess.check_output([objdump, '-h', str(elf)], text=True)
        # Only the path in the heading is normalized; section output is untouched.
        (output / (build + '-objdump.txt')).write_text(text.replace(str(elf), build + '/firmware.elf'))
        actual.extend(sections(text, build))
        for extension in ('elf', 'map'):
            file = pair / build / ('firmware.' + extension)
            if file.is_file():
                hashes[build + '/firmware.' + extension] = hashlib.sha256(file.read_bytes()).hexdigest()
    if sorted(actual) != sorted(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise ValueError('Section mismatch: expected-only=' + repr(missing) + '; actual-only=' + repr(extra))
    totals = {}
    for build in ('baseline', 'current'):
        totals[build] = {memory.lower(): sum(r[5] for r in actual if r[0] == build and r[2] == memory) for memory in ('FLASH', 'RAM')}
    delta = {k: totals['current'][k] - totals['baseline'][k] for k in ('flash', 'ram')}
    receipt = {'status': 'PASS', 'scope': 'Exact addresses and sizes of 18 allocated section records; not ELF byte identity',
               'records_matched': len(actual), 'objdump_version': version, 'reference_sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
               'input_sha256': hashes, 'totals': totals, 'delta': delta}
    (output / 'section-check.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pair', type=Path, help='Directory containing baseline/ and current/')
    parser.add_argument('--reference', type=Path, default=Path(__file__).with_name('verified-reference-sections.csv'))
    parser.add_argument('--output', type=Path, required=True, help='New evidence directory; must not already exist')
    parser.add_argument('--objdump', default='arm-none-eabi-objdump')
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError('Use a new output directory; earlier evidence is preserved')
        print(json.dumps(verify(args.pair.resolve(), args.reference.resolve(), args.output.resolve(), args.objdump), indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
