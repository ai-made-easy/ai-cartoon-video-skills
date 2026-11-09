# Upstream: gbro-collage-broll

- **Repository:** https://github.com/pyang5166/gbro-collage-broll
- **Vendored commit:** `a1a4ee2e2abf7d44e460026b706d0c72c2cf8a91` (2026-07-15)
- **License:** MIT, copyright (c) 2026 狗哥笔记. The full text is in `LICENSE`.
- **Vendored here:** `SKILL.md`, `scripts/`, `agents/openai.yaml`, `evals/evals.json`, `README.md`, `LICENSE`.
- **Not vendored:** `assets/` (demo GIFs, about 6.7 MB) so this repository stays small.
- **Language:** the skill is written in Chinese. Keep it as-is; translating it would drift from upstream.
- **Requirements:** a Codex environment with the built-in `image_gen` tool (Gate 2), `GEMINI_API_KEY`,
  Python 3.10 or newer, `google-genai >= 2.10.0`, and `ffmpeg` / `ffprobe`. The first run calls
  `scripts/check_setup.sh` and prints only the missing pieces.

This is a third-party skill. Issues with the skill itself belong upstream; issues with packaging or
installation belong in this repository.
