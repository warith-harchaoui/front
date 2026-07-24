# Captions & diarization (local AI) — `front-audio`

Draft WebVTT / SRT captions from a local whisper.cpp build, then add who-spoke-when (NeMo Sortformer) and who-is-who (TitaNet, or a transcript rule + a local Ollama pass). Bilingual, local-first, never a SaaS.

This is the human landing page. It points to the three places that hold the
detail — nothing is duplicated here.

- **What it is & what activates it** — [`front-audio/SKILL.md`](../front-audio/SKILL.md)
  (the agent-facing spec: purpose, trigger phrases, full flag surface).
- **Run it** — [`EXAMPLES.md`](../EXAMPLES.md) has a copy-paste recipe for
  `front-audio`.
- **Go deeper** — [`front-audio/references/`](../front-audio/references/): captions, diarization, speaker naming.
