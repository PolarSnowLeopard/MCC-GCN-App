# Fine-tuning

When the built-in models do not adequately capture the characteristics of your chemical system, you can **fine-tune** a base model on your own labelled dataset to produce a domain-specific predictor.

::: tip Navigation
Select **Fine-tuning** in the sidebar.
:::

## What fine-tuning does

You supply a CSV of molecule pairs with known classifications. The platform:

1. Loads the selected **base model** weights;
2. Freezes the earlier graph convolution layers and re-trains only the final dense layers;
3. Saves the checkpoint that maximises **balanced validation accuracy**;
4. Registers a new model in your account with **Draft** status.

A draft model is visible only to you. After evaluation, you can [publish](#publishing) it to make it accessible to other users.

## Page layout

The page is split into two columns:

- **Left** — *Fine-tune Configuration* form
- **Right** — *Fine-tune Tasks* list (your current and past jobs)

## Step 1 — Prepare training data

The form expects a CSV with three columns:

```csv
api_smiles,coformer_smiles,label
CCO,O=C(O)c1ccccc1O,2
c1ccccc1,CC(=O)O,0
```

Label encoding:

| Value | Class |
| :---: | --- |
| `0` | Negative |
| `1` | Salt |
| `2` | Cocrystal |
| `3` | Solvate |

::: tip
Click **Download Template** next to the upload area for a ready-to-use starter CSV.
:::

::: warning Minimum data requirements
The training pipeline requires **at least 2 rows** where both SMILES parse successfully and the label is a valid integer in `{0, 1, 2, 3}`. For meaningful transfer learning, plan for **dozens to hundreds** of labelled pairs with reasonable class balance.
:::

## Step 2 — Configure and submit

Complete the form on the left:

| Field | Description |
| --- | --- |
| **Base Model** | The model to initialise from. The built-in **MCC-GCN Pretrained v1** is the standard choice. |
| **Task Name** | A descriptive identifier (e.g. `api-screening-2026-04`). The resulting model file inherits this name. |
| **Training Data** | Upload your CSV via drag-and-drop or file picker. |

#### Advanced parameters

Expand the **Advanced Parameters** section to reveal additional controls. The defaults are well-tuned for most scenarios — modify only with justification.

| Parameter | Default | Effect |
| --- | --- | --- |
| **Epochs** | `50` | Number of full passes over the training data |
| **Batch Size** | `16` | Samples per gradient update |
| **Learning Rate** | `0.0003` | Optimiser step size |

Other parameters (`weight_decay`, `train_layers`) use safe defaults. Consult your administrator if you need to adjust them.

Click **Submit Fine-tune Task** to enqueue the job.

## Step 3 — Monitor progress

The submitted task appears at the top of the right panel. Click a row to expand its detail view:

| Status | Description |
| --- | --- |
| **Queued** | Waiting for the Celery worker |
| **Running** | Training is in progress; the per-epoch log streams once the first epoch completes |
| **Completed** | Training finished; best validation metrics and action buttons are shown |
| **Failed** | An error occurred; the full traceback is displayed (common causes: malformed CSV, unparseable SMILES) |

::: tip
The task list polls automatically during training. You can also click **Refresh** in the panel header to force an update.
:::

## Step 4 — Evaluate and use the result

When a job completes, the expanded detail view offers two actions.

### Testing

Click **Test Model** to open an inline evaluation dialog:

1. Enter a known API and Coformer SMILES pair.
2. Click **Predict**.
3. Review the four-class probability bars to assess whether the fine-tuned model behaves as expected.

### Publishing

By default, the resulting model has **Draft** status — visible only to you.

To make it available to all users on the platform:

1. Click **Publish Model**.
2. Confirm. The status tag changes from `Draft` to `Published`.

You can also publish later from the [Models](./models) page.

## Reading the training log

Each epoch produces a log line with the following format:

```
Epoch 12/50 | train_loss=0.2517 train_acc=0.8923 | val_loss=0.3104 val_acc=0.8421 val_bacc=0.8055
```

| Metric | Meaning |
| --- | --- |
| `train_loss` / `train_acc` | Cross-entropy loss and accuracy on the training split |
| `val_loss` / `val_acc` | The same metrics on the held-out 20 % validation split |
| `val_bacc` | Balanced validation accuracy — the checkpoint-selection criterion |

A healthy training run shows `val_bacc` rising over the first several epochs and then plateauing. If `train_acc` continues to increase while `val_acc` declines, the model is overfitting. Reduce the number of epochs or increase the dataset size.

## Next

- Manage your models: [Model Management](./models).
- Use the new model for inference: [Single Prediction](./predict) or [Batch Screening](./batch).
- Review a past training run: [History](./history).
