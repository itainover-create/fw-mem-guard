# FW Mem Guard 0.3.7 — Quick start

Evaluation pre-release. Processing stays local; there is no automatic firmware upload or product telemetry. The engine is proprietary.

## Choose the supported host

- VS Code: Windows x64; macOS 15+ Apple Silicon or Intel.
- WSL: use the Windows extension on the local UI host and the guided saved-project workflow.
- Linux x64: separate compiled CLI/CI package, glibc 2.28+ and documented dependencies; Node.js 22 or 24. There is no Linux VSIX.
- Remote-SSH, Dev Containers and browser execution are not supported.

## First useful result

1. Install fwmemguard.fw-mem-guard and select the pre-release. Trust only a workspace you control.
2. Run **FW Mem Guard: Run Demo**. Its BUDGET_EXCEEDED result is intentional.
3. Try the [verified MicroPython or Zephyr pair](REAL_FIRMWARE.html). No board is required to compare supplied artifacts.
4. Run **Set Up / Update Project**. Select baseline MAP + matching ELF, then current MAP + matching ELF from two completed builds.
5. Explicitly select compatible non-overlapping Flash/RAM banks. Set aggregate total/growth limits and per-bank limits for multi-bank projects.
6. Choose **Validate and Save**. Review the results panel, section growth, effective limits and conservative object/archive contributions.
7. After another completed build, use **Compare Builds** or **Repeat Last Comparison**. Keep the baseline fixed. Use **Open Project** after restarting.

For Zephyr, select the final zephyr.map and zephyr.elf from the same completed build and image. Intermediate zephyr_pre*.map/elf files are not the final pair. Custom directories and sysbuild change the parent path; compare one image at a time.

## Inputs and outcomes

Complete GNU ld MAP plus matching ARM ELF32 little-endian ET_EXEC files; unchanged supported memory layout. Initialized RAM also occupies its Flash load image. Allocated section bytes are not runtime heap/stack peaks. Limits: 32 MiB per MAP, 64 MiB per ELF and 1 MiB per project JSON.

PASS / exit 0 means all configured comparison budgets passed. BUDGET_EXCEEDED / exit 2 means a valid comparison exceeded at least one budget. ERROR / CLI exit 1 means no valid comparison result; review the diagnostic.

Exact verified configurations: MicroPython v1.24.1 NUCLEO_F411RE and Zephyr v3.7.0 qemu_cortex_m3 with GNU Arm. STM32CubeIDE, MCUXpresso and nRF Connect SDK installation/build-pair validation remains pending. No whole-family certification is implied.

[Detailed English guide](START_HERE_EN.html) · [CLI/CI guide](https://github.com/itainover-create/fw-mem-guard/releases/download/v0.3.7/CLI_CI.md) · [GitHub Action](https://github.com/itainover-create/fw-mem-guard-action)

## Feedback

[Report a first own-project run or blocker](https://github.com/itainover-create/fw-mem-guard/issues/new?template=question.yml). Include the host, toolchain, whether you obtained a useful result and whether you returned for another comparison. This is public; do not attach proprietary firmware, source, credentials or private paths.

**Export Report for Sharing** opens a reduced JSON editor tab for review and optional Save As. It is not uploaded automatically. Totals and budgets can still be sensitive.

[Support](SUPPORT.md) · [Privacy](PRIVACY.md). The supplied evaluation license does not grant general production-use or engine source rights.
