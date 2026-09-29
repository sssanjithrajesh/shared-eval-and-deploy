# Write-up

The brief was: extract the eval harness and the deploy template after a second project
needed them. Three projects needed them. This is the extract.

## Eval

promptfoo and DeepEval both want an API key or a large Node install to be useful. The
thing every repo here actually ran in CI was smaller: a committed JSON and a floor file.
`seval.gate` is that, with dotted paths so a new project does not write a fourth
`check_gate`. Operators are `gte`, `lte`, `eq`, `neq`, `exists`. That is enough to express
"unsafe auto-send stays 0" and "1.5 still fails to compile."

The three example gates are copies of the floors already enforced in those repos. If a
number here is higher than the source repo, that is a bug in this extract, not a tighter
standard.

## Deploy

`docker compose up --wait` is a no-op unless every dependency has a healthcheck and
`condition: service_healthy`. The checker refuses a list-shaped `depends_on`. The template
waits on Postgres before the app, and on the app before the worker.

The chart is the CCR chart with the customer-specific names stripped. `offline: true`
drops the integration Secret and port 443 from the NetworkPolicy. A rendered-manifest
check fails if an offline render still has 443. That is the air-gapped flag the brief
asked for.

kind + chart-testing would install the chart in CI. This repo lints and renders instead:
no cluster, same assertions, runs on a laptop without Docker. The `ct.yaml` is there for
when someone adds the cluster job.

## What I would not do

I would not rewrite the three projects to import this package in the same week. They
already gate themselves. The next project should depend on `seval` from day one.
