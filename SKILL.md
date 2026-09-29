---
name: shared-eval-and-deploy
description: Run the shared eval gate and check the compose / Helm deploy templates.
---

```
uv sync --extra dev
uv run pytest
uv run seval compose
uv run seval chart          # needs helm on PATH
uv run seval gate --summary examples/summaries/legacy-test-writer.json --gate examples/gates/legacy-test-writer.yaml
```

Do not raise a floor in `examples/gates/` to make a run green. Change the project, then update the summary.
