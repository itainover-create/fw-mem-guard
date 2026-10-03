[FW Mem Guard](index.html) · [English guide](START_HERE_EN.md) · <a href="START_HERE_HE.html" lang="he">עברית</a> · [Privacy](PRIVACY.md)

# FW Mem Guard Support

Help with installation, project setup and Flash/RAM comparisons. Guide for the 0.3.3 pre-release; engine 0.1.0-pilot.1.

<div class="contact">

**Contact**

Support: `fwmemguard.support@gmail.com`

Copy this address into your email service to report a problem or share feedback. The extension does not send reports or files automatically.

</div>

[Open a public problem report or question](https://github.com/itainover-create/fw-mem-guard/issues/new/choose). Public issues are visible to everyone. Include only reviewed information you are authorized to share.

## Before reporting a problem

- **Demo shows BUDGET_EXCEEDED / exit 2:** this is expected. The bundled example intentionally exceeds its budgets.
- **Project comparison shows BUDGET_EXCEEDED:** read the effective limits. Use Edit Budgets only when changing your intended policy.
- **Manual profile error:** a .fwmg.json project belongs in Open Project, not Manual Profile Comparison.
- **Map/ELF mismatch:** select matching artifacts from the same completed build, then repeat.
- **Missing or incomplete file:** wait for the build to finish, correct the input paths and repeat.
- **WSL read remains pending:** reconnect. If it stays stuck, save your work, run Developer: Reload Window, then Open Project and compare again.
- **Blocked native executable:** include the exact error. Follow your organization's IT policy; do not disable security controls to run the preview.

## What to include

Include this short template in your email. Copy the relevant diagnostic from FW Mem Guard: Open Output.

    Extension version (copy installed version):
    OS and processor: Windows x64 / macOS Apple Silicon / macOS Intel
    VS Code version:
    Workspace: local / WSL
    Command used:
    Expected result:
    Actual result and full error:
    What worked before the first blocker:
    Steps to reproduce:
    Map and ELF sizes (if relevant):

Review paths and identifiers before sharing. Start with the diagnostic text. Do not attach proprietary source, Map or ELF files unless you are authorized to share them. Do not send passwords or access tokens.

## Preview scope

Local Windows x64 and macOS Intel/Apple Silicon (macOS 15+ for these packages); guided WSL access on Windows. GNU ld Map with GNU Arm ELF32 little-endian, one active Flash and one active RAM region. Maximum 64 MiB per ELF and 32 MiB per Map. Remote-SSH, Dev Containers, Codespaces, Linux-native execution, IAR/Keil and object/symbol attribution are not supported.

<span class="small">Publisher: FW Mem Guard · Extension ID: fwmemguard.fw-mem-guard · Local processing; no automatic telemetry or report upload. Use the support address below or the public issue forms.</span>

## Attach a reduced report to a support request

After a completed run, use **Export Report for Sharing**. The report opens first in a new, unsaved editor tab; no report file is created on disk. Review its contents, then use **Save As** to save a separate `.fwmg-report.json` file if you choose to attach it to your support email. No file is uploaded automatically.

Reduced reports exclude paths, filenames and symbols but still reveal memory usage and limits. Share only what your organization permits; your email provider and the recipient receive what you send. There is no need to attach Map/ELF files or source code. Saved reports are static snapshots.

If a run failed or was cancelled, there is no new report to export. Describe the error and review any diagnostic text before sending it. Run a fresh successful operation when you need a new result.
