# Rule: Tests (`tests/**.py`)

- Use pytest. Mark tests with the registered markers: `unit`, `integration`,
  `leakage`, `gpu`, `slow`.
- Fast suite (`unit` + `leakage`) must be deterministic, offline, and quick.
  **No network, no dataset downloads, no TSFM checkpoint fetches.**
- `tests/leakage/` is first-class. Every splitting / scaling / retrieval /
  feature-engineering component MUST have a leakage test that *fails* when a
  temporal violation is deliberately introduced.
- A leakage test must assert the violation is caught (raises / returns failure),
  not merely that "normal" input passes.
- GPU-only tests use the `gpu` marker and must skip cleanly when CUDA is absent.
- Seed any randomness explicitly via `graphroute_ts.reproducibility.set_seed`.
- Do not weaken an assertion to make a failing test pass — fix the code or the test's premise.
