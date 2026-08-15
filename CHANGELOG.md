# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Bilingual MkDocs documentation site (EN/中文) published to GitHub Pages and ReadTheDocs; eval
  section and docs links added to README; developer artifacts excluded from the site build.

## [0.2.0] - 2026-08-15

### Added

- Source-checkout verification: `scripts/doctor.py` and `scripts/run_acceptance.py`
  forwarders reliably resolve a nested or sibling `cloudQuant/backtrader` checkout, honor
  explicit `--target`/`--repository` overrides, and return structured
  `SOURCE_CHECKOUT_NOT_FOUND` / `BACKTRADER_SOURCE_MISMATCH` codes instead of guessing.
- Approval-token concurrency: a single token is protected across local processes; exactly
  one claim or consume wins, a failed claim leaves the token `ISSUED`, and lock timeouts
  map to `APPROVAL_LOCK_TIMEOUT` (`filelock` declared as a dependency).
- Manifest-tool safety: `scripts/build_manifest.py --check` and `--help` are read-only and
  never modify `manifest.json`; the read-only check is wired into CI.
- Comparison-contract typing: complete key sets for metrics and events comparison results
  with a recomputable `comparison_hash`, plus a `mypy src/backtrader_skills` CI gate.
- Supported-Python CI matrix: a quality job on 3.11 and a pytest matrix across Python
  3.10–3.13 with the correct extras per job.
- Clean-wheel dependency isolation: acceptance installs the built wheel with
  `--ignore-installed --target` and probes `filelock` under `python -I -S` inside the
  install root, proving the distribution does not borrow host site-packages.
- Published acceptance evidence: the full 7×2 matrix result is refreshed through the public
  forwarder and packaged, with historical baselines clearly labeled as such.
- Portable dependency evidence: published evidence records the `filelock` origin and a
  relative `module_path` that contains no absolute paths or `..` components.
- Clean-wheel installer smoke: an isolated `python -I -S` subprocess completes a Codex
  preview → approve → apply cycle from the clean wheel, installing all three canonical
  skills.
- Validation-report integrity: `apply` rejects a tampered validation report with
  `IntegrityError` before claiming the token, leaving the token `ISSUED` and writing no
  target files.
- cloudQuant provenance hardening: URL normalization, Git-remote and PEP 610 verification,
  missing-package installation, `BACKTRADER_SOURCE_WARNING` for unverifiable installed
  packages, and `BACKTRADER_INSTALL_FAILED` with a sanitized diagnostic.
- Skill grounding: the three canonical skills ship complete reference contracts,
  diagnostic catalogs, worked examples, failure playbooks, and pipeline handoffs,
  drift-locked to runtime facts by tests.
- CI: a master-only full-acceptance workflow checks out the cloudQuant Backtrader fork,
  runs the full suite with an 80% coverage gate over `src/backtrader_skills`, then runs
  the complete 7×2 acceptance matrix; pull requests keep the lighter quality and
  supported-Python jobs.
- Evals: a golden-prompt skill eval suite (seven archetype prompts plus adversarial and
  cross-skill prompts) with a mechanical scorer (`scripts/record_eval.py`) and a runbook.
- Repo hygiene: added `CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md`, and `docs/roadmap.md`;
  the README now links the maintainer docs and states the SemVer policy.
