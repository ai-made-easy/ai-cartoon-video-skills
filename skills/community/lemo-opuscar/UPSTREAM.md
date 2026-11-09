# Upstream: lemo-opuscar

- **Repository:** https://github.com/lemomo-ai/lemo-opuscar
- **Vendored commit:** `143f387ad774525dc9abc0ff05fb5f4bfbaa5f02` (2026-11-08)
- **License:** MIT for the code, CC BY 4.0 for the film styles and demo material. The MIT text is in `LICENSE`.
- **Vendored here:** the thin plugin skill from `plugin/skills/lemo-opuscar/` (`SKILL.md` and
  `scripts/setup.sh`) plus the upstream MIT licence.
- **Not vendored:** the Lemo-Opuscar library itself (about 191 MB). At runtime, `scripts/setup.sh`
  clones or updates it into `~/lemo-opuscar` by default, then the skill reads that library's own
  `AGENTS.md` and follows its workflow.
- **Requirements:** Node, ffmpeg and Python for the library's tools. On first use, `setup.sh deps`
  installs the core tools; a film may need extra packages named in its `STYLE.md`.

This is a third-party skill. Issues with the skill itself belong upstream; issues with packaging or
installation belong in this repository.
