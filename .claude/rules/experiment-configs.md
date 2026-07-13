# Rule: Experiment configs (`configs/**.yaml`)

- Configs are YAML, validated by `graphroute_ts.config.ExperimentConfig`
  (`extra = "forbid"` — unknown keys are errors, not ignored).
- Every experiment config declares: `name`, `seed`, `data` (dataset, freq, target),
  and `split` (`train_end`, `val_end`, `horizon`). Splits are chronological.
- One config = one reproducible run definition. Do not hardcode hyperparameters in
  code that belong in a config.
- Changing a config for a new experiment means a new file / new `name`, not silently
  mutating an existing one whose results are already recorded.
- Never embed secrets, tokens, absolute machine paths, or dataset contents in configs.
- The config file used is recorded in every experiment's run record (repro rule 10).
