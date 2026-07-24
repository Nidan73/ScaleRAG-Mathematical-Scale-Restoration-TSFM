# TS-RAG Official Repository Audit (Phase 11A · Part 1)

**Date:** 2026-07-14
**Auditor:** ScaleRAG-TS team (Claude Code)
**Purpose:** Determine, by direct inspection (not from any secondary/NotebookLM claim),
whether the official TS-RAG protocol can be faithfully reproduced on **ETTm2 only** as a
development dataset, and exactly which files/checkpoints/data are required.

> Scope guard: this audit and everything in Phase 11A touches **ETTm2 only**. ETTh1,
> ETTm1, Weather, Electricity are Phase-11B **final** datasets and are NOT opened here.

---

## 1. Provenance

| Field | Value |
|---|---|
| Repository URL | https://github.com/UConn-DSIS/TS-RAG.git |
| Commit hash (pinned) | `73ac807789d2e61b8a3dfc8514e3fc947fe185cc` |
| Commit date | 2026-04-14 22:21:46 −0400 |
| Commit subject | "Fix Huggingface link in README.md" |
| License | **MIT** (© 2025 UConn DSIS Research Lab) |
| Paper | TS-RAG (NeurIPS 2025), arXiv:2503.07649 |
| Clone location (isolated) | `external/ts-rag/` (LFS smudge disabled at clone; no binaries pulled) |
| Repo size | 22 tracked files, pure source (no data/checkpoints in git) |

Isolation: cloned with `GIT_LFS_SKIP_SMUDGE=1 git clone --no-checkout` then a plain
checkout, so **no** large/binary/pickle artifacts were fetched. The existing GraphRoute-TS
`.venv` (Py 3.11/3.14) is untouched; a **separate** Python 3.9 env will be built for Part 2.

## 2. Declared environment & dependencies

`README.md` → conda env, **Python 3.9**. `requirements.txt` (verbatim):

```
autogluon==1.3.0
chronos-forecasting==1.5.1
faiss_gpu==1.7.2
numpy==1.25.0
wandb==0.19.10
```

**`requirements.txt` is incomplete for the actual import graph.** The following are imported
but not pinned, and are pulled transitively (almost entirely by `autogluon==1.3.0`):
`torch`, `transformers`, `gluonts`, `scikit-learn`, `pandas`, `statsmodels` (STL),
`matplotlib`, `tqdm`, `huggingface_hub`. Concretely:

- `zeroshot.py` **unconditionally** does `from models.moment import MOMENTPipelineWithRetrieval`
  (top-level, line 13) → `models/moment.py` → `from models.utils import ...` →
  `models/utils.py` imports `gluonts.*` and `autogluon.{common,core,timeseries}.*`.
  So **autogluon + gluonts must import even for the Chronos-only path.**
- `models/moment.py` does **not** import `momentfm`; MOMENT is a from-scratch T5 reimpl, so
  there is **no momentfm blocker** (contrary to what a naive read of the model name suggests).
- `data_provider/data_loader.py` imports `statsmodels.tsa.seasonal.STL` at module top.
- The retrieval **embedder** is `amazon/chronos-t5-base` via `chronos.ChronosPipeline`
  (from `chronos-forecasting`), **distinct** from the Chronos-Bolt forecasting backbone.

### faiss compatibility risk (identified blocker → mitigation)
`retrieve.py` does `import faiss` at module top and uses `faiss.IndexFlatL2`. `faiss_gpu==1.7.2`
is a legacy PyPI wheel (CUDA 10/11 era) and will **not** run on this box (RTX 5070 Ti, sm_120,
CUDA 13). **Mitigation:** at eval time with the **cached official retrieval CSV** (see §5),
`do_retrieve` is skipped and FAISS is never *executed* — only *imported*. `faiss-cpu` satisfies
the import (and would only be exercised if we regenerated retrieval, which we will not for the
official reproduction). Substituting `faiss-cpu` for `faiss_gpu` therefore does **not** change
any official-reproduction number; it will be recorded as an explicit, results-neutral deviation.

## 3. Entry point: `script/zeroshot_chronos.sh`

