# Attribution

The Helm chart and compose template were extracted from
[contract-compliance-reviewer](https://github.com/sssanjithrajesh/contract-compliance-reviewer)
(`deploy/helm/ccr`, `docker-compose.yml`). The eval gate shape is the same idea used in
`legacy-test-writer` and `support-ops-agent`: a committed results JSON and a floor file CI
refuses to drop below.

No third-party eval SaaS. promptfoo's assertion style (path + operator + expected) is the
inspiration; the implementation here is original and has no runtime dependency on promptfoo.
