# FW Mem Guard GitHub Action

Compare completed GNU Arm firmware builds on an **Ubuntu 24.04 x64** runner.
The public wrapper downloads a compiled CLI release, checks the release asset's
SHA-256 digest before extraction, and runs the saved project. Private engine
source is not distributed. The Action's Node runtime is used automatically.

**Release status:** this wrapper targets CLI 0.3.5. Publish its compiled
`fw-mem-guard-0.3.5-linux-x64.tar.gz` asset under release `v0.3.5` before enabling
the example. Source code alone does not make that binary available.

After checkout, firmware compilation, and restoring your reviewed baseline:

```yaml
- name: Check firmware memory budgets
  uses: itainover-create/fw-mem-guard@v0.3.5
  with:
    project: firmware.fwmg.json
```

If the project is named `firmware.fwmg.json` at the workspace root, the integration
is a single `uses:` line. Pin the Action to a reviewed full commit SHA for production.
The exact CLI version defaults to 0.3.5; floating versions such as `latest` are
rejected. The two release references are separate: `uses` selects the wrapper,
and the `version` input selects the compiled CLI.

Inputs: `project` (default `firmware.fwmg.json`), `version` (default `0.3.5`),
`report` (default `fwmg-result.json`). Paths are relative to the workspace.
The report's parent directory must exist. Existing report files are never
overwritten, so choose distinct filenames for multiple runs in a job.

Outputs: `exit-code` and, for a valid comparison, `report-path`. PASS exits 0,
budget violations exit 2 and fail the step, input/download/runtime errors exit 1.
The report is also written on budget failure. No JSON report is created on error.
A short aggregate summary appears in the job; full object paths stay in the local
report unless you deliberately upload it. There is no automatic artifact upload.

To block a merge, make this job a required check in repository rules. Do not use
`continue-on-error` or reset the saved baseline automatically after a failure.
Both baseline/current MAP and matching ARM ELF32 little-endian files must be
available with the paths saved in the project. Linux application ELF files are
outside this firmware format. See the [JSON contract](../CLI_JSON.md).

The Action needs outbound HTTPS to GitHub Releases and the public API. No publisher
token or private-repository read permission is required to download the public CLI.
GitHub API rate limits and network failures produce an explicit failed step.

## Publishing checklist for the maintainer

1. Build and test the exact candidate in the private native workflow.
2. Upload only the compiled Linux CLI archive and its checksum to a public draft
   release named `v0.3.5`. Retain all bundled licenses. Never upload the developer kit.
3. Publish the release against the reviewed public wrapper commit, then verify the
   asset digest, download and real PASS → exit 2 → PASS workflow.
4. In GitHub's release UI, select **Publish this Action to the GitHub Marketplace**;
   complete the Marketplace Developer Agreement if required. Suggested primary
   category: Continuous integration. A release alone does not establish a listing.

The wrapper code in this directory is MIT-licensed. The compiled CLI retains its
own license included in the downloaded package.