Fixed hyperparameters (identical for all datasets): `seq_len=512`, `pred_len=64`,
`lookback_length=512`, `label_len=0`, `top_k=10`, `augment_mode=moe`, `batch_size=256`,
`dimension=768`, `embedding_model_type=chronos`, `model=ChronosBoltRetrieve`,
`run_file=zeroshot.py`, `retrieval_database_dir='../retrieval_database/'`,
`checkpoint_model_path='./checkpoints/chronos-bolt/best.pth'`. Matches the required protocol
(ctx 512 / horizon 64 / frozen Chronos-Bolt / MSE+MAE). The provided script's default
`datasets="ETTh1"`; for **ETTm2** the branch sets `data=ett_m_retrieve`,
`metadata_frequency='minute'`, `root_path='../datasets/ETT-small/'`,
`retrieve_database_name=metadata_database_name='ETTm2'`, `data_path='ETTm2.csv'`.

> The shipped script runs **only the retrieval model** (`ChronosBoltRetrieve`). The
> **target-only** Chronos-Bolt baseline (`--model ChronosBolt --data ett_m`) is present in
> `zeroshot.py` but **not** wired into any `.sh`; we invoke it directly in Part 2 (§6).

## 4. Call graph (files actually required for an ETTm2 run)

```
script/zeroshot_chronos.sh
└── zeroshot.py                      # arg parsing, model load, retrieval-CSV cache, eval
    ├── models/ChronosBolt.py        # ChronosBoltPipeline (target-only) +
    │   └── models/base.py           #   ChronosBoltModelForForecastingWithRetrieval (ARM)
    │       └── models/utils.py      # gluonts/autogluon imports (import-time dependency)
    ├── models/moment.py             # imported unconditionally; not used on chronos path
    ├── retrieve.py                  # do_retrieve/load_database; import faiss; chronos-t5 embed
    ├── data_provider/data_factory.py
    │   └── data_provider/data_loader.py   # Dataset_ETT_minute[_retrieve], get split borders
    └── utils/{tools.py, metrics.py, timefeatures.py}   # test()/test_retrieve(), MSE/MAE, get_borders
```

Files **not** needed for ETTm2 zero-shot eval: `pretrain.py`, `script/pretrain.sh`,
`script/zeroshot_moment.sh`, `dataset.py`, `images/*`.

## 5. Data & retrieval-DB formats (measured on HF `nkh/TS-RAG-Data`)

The official data/DB is on HF `datasets/nkh/TS-RAG-Data` (also mirrored on the README's Google
Drive). Real file sizes (queried via HF API, **not** downloaded):

| File (ETTm2-relevant in **bold**) | Bytes | Needed for ETTm2? |
|---|---:|---|
| **`database_512/ETTm2_minute_512.pkl`** | 1,528,600,844 (1.53 GB) | **Yes** (pickle → `raw_data` for reconstruction) |
| **`datasets_512/ETTm2_retrieve_ETTm2_512_only_self_train_None.csv`** | 317,999,133 (318 MB) | **Yes** (cached retrieval indices; skips `do_retrieve`) |
| `database_512/ETTm1_minute_512.pkl` | 1,528,600,844 | No (Phase-11B) |
| `database_512/ETTh1_hour_512.pkl` | 372,285,549 | No (Phase-11B) |
| `database_512/electricity_hour_512.pkl` | 26,140,103,187 (26 GB!) | No (Phase-11B) |
| `database_512/weather_10minutes_512.pkl` | 3,459,812,839 | No (Phase-11B) |
| `retrieval_database_512.parquet` | 4,769,752,172 | No (pretrain only) |
| `pretrain_pairs_ctx512/*.parquet` (30 files) | ~17 GB total | No (pretrain only) |

**Retrieval-DB pickle format** (`retrieve.py:create_database`): a `dict` keyed by variable
name; each value = `{'raw_data': list[float] (full series), 'timestamps': np.ndarray,
'embeddings': np.ndarray (n_windows × 768, chronos-t5 EOS embeddings), 'metadata': {...}}`.
File naming: `{dataset}_{frequency}_{lookback}.pkl` → **`ETTm2_minute_512.pkl`**.

