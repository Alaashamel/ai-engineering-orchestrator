# Eval Report: Mock Controller Sweep v1

- **Model:** gpt-4o (mock)
- **Provider:** deterministic-mock
- **Timestamp:** 2026-08-28T19:05:34.792636+00:00
- **Total tests:** 10
- **Passed:** 10
- **Failed:** 0
- **Pass rate:** 100.0%
- **Avg latency:** 55.9ms
- **Total cost:** $0.000000
- **Total tokens:** 0

## Per-Test Results

| Test | Status | Score | Latency (ms) | Tokens | Cost |
|------|--------|-------|--------------|--------|------|
| todos_auth_fastapi | ✓ | 1.0 | 41.6 | 0 | $0.000000 |
| notes_public_noauth | ✓ | 1.0 | 49.04 | 0 | $0.000000 |
| products_catalog_backend | ✓ | 1.0 | 64.21 | 0 | $0.000000 |
| blog_posts_frontend | ✓ | 1.0 | 61.11 | 0 | $0.000000 |
| task_board_fullstack | ✓ | 1.0 | 54.61 | 0 | $0.000000 |
| inventory_items_noauth | ✓ | 1.0 | 40.96 | 0 | $0.000000 |
| orders_public_fallback | ✓ | 1.0 | 38.39 | 0 | $0.000000 |
| notes_no_security_gate | ✓ | 1.0 | 39.31 | 0 | $0.000000 |
| todos_api_ui | ✓ | 1.0 | 111.04 | 0 | $0.000000 |
| products_admin_auth | ✓ | 1.0 | 58.57 | 0 | $0.000000 |

## Appendix: determinism

Ran `todos_auth_fastapi` twice through the pipeline with the identical mock provider and compared SHA-256 hashes of every generated file. Result: **byte-identical**.

## Appendix: honesty notes

- Mode is `mock`: the provider returns deterministic template content, so `cost=$0.00`, `tokens=0`, and latency reflects mock execution, not a real LLM.
- Real mode is blocked (API key holds no quota; every real call returns HTTP 429) — no warm-start or real-LLM numbers were attempted for this sweep.
- `tests` are generated unconditionally by the mock controller for every case; prompts that asked to skip a quality gate still yield a test file.
- The `orders_public_fallback` case exercises resource-model fallback: 'orders' is not in the mock's resource vocabulary, so the controller falls back to the default `Item`/`items` model/table.
- Generated-test failures can carry framework warnings (PyJWT key-length, Starlette deprecation) that are non-fatal and do not fail the suite.
