#!/usr/bin/env python3
"""Rebuild the MicroPython F411 example into a NEW directory on Ubuntu 24.04 x86-64.

Run: python3 build_from_source.py /absolute/path/to/new-build-directory
Install the packages listed in BUILD_FROM_SOURCE.md first. Never overwrites the
original example firmware. Network access to GitHub is required.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

COMMIT = 'ecfdd5d6f9be971852003c2049600dc7b3e2a838'
PACKAGES = {'gcc-arm-none-eabi': '15:13.2.rel1-2', 'binutils-arm-none-eabi': '2.42-1ubuntu1+23',
            'libnewlib-dev': '4.4.0.20231231-2'}
ASSETS = Path(__file__).resolve().parent


def capture(command, cwd=None):
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work', type=Path, help='New directory for source, rebuilt pair and evidence')
    args = parser.parse_args()
    work = args.work.resolve()
    os_info = platform.freedesktop_os_release()
    if os_info.get('ID') != 'ubuntu' or os_info.get('VERSION_ID') != '24.04' or platform.machine() != 'x86_64':
        raise ValueError('This recipe is verified only on Ubuntu 24.04 x86-64')
    # Reject inherited make overrides that could silently turn release into a different build.
    for key in ('DEBUG', 'CFLAGS', 'COPT', 'LDFLAGS', 'MAKEFLAGS', 'MFLAGS', 'CROSS_COMPILE', 'CC', 'CXX', 'MICROPY_MPYCROSS'):
        if os.environ.get(key):
            raise ValueError('Unset the build override ' + key + ' before running')
    packages = {}
    for name in [*PACKAGES, 'build-essential', 'git', 'python3', 'ca-certificates']:
        state = capture(['dpkg-query', '-W', '-f=${Status}\t${Version}', name])
        status, version = state.split('\t')
        if status != 'install ok installed' or (name in PACKAGES and version != PACKAGES[name]):
            raise ValueError('Package/version mismatch: ' + name + ' ' + state)
        packages[name] = version
    for name in ('change.patch', 'check_sections.py', 'verified-reference-sections.csv'):
        if not (ASSETS / name).is_file():
            raise ValueError('Missing adjacent asset: ' + name)
    work.mkdir(parents=True, exist_ok=False)
    source, pair = work / 'micropython', work / 'rebuilt'
    logs = work / 'logs'
    logs.mkdir()
    commands = []

    def run(command, label, cwd=None):
        commands.append(command)
        print(label, flush=True)
        with (logs / (label + '.txt')).open('w') as log:
            subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True)

    run(['git', 'clone', '--depth', '1', '--branch', 'v1.24.1', 'https://github.com/micropython/micropython.git', str(source)], 'clone')
    actual_commit = capture(['git', 'rev-parse', 'HEAD'], source)
    if actual_commit != COMMIT:
        raise ValueError('MicroPython tag does not resolve to the pinned commit')
    make = ['make', '-C', str(source / 'ports/stm32'), 'BOARD=NUCLEO_F411RE', 'BUILD=build-fwmg']
    run([*make, 'submodules'], 'submodules')
    makefile = source / 'ports/stm32/Makefile'
    text = makefile.read_text()
    text, count = re.subn(r'(?m)^CFLAGS \+= -g(  # always include debug info.*)$', r'CFLAGS += -g3\1', text)
    if count != 1 or 'COPT ?= -Os -DNDEBUG' not in text:
        raise ValueError('Unexpected release Makefile; refusing to guess')
    makefile.write_text(text)
    run(['make', '-C', str(source / 'mpy-cross'), '-j2'], 'mpy-cross')
    for build in ('baseline', 'current'):
        if build == 'current':
            run(['git', 'apply', '--check', str(ASSETS / 'change.patch')], 'patch-check', source)
            run(['git', 'apply', str(ASSETS / 'change.patch')], 'patch', source)
        run([*make, '-j2'], build)
        (pair / build).mkdir(parents=True)
        for extension in ('elf', 'map'):
            name = 'firmware.' + extension
            shutil.copyfile(source / 'ports/stm32/build-fwmg' / name, pair / build / name)
    evidence = work / 'verification'
    run([sys.executable, str(ASSETS / 'check_sections.py'), str(pair), '--reference', str(ASSETS / 'verified-reference-sections.csv'), '--output', str(evidence)], 'section-check')
    # Negative control: the checker must reject a one-byte error in the reference.
    with (ASSETS / 'verified-reference-sections.csv').open(newline='') as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    rows[0]['size_bytes'] = str(int(rows[0]['size_bytes']) + 1)
    bad_reference = work / 'one-byte-mutated-reference.csv'
    with bad_reference.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    negative = subprocess.run([sys.executable, str(ASSETS / 'check_sections.py'), str(pair), '--reference', str(bad_reference), '--output', str(work / 'negative-control')], capture_output=True, text=True)
    (evidence / 'negative-control.txt').write_text(negative.stderr)
    if negative.returncode != 1 or 'Section mismatch:' not in negative.stderr:
        raise ValueError('One-byte negative control did not reject a section mismatch')
    submodules = capture(['git', 'submodule', 'status'], source)
    (evidence / 'submodules.txt').write_text(submodules + '\n')
    tools = {name: capture([name, '--version']).splitlines()[0] for name in ('arm-none-eabi-gcc', 'arm-none-eabi-objdump', 'make', 'git', 'python3', 'gcc')}
    hashes = {str(p.relative_to(work)): digest(p) for p in sorted(pair.rglob('*')) if p.is_file()}
    hashes.update({str(p.relative_to(work)): digest(p) for p in sorted(logs.glob('*.txt'))})
    hashes.update({str(p.relative_to(work)): digest(p) for p in sorted(evidence.glob('*')) if p.is_file()})
    receipt = {'status': 'PASS', 'verified_at_utc': datetime.now(timezone.utc).isoformat(),
               'os': os_info['PRETTY_NAME'], 'architecture': platform.machine(), 'packages': packages, 'tools': tools,
               'micropython_commit': actual_commit, 'board': 'NUCLEO_F411RE', 'build': 'build-fwmg',
               'flags': '-Os -DNDEBUG -g3; DEBUG=1 not used; same build directory for both builds',
               'claim': '18 allocated section address/size records match; no ELF byte-identity claim',
               'section_check': json.loads((evidence / 'section-check.json').read_text()),
               'negative_control': {'reference_change_bytes': 1, 'exit_code': negative.returncode, 'rejected': True},
               'asset_sha256': {name: digest(ASSETS / name) for name in ('build_from_source.py', 'check_sections.py', 'change.patch', 'verified-reference-sections.csv')},
               'output_sha256': hashes, 'commands': commands}
    (work / 'build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('PASS: all 18 section records match; one-byte mutation rejected. Receipt: ' + str(work / 'build-receipt.json'))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