**Cached retrieval CSV** (`do_retrieve` output): the original ETTm2 columns (`date` + 7 vars)
concatenated with `boundary_idx_{var}_{k}`, `timestamp_idx_{var}_{k}`, `distance_{var}_{k}`
columns (k over top-20 as stored). At eval, `zeroshot.py` reconstructs each retrieved 576-length
window as `retriever_rawdata[feat_id][timestamp_idx : timestamp_idx + seq_len + pred_len]`.

> **Pickle safety:** the `.pkl` files are **untrusted**. They will be downloaded only from the
> official HF repo (over HTTPS, with recorded sha256), inspected for provenance, and loaded
> **only inside the isolated Py-3.9 env**, never in the main GraphRoute-TS environment. A
> manifest with sha256 of every downloaded asset will accompany Part 2.

**Raw `ETTm2.csv`** (7 vars `HUFL,HULL,MUFL,MULL,LUFL,LULL,OT`, 15-min, 69,680 rows) is the
standard ETDataset file. It is embedded inside the retrieve-CSV (`df_ori`), and is also
independently available from the public ETDataset repo (~10 MB) for the target-only baseline.

## 6. Checkpoints (measured; HF-hosted, verifiable)

| Logical name (TS-RAG path) | Source | Bytes | Role |
|---|---|---:|---|
| `./checkpoints/chronos-bolt/best.pth` | HF `nkh/TS-RAG-ChronosBolt/pytorch_model.bin` | 840,404,992 (840 MB) | TS-RAG-trained **full** model (frozen backbone **+ trained ARM**), loaded via `load_state_dict` |
| `./checkpoints/base/` (config + weights) | HF `autogluon/chronos-bolt-base` (`config.json` 1,123 B + `model.safetensors` 821 MB) | ~821 MB | Base architecture/config for `from_pretrained`; the model the ARM was fine-tuned from |
| retrieval embedder | HF `amazon/chronos-t5-base` (`model.safetensors` 805 MB) | ~805 MB | 768-d embeddings; **only if regenerating retrieval** — not needed when using the cached CSV |

`nkh/TS-RAG-ChronosBolt` card: Apache-2.0, `base_model: autogluon/chronos-bolt-base`
(finetune), metrics mae/mse, lastModified 2025-12-03. 840 MB ≈ 210M fp32 params ≈ chronos-bolt-
base backbone (~205M) + small ARM heads, consistent with `best.pth` = full trained model.

**Target-only baseline provenance (open item for Part 2):** `zeroshot.py`'s `ChronosBolt`
branch loads `pretrained_model_path` (default `./checkpoints/base`) then overwrites with
`pretrained_model_path + 'autogluon_model.pth'`. The string concat implies the intended flag is
`--pretrained_model_path ./checkpoints/base/` (trailing slash) → `./checkpoints/base/autogluon_model.pth`.
`autogluon/chronos-bolt-base` ships `model.safetensors`, **not** `autogluon_model.pth`; the
`.pth` copy is expected to come from the Google-Drive `checkpoints/base/` folder. Part 2 will
first inspect the Drive `checkpoints/base/` contents and compare against vanilla
`autogluon/chronos-bolt-base` to decide the faithful target-only source (documented, not guessed).

## 7. Splits, metrics, and leakage posture (from source)

- **Split (ETTm, `get_borders` / `Dataset_ETT_minute[_retrieve]`)**, seq_len=512:
  train `[0, 34560)`, val `[34560−512, 46080)`, test `[46080−512, 57600)`
  (12/4/4 months at 15-min → ×4). **Test-only** is loaded for evaluation.
- **Scaler:** dataset `StandardScaler` is fit on **train only** (`[border1s[0]:border2s[0]]`) and
  applied to all splits — train-only fit ✓ (rule 5 compliant for the query/target path).
- **Metric:** `utils/metrics.metric` → `MSE = mean((pred−true)²)`, `MAE = mean(|pred−true|)`,
  averaged over **all** (window × horizon × channel) elements in the **normalized** space
  (standard Time-Series-Library ETT convention). This is the required MSE/MAE.
