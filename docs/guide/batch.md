# Batch Screening

**Batch Screening** is designed for evaluating large numbers of molecule pairs in a single submission. The platform queues the job, processes it asynchronously via a Celery worker, and presents the full results table upon completion.

::: tip Navigation
Select **Batch Screening** in the sidebar.
:::

## Choosing the right workflow

| Workflow | Best suited for |
| --- | --- |
| [Single Prediction](./predict) | One pair; immediate, interactive result |
| **Batch Screening** | Tens to thousands of pairs supplied as CSV or pasted text |

## Workflow

### 1. Select a model

The model dropdown is shared with the Prediction page. All models visible to your account are listed. Select the model whose training stage and data type match the intended evaluation.

### 2. Provide the input data

A segmented control beneath **Data Input** offers two modes:

#### Text input

Paste molecule pairs directly into the text area, one pair per line:

```
api_smiles,coformer_smiles
```

Example:

```
CCO,O=C(O)c1ccccc1O
O=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]
```

Empty lines and lines that do not contain exactly two comma-separated SMILES strings are silently discarded.

#### CSV upload

Click or drag-drop a `.csv` file into the upload area.

Required format:

```csv
api_smiles,coformer_smiles
CCO,O=C(O)c1ccccc1O
O=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]
```

- **Header row**: optional. If the first line contains the word `smiles` (case-insensitive), it is treated as a header and skipped.
- **Columns**: exactly two — `api_smiles` and `coformer_smiles`.
- **Encoding**: UTF-8.

::: tip
Click **Download Template** next to the upload area to obtain a ready-to-use starter file with two example rows.
:::

### 3. Submit

Click **Start Screening**.

- The form validates that a model has been selected and that at least one valid pair has been provided.
- On acceptance, a confirmation toast appears: *"Batch task submitted. Check history for results."*

### 4. Monitor progress

A progress card is displayed with one of the following states:

| Status | Meaning |
| --- | --- |
| **Queued** | The task is waiting for the Celery worker (typically less than one second under normal load) |
| **Running** | Inference is in progress |

::: warning
Navigating away from the Batch Screening page stops the in-page progress polling. The task itself **continues to run** on the server. To view results after navigation, go to [History](./history).
:::

### 5. Review results

When the task completes, a results table appears:

| Column | Description |
| --- | --- |
| **#** | Row index (1-based) |
| **API SMILES** | Input echo (hover for full string) |
| **Coformer SMILES** | Input echo |
| **Prediction** | Colour-coded tag: `Negative` (grey), `Salt` (amber), `Cocrystal` (green), `Solvate` (blue) |
| **Confidence** | Maximum class probability, expressed as a percentage |

Rows are lightly tinted by predicted class for rapid visual scanning.

### 6. Export

Click **Export CSV** in the results card header. The downloaded `batch_results.csv` contains:

```
API SMILES, Coformer SMILES, Prediction, Label, Confidence
```

## Best practices

- **Validate a small sample first.** Run a few representative pairs through [Single Prediction](./predict) before submitting a large CSV. A header typo is cheaper to discover at row 1 than at row 5,000.
- **Use canonical SMILES.** Pairs where RDKit cannot parse either molecule produce empty result rows. Canonical SMILES from PubChem are accepted with near-certainty.
- **Keep submissions under approximately 5,000 pairs.** The default pipeline uses CPU-only inference. For larger screens, split the input into sequential submissions — all results appear under the same [History](./history) page.

## Next

- Review a past screening run: [History](./history).
- Train a model tuned to your chemical domain: [Fine-tuning](./finetune).
