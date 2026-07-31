# Model Management

The **Models** page serves as the central model library. Every weight file available for prediction — built-in, fine-tuned, or externally uploaded — is listed here.

::: tip Navigation
Select **Models** in the sidebar.
:::

## Built-in models

| Name | Purpose |
| --- | --- |
| `MCC-GCN 4-Class Pretrain v2` | Four-class model trained on the pretraining dataset |
| `MCC-GCN 4-Class Finetune Exp+Minoxidil v1` | Four-class model fine-tuned on experimental and Minoxidil data |

## Model cards

Each model is presented as a card displaying:

| Element | Description |
| --- | --- |
| **Letter badge** | `P` (Pretrained) or `F` (Fine-tuned), colour-coded |
| **Name and description** | Free-text metadata set at creation time |
| **Type** | `Pretrained` or `Fine-tuned` |
| **Number of classes** | Output dimension of the model (default: 4) |
| **Status** | `Built-in` (grey) · `Draft` (amber, dashed border) · `Published` (green) |
| **Created date** | Timestamp |
| **Actions** | **Publish** and/or **Delete**, when applicable |

## Visibility rules

A model is visible to a user if **any** of the following conditions holds:

- The model belongs to that user.
- The model is **built-in**.
- The model has been **published**.

Implications:

- Your *Draft* fine-tuned models are private until you publish them.
- Other users' drafts are never visible to you.
- Built-in models are visible to all users.

## Common operations

### Uploading a model

If you have an externally trained `.pt` or `.pth` weight file that is compatible with the project's `GCNNet` architecture:

1. Click **Upload Model** (upper-right corner).
2. Complete the form:

| Field | Notes |
| --- | --- |
| **Model Name** | Required |
| **Description** | Optional |
| **Model Type** | `Pretrained` or `Fine-tuned` (required) |
| **Number of Classes** | Must match the model's output dimension; default `4` |
| **Model File** | `.pt` or `.pth` file (drag-and-drop or file picker) |

3. Click **Upload**.

The new model appears with **Draft** status, visible only to you.

::: warning State-dict format required
The platform expects a PyTorch **state dict** — the output of `torch.save(model.state_dict(), path)`. Files saved with `torch.save(model, path)` (which serialise the entire object) will fail at load time. The state dict must be compatible with the project's `GCNNet` architecture (see [`backend/mcc_gcn/models/gcn.py`](https://github.com/PolarSnowLeopard/MCC-GCN-App/blob/main/backend/mcc_gcn/models/gcn.py)).
:::

### Publishing a model

To make a draft model accessible to all platform users:

1. Locate the model card.
2. Click **Publish**.
3. The status changes from `Draft` to `Published`.

::: info
Publishing is a one-way operation in the current version. To revert a published model to draft status, contact your administrator.
:::

### Deleting a model

For your own, non-built-in models:

1. Click **Delete** on the model card.
2. Confirm the action.

::: warning
- **Built-in models cannot be deleted.**
- Deletion permanently removes the weight file from server storage. Prediction results produced by the deleted model remain accessible in [History](./history), but the model can no longer be used for new predictions.
:::

## Empty state

If the model library appears empty, this indicates:

- You have no models of your own, **and**
- No built-in models exist (the administrator has not run the `seed_builtin_model` management command).

Under normal deployment, at least two built-in models should be present. Contact your administrator if they are missing.

## Next

- Use a model immediately: [Single Prediction](./predict).
- Create a new model: [Fine-tuning](./finetune).
