# Batch Screening

Use **Batch Screening** when you want to test more than a few pairs at once. The platform queues the job, runs it in the background, and shows the full table when it's done.

::: tip Reach the page
Click 📊 **Batch Screening** in the sidebar.
:::

## When to use which

| Workflow | Best for |
| --- | --- |
| [Single Prediction](./predict) | One pair, immediate result, screenshot-able |
| **Batch Screening** | Anything from a handful to thousands of pairs from a CSV |

## Workflow

### 1. Pick a model

Same dropdown as on the Prediction page — every visible model is selectable. Built-in `MCC-GCN v1` is the recommended default.

### 2. Choose the input mode

The page has two input modes, switched via the segmented control under **Data Input**:

- **Text Input** — paste pairs one per line.
- **Upload CSV** — upload a `.csv` file.

#### Text Input

Paste molecule pairs into the textarea. Each line:

```
api_smiles,coformer_smiles
```

For example:

```
CCO,O=C(O)c1ccccc1O
O=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]
```

Empty lines and lines without exactly two SMILES are silently dropped.

#### Upload CSV

Click the dashed drop zone and pick a file, or drag-drop one in.

The CSV format:

```csv
api_smiles,coformer_smiles
CCO,O=C(O)c1ccccc1O
O=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]
```

- Header row is **optional** — if the first line contains the word `smiles`, it is skipped.
- Two columns: `api_smiles`, `coformer_smiles`.

::: tip Don't have a CSV yet?
Click the dashed **Download Template** button next to the upload area to grab a working starter file with two example rows.
:::

### 3. Submit

Click **Start Screening**.

- The form validates that you picked a model and provided ≥1 valid pair.
- On submission you'll see *"Batch task submitted. Check history for results."* — the task is now in the Celery queue.

### 4. Watch progress

A progress card appears showing one of two states:

| Status | Meaning |
| --- | --- |
| **Queued** | The Celery worker hasn't picked up your task yet (usually <1 s in light load). |
| **Running** | Predictions are streaming through the model. |

The progress bar is approximate — it grows over time but the only authoritative completion signal is the *"Screening complete"* toast.

::: warning Don't navigate away
Leaving the Batch page cancels the live polling for that submission. The task itself **keeps running** server-side — you can revisit the result via [History](./history) — but the in-page progress card and result table won't reappear automatically.
:::

### 5. Read the results

When the task completes, a results table appears below:

| Column | Meaning |
| --- | --- |
| **#** | Row index (1-based) |
| **API SMILES** | Echoed input (hover for full string) |
| **Coformer SMILES** | Echoed input |
| **Prediction** | Coloured tag — `Negative` (grey) / `Salt` (orange) / `Cocrystal` (green) / `Solvate` (blue) |
| **Confidence** | The max class probability, in % |

Rows are tinted by predicted class for quick scanning.

### 6. Export

Click **Export CSV** in the results card title. You get `batch_results.csv` with columns:

```
API SMILES, Coformer SMILES, Prediction, Label, Confidence
```

## Best practices

- **Sanity-check a few rows in [Single Prediction](./predict) first.** A typo in your CSV header is much cheaper to discover at row 1 than at row 5,000.
- **Mind RDKit-incompatible SMILES.** Any pair where RDKit can't featurize either molecule will show as a row with no prediction — keep the input canonical.
- **Keep batches under ~5,000 pairs per submission.** The pipeline runs CPU-only by default. For very large screens, split into sub-batches and submit sequentially — they all show up under the same [History](./history) page.

## Where to go next

- Need to look at an old run? [History → Batch Prediction](./history).
- Want a model that performs better on your specific chemistry? [Fine-tuning](./finetune).
