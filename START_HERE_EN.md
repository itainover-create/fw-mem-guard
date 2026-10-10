FW Mem Guard 0.3.3 — Quick Start

[FW Mem Guard](index.html) · [English](START_HERE_EN.html) · [Support](SUPPORT.html)

# FW Mem Guard 0.3.3 — Quick Start

**Help inside VS Code:** Open the Command Palette → `FW Mem Guard: Open User Guide`, then choose English or Support. No browser or internet connection is needed.

**Publisher: FW Mem Guard — `fwmemguard`.** Extension ID: `fwmemguard.fw-mem-guard`. Disable the old `fw-mem-guard-pilot.fw-mem-guard` extension if installed, then use Open Project to reopen your existing project file. Previous workspace selections may not carry over. Project files remain unchanged.

Install the VS Code extension, then compare completed firmware builds. No Python or separate installer is required.

This guide accompanies the 0.3.3 pre-release packages for Windows x64, Mac Apple Silicon and Mac Intel. The extension and engine 0.1.0-pilot.1 have separate version numbers.

## 1. Install the right package

Search for `fwmemguard.fw-mem-guard` in VS Code Extensions and select the pre-release offered by the Marketplace. For a supplied candidate, use Install from VSIX with the matching file below.

| Computer          | VSIX                                   |
|-------------------|----------------------------------------|
| Windows x64       | `fw-mem-guard-0.3.3-win32-x64.vsix`    |
| Mac Apple Silicon | `fw-mem-guard-0.3.3-darwin-arm64.vsix` |
| Mac Intel         | `fw-mem-guard-0.3.3-darwin-x64.vsix`   |

