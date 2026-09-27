# Shared Eval and Deploy

**Type:** Cross-cutting library, extracted from `contract-compliance-reviewer` once a second project needs it.

The single eval harness (promptfoo or DeepEval) and the single deployment template (Docker Compose
plus Helm) reused by every project in this portfolio. Its existence is the visible proof of
"codify repeatable deployment patterns."

## Contents (planned)

- `eval/` — case schema, runner, CI regression gate
- `deploy/` — Compose template, Helm chart skeleton, air-gapped flag

## Status

Empty. Do not build here first; build inside the anchor project and extract.
