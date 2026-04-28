# Fine-tuning

If the built-in models aren't quite right for your chemistry, you can **fine-tune** one of them on your own labelled data and get a private model back.

::: tip Reach the page
Click 🎯 **Fine-tuning** in the sidebar.
:::

## What "fine-tuning" means here

You provide a CSV of molecule pairs you've already classified (positive / negative / salt / etc.). The platform:

1. Loads the **base model** weights you choose;
2. Continues training only the last few dense layers;
3. Saves the weights with the best validation performance;
4. Registers a new model in your account as **Draft**.

Once it's a draft, it's only visible to you. You can [test it](#testing-the-result), then [publish](#publishing-the-result) it to make it visible to others.

## Page anatomy

Two columns:

- **Left** — *Fine-tune Configuration* form (your job submission)
- **Right** — *Fine-tune Tasks* (your past and ongoing fine-tune runs)

## Step 1 — Prepare your training data

The form expects a CSV with **three columns**:

```csv
api_smiles,coformer_smiles,label
CCO,O=C(O)c1ccccc1O,2
c1ccccc1,CC(=O)O,0
...
```

Label values:

| Value | Class |
| --- | --- |
| `0` | `Negative` |
| `1` | `Salt` |
| `2` | `Cocrystal` |
| `3` | `Solvate` |

::: tip Don't have a template?
Click **Download Template** next to the upload area for a starter CSV.
:::

::: warning Minimum requirements
The training pipeline requires **at least 2 valid rows** (rows where both SMILES parse and the label is a valid integer). Anything fewer fails with `Need at least 2 valid training samples`.
For meaningful fine-tuning, plan for **dozens to hundreds** of rows, with reasonable class balance.
:::

## Step 2 — Submit a job

Fill in the form on the left:

| Field | What to enter |
| --- | --- |
| **Base Model** | Pick a model to start from. The built-in **`MCC-GCN Pretrained v1`** is the standard choice. |
| **Task Name** | Anything memorable, e.g. `aspirin-derivatives-2026-04`. The resulting model file will be named after it. |
| **Training Data** | Upload your CSV (drag-drop or click). |

### Advanced parameters

Click **Advanced Parameters** to expand. Defaults are sensible — only change them if you know why.

| Parameter | Default | What it does |
| --- | --- | --- |
| **Epochs** | `50` | How many passes over your data. Higher = more fitting, but also more risk of overfitting. |
| **Batch Size** | `16` | Samples per gradient step. Lower works for tiny datasets. |
| **Learning Rate** | `0.0003` | Step size of the optimizer. The default is well-tuned for most cases. |

Other knobs (`weight_decay`, `train_layers` — how many dense layers to unfreeze) use safe defaults. Reach out to your administrator if you need to tune them.

Click **Submit Fine-tune Task**.

## Step 3 — Watch progress

The submitted job appears at the top of the **right** panel.

Click a row to expand its detail. You'll see one of:

| Status | What's happening |
| --- | --- |
| **Queued** | The Celery worker hasn't started yet. |
| **Running** | The model is training. The training log streams as soon as the first epoch finishes. |
| **Completed** | Training finished. Best validation balanced accuracy and the per-epoch log are shown. Action buttons appear. |
| **Failed** | Something went wrong. The full traceback is in the error block — most often a malformed CSV or an unparseable SMILES. |

::: tip Refresh
The right panel polls automatically while a task is running, but you can also click **Refresh** in the top-right of the panel to force-refresh the list.
:::

## Step 4 — Use the result

When a job completes, expanding it shows two action buttons.

### Testing the result

Click **Test Model**. A dialog opens with two SMILES inputs.

1. Enter a known-good API and Coformer SMILES.
2. Click **Predict**.
3. The dialog shows the four-class probability bars. Use this to sanity-check the fine-tuned model before publishing.

### Publishing the result

By default, the resulting model is **Draft** — only you can see and use it.

To make it usable by other users on the platform:

1. Click **Publish Model**.
2. Confirm. The badge flips from `Draft` to `Published`.

You can also publish from the [Models page](./models) later.

## Reading the training log

The log is a per-epoch line of the form:

```
Epoch 12/50 | train_loss=0.2517 train_acc=0.8923 | val_loss=0.3104 val_acc=0.8421 val_bacc=0.8055
```

| Metric | Meaning |
| --- | --- |
| `train_loss` / `train_acc` | Cross-entropy loss / accuracy on the training split |
| `val_loss` / `val_acc` | Same, on the held-out 20% validation split |
| `val_bacc` | **Balanced** validation accuracy — the platform saves the checkpoint that maximizes this value |

Reasonable runs show `val_bacc` climbing for the first several epochs and plateauing. If `train_acc` keeps climbing while `val_acc` drops, you are overfitting — try fewer epochs or a larger dataset.

## Where to go next

- See where your new model lives: [Model Management](./models).
- Use the new model to predict more pairs: [Single Prediction](./predict) or [Batch Screening](./batch).
- Need to revisit a past run? [History](./history) → *Fine-tune Tasks* tab.
