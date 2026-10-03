# FW Mem Guard 0.3.3 — data handling

The bundled engine executes locally on the VS Code desktop host. FW Mem Guard has no telemetry client, account, license server or cloud upload feature.

In guided WSL mode on Windows, full Map and ELF contents are read through VS Code workspace.fs into local Windows memory. Validated maps and a generated profile are written to a temporary local directory for native execution and removed in a finally block; forced termination can leave temporary files. ELF contents are not intentionally written to that temporary directory. This transfers artifacts out of WSL to Windows; it does not keep processing within Linux.

Project JSON stores artifact references, layout, budgets and full baseline SHA256 values. Workspace state stores project/profile references and the last comparison. Reports can reveal paths, section information and memory sizes. Review them before voluntary support sharing. Structural agreement and metadata checks do not prove an atomic build snapshot.

Export Report for Sharing constructs a reduced JSON snapshot in a new, unsaved VS Code editor. It includes Flash/RAM totals, effective limits, result/context, component versions and capture time. It excludes input paths, filenames, addresses, symbols, section names, input hashes and arbitrary engine fields. These exports may still disclose sensitive memory usage and budgets; they are not anonymized or signed. Export state stays in memory and is cleared on a new project/profile operation, failure, cancellation or extension reload. Previously opened/saved documents remain static snapshots.

The export opens in an unsaved editor tab before you choose whether to save it; it creates no report file on disk and opens no save dialog automatically. Use Save As only after reviewing the contents. The command sends no data to any service. If you choose to attach the report to a support email or another service, the provider and recipient receive what you send under their own policies. Share only what your organization permits.

VS Code, its WSL extension, Marketplace downloads and update services have separate network behavior and policies. This statement applies to FW Mem Guard itself.