- **Retrieval leakage posture (official):** the FAISS index is built over embeddings sliced to
  `[border1s[0] : border2s[0]]` (**training region**), and retrieval is performed **only** for
  windows whose context end exceeds `border2s[0]` (test region). Query origins are in test;
  retrieved contexts/continuations lie in train (⇒ `candidate_end + H < origin`, no test-future
  leakage — consistent with ScaleRAG rule 3).
  - *Two hygiene nuances to preserve/report faithfully (do NOT "fix" official code — rule 9):*
    (a) the index slice uses window-**start** indices `< 34560`, so a retrieved window can *end*
    up to ~35k (a sliver of validation), and the reconstructed 576-length continuation can reach
    ~35.1k — still strictly before any test origin. (b) `zeroshot.py` fits the *retrieved-sequence*
    `StandardScaler` on the **full** series `raw_data` (train+val+test) — a global-normalization-
    statistic touch on retrieval scale (largely washed out by the model's per-window InstanceNorm).
    ScaleRAG's own retriever (Part 3) will instead use **train-only** scale statistics and a
    **strictly train-only** candidate pool (rule 5), and we will report the contrast.

## 8. Mechanism summary (what "official TS-RAG" does at eval, augment=moe)

For each test window: (1) look up top-k precomputed retrieval indices from the cached CSV;
(2) reconstruct k candidate 576-length sequences from `raw_data`; (3) the model **InstanceNorm-
normalizes** context and each retrieved window by their **own** per-window mean/std; (4) splits
each retrieved window into `(retrieved_x[512], retrieved_y[64])`; (5) `augment=moe`: MLP-encode
each `retrieved_y`, run multihead self-attention over `[decoder_output, k×encoded_y]`, softmax-
gate-fuse, skip-connect into the decoder output; (6) the fused representation goes through the
output head → quantile preds; central (0.5) quantile is the point forecast; (7) InstanceNorm-
inverse to restore scale. The ARM (encode_mlp / mha / ffn / gate) is **trained** (in `best.pth`).

**Contrast with ScaleRAG's thesis:** TS-RAG handles scale via per-window InstanceNorm and a
*learned* attention gate. ScaleRAG instead does **explicit candidate→query scale restoration**
(non-neural) and a fixed convex fusion. Part 3 tests whether that explicit restoration transfers
to this benchmark regime.

## 9. Required-file manifest for the ETTm2 run (final)

Target-only baseline (`chronos_bolt_target`):
- `datasets/ETT-small/ETTm2.csv` (raw; public ETDataset or derived from retrieve-CSV `df_ori`)
- `checkpoints/base/` (config.json + weights) **and** the target-only weight file (Part-2 §6 item)

Official TS-RAG (`tsrag_official`, augment=moe, top_k=10):
- `datasets/ETT-small/ETTm2_retrieve_ETTm2_512_only_self_train_None.csv` (318 MB, cached indices)
- `retrieval_database/ETTm2_minute_512.pkl` (1.53 GB, for `raw_data` reconstruction)
- `checkpoints/base/` (config for `from_pretrained`) + `checkpoints/chronos-bolt/best.pth` (840 MB)
- `faiss-cpu` (import only; not executed when the cached CSV is present)

**Total download for ETTm2 dev ≈ 3.1 GB** (best.pth 840 MB + base 821 MB + pickle 1.53 GB +
retrieve-CSV 318 MB; chronos-t5-base 805 MB only if we ever regenerate retrieval). Disk free: 721 GB.

## 10. Reproducibility verdict (Part 1)

**No hard blocker to reproduction identified.** Everything needed for an ETTm2 run is publicly
available and directly inspectable. Two engineering items are handled without changing any
official number: (i) `faiss_gpu → faiss-cpu` substitution (import-only, cached retrieval); (ii)
Python-3.9 + `autogluon==1.3.0` isolated env (heavy but standard). One reproduction-fidelity item
(target-only checkpoint provenance, §6) is deferred to Part-2 setup and will be resolved by
inspection, not assumption. Proceeding to Part 2 (isolated env build + ETTm2-only downloads +
official reproduction) is warranted.
