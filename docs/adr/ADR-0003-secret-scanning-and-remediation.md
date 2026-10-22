# ADR-0003: Secret scanning and rotate-first remediation

- Status: Accepted
- Date: 2026-10-21
- Decision owners: Technical lead

## Context

A credential committed to version control is a credential in every clone, in
every fork, and in the provider's own logs. Deleting the file does not
withdraw it. The repository therefore needs two things that are often confused:

1. a check that finds secret material, and
2. a documented procedure for what to do when the check fires.

The check must also be safe to run in a pull request from an untrusted
contributor: its output is read by everyone.

## Decision drivers

- Detect credential material in the working tree and in the full
  version-controlled history.
- Never print a detected value, in stdout or in any machine-readable output.
- Run without a network connection and without an external binary, so it
  cannot fail for an environmental reason and silently pass.
- Make the remediation path unambiguous: rotation first, history rewriting
  second.

## Options considered

1. **Repository-native scanner (`ci/secret_scan.py`) (selected)** — benefits:
   no external binary to install or pin, the same Python patterns apply to the
   working tree and to the history, and the output format is under our
   control, so redaction is a property of the code rather than a flag.
   Costs: the rule set is ours to maintain; it covers the credential shapes
   we know about rather than every shape any tool has ever seen.
   Risks: a novel credential format would not be detected. Mitigation — the
   rule set is small and explicit, and the `.gitleaks.toml` configuration
   records the same allowlist for the advisory `gitleaks` hook.
2. **gitleaks in git mode with `--redact` (selected as the advisory
   companion)** — benefits: a mature, wide rule set and a native git-history
   mode. Costs: an external binary that must be installed and pinned, which
   makes the required check depend on a download that may fail; its rule set
   cannot be reconciled automatically with ours. Risks: a tool that cannot be
   installed in the CI image is a check that could not run, and a check that
   could not run must fail the gate. Mitigation — `gitleaks` runs in the
   advisory pre-commit hook, never as a required check.
3. **trufflehog** — benefits: verifies credentials against the issuing
   provider rather than only by shape. Costs: network access to the provider,
   which the required checks must not have; and it is Apache-2.0 licensed
   while its git-history mode shells out to external services. Risks: an
   active credential check that calls the provider is itself an outbound
   request from the build, which is exactly the shape of attack the checks are
   supposed to prevent.
4. **detect-secrets** — benefits: a baseline-file model that records which
   findings are known. Costs: an Apache-2.0 baseline that must be reviewed and
   updated on every change, so the baseline itself becomes a source of false
   negatives; it is a Python package with a dependency footprint that would
   have to be maintained. Risks: the baseline grows until it silently accepts
   everything.

## Decision

The repository uses a **repository-native scanner** as the required
`secret-scan` check, and **gitleaks** as an advisory pre-commit hook.

- `ci/secret_scan.py` scans the tracked tree and every commit in the
  version-controlled history.
- Every finding is redacted: the `secret` and `match` fields are replaced
  before anything is printed, in human-readable and JSON output alike
  (Constitution Article X.3).
- `.gitleaks.toml` records the repository's placeholder allowlist so that the
  advisory hook and the required check agree on what a placeholder is.
- The remediation path is **rotate first**. The contributor guide states the
  procedure: confirm the finding, rotate the credential at the issuer, record
  the incident, remove the material, decide about history rewriting only when
  rotation alone is insufficient, and re-run the check.

## Consequences

- Positive: the required check has no external dependency, cannot fail for an
  environmental reason, and never prints a secret.
- Negative: the rule set is narrower than gitleaks'.
- Risks and mitigations: a missed credential shape. Mitigation — gitleaks runs
  in the advisory hook, and the rotate-first procedure limits the impact of a
  missed detection to the window between commit and discovery.

## Follow-up actions

- [x] Implement `ci/secret_scan.py` with redaction and history scanning.
- [x] Publish the rotate-first runbook in `CONTRIBUTING.md`.

## Revisit triggers

- The rule set fails to detect a credential that was committed.
- gitleaks becomes installable from a pinned, checksummed source in the CI
  image, making it viable as the required check.
- A provider-side revocation mechanism becomes reliable enough to make
  active verification safe to run.
