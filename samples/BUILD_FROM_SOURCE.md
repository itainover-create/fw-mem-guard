# Rebuild the MicroPython F411 example

This recipe checks **addresses and sizes of 18 allocated section records** against
`verified-reference-sections.csv`. It does not promise byte-identical ELF or Map
files: debug paths, generated build information and other non-allocated content
can differ. The four original firmware files in the example ZIP remain unchanged.
No FW Mem Guard engine source is required or included in this procedure.

## Environment

Use Ubuntu 24.04 x86-64 (a VM or WSL2 Ubuntu 24.04 is suitable), with Internet
access for GitHub and Ubuntu packages. Install:

```sh
sudo apt-get update
sudo apt-get install --no-install-recommends \
  gcc-arm-none-eabi=15:13.2.rel1-2 \
  binutils-arm-none-eabi=2.42-1ubuntu1+23 \
  libnewlib-dev=4.4.0.20231231-2 \
  build-essential git python3 ca-certificates
```

These three cross-toolchain package versions are pinned; do not silently replace
them if your repository does not offer them. The recipe records the installed
versions of the other packages and the tool version strings in its receipt.

## Run the checked recipe

Extract the complete example ZIP, then from its root run:

```sh
python3 build_from_source.py "$HOME/fwmg-micropython-rebuild"
```

Choose a **new, nonexistent output directory**. The script refuses to overwrite
an earlier run. `build_from_source.py`, `check_sections.py`, `change.patch` and
`verified-reference-sections.csv` must be together. The script checks Ubuntu,
architecture, packages, the source commit, and accidental inherited build flags.
It never overwrites `baseline/` or `current/` in the supplied example.

The build sequence is:

1. Clone tag `v1.24.1` and require HEAD to equal
   `ecfdd5d6f9be971852003c2049600dc7b3e2a838`.
2. `make -C ports/stm32 BOARD=NUCLEO_F411RE BUILD=build-fwmg submodules`
3. In `ports/stm32/Makefile`, change the **release** `CFLAGS += -g` line to
   `CFLAGS += -g3`. Keep that change for both builds. Keep the normal
   `COPT ?= -Os -DNDEBUG`; **do not set `DEBUG=1`**.
4. `make -C mpy-cross -j2`
5. `make -C ports/stm32 BOARD=NUCLEO_F411RE BUILD=build-fwmg -j2`
6. Copy `ports/stm32/build-fwmg/firmware.elf` and `firmware.map` into
   `rebuilt/baseline/` under the new output directory.
7. Apply the supplied `change.patch` with `git apply`.
8. Repeat step 5 in the **same `build-fwmg` directory** and copy the resulting
   pair into `rebuilt/current/`. Do not clean or switch to a DEBUG build.
9. Run the independent section checker, then alter one reference size by one
   byte and require the checker to reject it with exit code 1.

Full build logs are in `logs/`; raw GNU objdump section headers and the independent
result are in `verification/`. `build-receipt.json` records package/tool versions,
the source commit, commands, script/reference hashes, rebuilt artifact hashes,
log/evidence hashes and the negative-control result. Paths in that receipt are
the locations used for that run; ELF byte identity is not the acceptance criterion.

## Independently check either pair

From the extracted sample root:

```sh
python3 check_sections.py . --output original-section-check
python3 check_sections.py "$HOME/fwmg-micropython-rebuild/rebuilt" \
  --output rebuilt-section-check
```

Both output directories must be new. The default tool is `arm-none-eabi-objdump`;
`--objdump /path/to/gnu-objdump` allows another GNU build with ARM ELF support.
The checker uses only Python's standard library and GNU objdump, independently
of FW Mem Guard. It checks all nonempty ALLOC sections, Flash LOAD addresses and
RAM runtime addresses (including heap/stack reservations). `.isr_vector` and
`.data` are counted in both memories; non-allocated debug sections are excluded.

Expected totals in bytes:

| Memory | Baseline | Current | Delta |
| --- | ---: | ---: | ---: |
| Flash load images | 292212 | 300452 | 8240 |
| RAM including reservations | 22440 | 26536 | 4096 |

`build-receipt.json`, `rebuilt-baseline-objdump.txt`,
`rebuilt-current-objdump.txt` and `checker-negative-control.txt` distributed with
the example document the checked rebuild. SHA-256 values for newly rebuilt
files can differ from the original firmware hashes; that is expected.

## Demonstrate the RAM budget failure

Follow `TRY_GUIDED_SETUP_EN.md` or `TRY_GUIDED_SETUP_HE.md`. After the initial PASS,
run **FW Mem Guard: Edit Budgets**, lower **only RAM growth from 4096 to 4095**,
and leave Flash total **524288**, Flash growth **8240** and RAM total **114688**.
**Validate and Save automatically runs the comparison.** Expect exactly one
RAM growth violation: `actual=4096`, `limit=4095`, engine exit code **2**.
Restoring RAM growth to **4096** and choosing **Validate and Save** returns PASS.
Exit code 2 is the engine result; the extension presents the budget violation.

Raw failure output is supplied in `verification/ram-growth-4095.json` and
`verification/ram-growth-4095.txt`; the restored result is in
`verification/ram-growth-restored-4096.json`. Source-engine and guided-validator
checks do not constitute interactive installed-extension acceptance testing.

## Licenses

Keep all existing `licenses/` files. Added notices include the full upstream
`MICROPYTHON_LIB_LICENSE.txt` and `FROZEN_PYTHON_NOTICES.txt` for asyncio, dht and
onewire. Existing MicroPython, ST, CMSIS and GCC notices remain in force.
The firmware package as a whole is not relicensed under MIT.