Mac native command-line and package checks passed on macOS 15.7.9. Compatibility with macOS 13/14 remains unverified; the 0.3.3 package metadata and bundled guide still declare a 15.0 target. See [Mac validation details](index.html#scope). In VS Code choose Extensions → … → Install from VSIX, select the matching file, and reload if requested. Confirm version 0.3.3. On WSL, choose the Windows package for the local Windows host.

If the binary is blocked by security policy, stop and share the error. Do not disable protections or change quarantine settings.

## 2. Run the example

Open a folder you control and trust it when prompted. Press Ctrl+Shift+P (Mac: Cmd+Shift+P) and run **FW Mem Guard: Run Demo**. Expected: BUDGET_EXCEEDED, engine exit 2. The example intentionally exceeds its limits and is not validation of your project.

## 3. Set up your project once

1.  Run **Set Up / Update Project**.
2.  Select baseline.map + its matching baseline.elf, then current.map + its matching current.elf. Use successful completed builds and distinct baseline/current files.
3.  Review each Flash/RAM candidate: start/end addresses, capacity and coverage of VMA/run and LMA/load sections in both builds. A unique compatible region is suggested; confirm it explicitly. If multiple overlapping containers fit, choose explicitly. Unavailable choices name the uncovered section and address. One active region of each type is supported.
4.  Enter maximum total bytes and allowed growth bytes for both regions. A growth limit of 0 forbids any positive growth; it does not disable checks.
5.  Review and choose Validate and Save. Use a new filename such as `board.fwmg.json`. One suffix is retained for new files. An existing file is never overwritten by new setup.

## 4. Daily use and budgets

After each completed build run **Compare Builds** or **Repeat Last Comparison**. Keep baseline files unchanged. To change limits, use **FW Mem Guard: Edit Budgets**: select an existing project if none is active, enter four values and Validate and Save. No new filename is requested. To change artifact paths or intentionally replace the baseline, use Set Up / Update Project → Update active project.

To reopen, run **Open Project** and select the existing .fwmg.json file. Existing names with duplicate suffixes still work; do not create another project just to edit budgets.

## 5. WSL on Windows

1.  Install Microsoft WSL in VS Code and connect to your distribution/project folder.
2.  Confirm the bottom-left indicator says **WSL: …**. Trust this folder separately if prompted.
3.  Use the guided commands and the remote picker. Save the project in the same WSL filesystem as its four artifacts.
4.  In report DETAILS, artifact references should start with `vscode-remote://wsl`. Encoded `%2B` is normal.

FW Mem Guard runs on the Windows UI host; no Linux engine or Python installation is needed in WSL. If the connection/window closes, reconnect, open the saved project and repeat. Input reading has a 30-second limit and a Cancel button. After timeout/cancel, no late result is accepted. Reconnect and retry. VS Code may continue the underlying filesystem request; this is not a promise that closing VS Code is prevented. The limit excludes selection, engine execution and saving. User setting: `fwMemGuard.inputReadTimeoutSeconds` (1–300 seconds).

## 6. Read the outcome

- **PASS / exit 0:** all configured comparison budgets passed.
- **BUDGET_EXCEEDED / exit 2:** at least one effective limit was exceeded.
- **ERROR:** no valid result for this operation. Validation can stop before the engine runs, so an engine exit code may be absent.
- **ANALYZED:** totals only; budgets were not checked. In an active project, both pairs are validated and the CURRENT Map is analyzed; its path is printed in Output.

## 7. Export a report for support

After a completed comparison or Analyze, run **FW Mem Guard: Export Report for Sharing**. The report opens first in a new, unsaved editor tab; no report file is created on disk. Review its contents, then use **Save As** to save `result.fwmg-report.json` if you choose to share it. This command is available from version 0.3.2; it is absent from 0.3.1.

The export includes memory totals, effective limits, result/context, component versions and capture time. It excludes paths, filenames, symbols, section names, addresses and input hashes. Usage and limits may still be sensitive. The extension does not upload it. If you attach it to a support email, your email provider and the recipient receive what you send. Share only what your organization permits.

Demo reports remain labeled examples; Analyze has no budget verdict. A new project/profile operation clears the exportable result, including failure or cancellation. Help and Output preserve it. After a reload, run again. Previously opened or saved reports remain static snapshots and do not update automatically.

## Limits and troubleshooting

For support after a completed run, use **Export Report for Sharing**, review the new editor tab, then save and attach the reduced report to an email using the address on the Support page. A failed run has no new export: describe the error and review any diagnostic text before sending it. Do not attach Map/ELF files or source code.

64 MiB per ELF; 32 MiB per Map. GNU Arm ELF32 little-endian + GNU ld. One Flash and one RAM bank. No SSH, Containers, Linux native, IAR/Keil, or object/symbol attribution. Full ELF files are read, including debug data; do not strip artifacts just to bypass validation limits.

Mismatch: select Map/ELF from the same completed build. Missing/empty file: fix the build inputs and repeat. Existing project: Open Project, then Edit Budgets. Trust error: approve only a folder you control using Workspaces: Manage Workspace Trust. Open Output for full diagnostics.

Manual Profile Comparison requires a reviewed engine JSON, not a .fwmg.json project, and is local-only. Guided WSL use does not require a UNC allowlist. For the optional local-window UNC route, allow only the specific WSL host in security.allowedUNCHosts and keep UNC restrictions enabled.

Support: `fwmemguard.support@gmail.com`

While a previous read of the same URI remains pending, retries show an explicit error and do not start another transfer. After it settles and connectivity returns, retry reads fresh input.

If the pending-read message persists, save your work and run Developer: Reload Window from the Command Palette. Reconnect to WSL, open the saved project and compare again. Reload resets extension state; it does not repair an unavailable connection.

## Example and accounting

    BUDGET_EXCEEDED
    Configured budget exceeded.

    FLASH  +51,200 bytes  (720,896 -> 772,096)
    RAM  +27,136 bytes  (176,640 -> 203,776)

    BUDGET CHECKS — effective limits for this run
    FLASH allocated sections: 772,096 <= 1,048,576 bytes — OK
    FLASH growth: 51,200 > 16,384 bytes — EXCEEDED
    RAM allocated sections: 203,776 <= 262,144 bytes — OK
    RAM growth: 27,136 > 4,096 bytes — EXCEEDED

    Accounting: configured linker profile; allocated output-section bytes.
    Object/symbol attribution: not available.

Bundled demo data. The report prints each checked value and limit. Initialized RAM is counted once in RAM and once for its Flash load image. Heap/stack reservations are not measured runtime usage. Structural Map/ELF agreement does not establish common build provenance or an atomic snapshot. Guided validation is currently in the extension, not a standalone Map/ELF CLI contract.

Support opens its own bundled page through Open User Guide → Support. Copy the support address into your email service; no reports, telemetry or firmware files are uploaded automatically.
