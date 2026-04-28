# Model Management

The **Models** page is your model library — every weight file you can use anywhere on the platform shows up here.

::: tip Reach the page
Click 📚 **Models** in the sidebar.
:::

## What you see

A grid of cards, one per model. Each card shows:

- A coloured letter badge — `P` for **Pretrained**, `F` for **Fine-tuned**.
- The **model name** and a one-line **description**.
- The **type** (`Pretrained` / `Fine-tuned`) and **number of classes**.
- A **status tag**:
  - `Built-in` (grey) — shipped with the platform, cannot be deleted.
  - `Draft` (orange dashed border) — your own model, only visible to you.
  - `Published` (green) — your own model, visible to other users.
- **Created date**.
- Per-card actions (when applicable): **Publish** and **Delete**.

## Visibility rules

A model is shown to a user if **any** of these is true:

- It belongs to that user;
- It is **built-in**;
- It has been **published**.

That means:

- Your *Draft* fine-tuned models are private to you until you publish them.
- You cannot see other users' drafts.
- Built-in models are visible to everyone.

## Common tasks

### Upload a model

If you have your own pretrained or fine-tuned `.pt` / `.pth` file (e.g. trained externally in PyTorch and following the project's `GCNNet` architecture):

1. Click the **Upload Model** button (top right of the page).
2. Fill the form:
   | Field | Notes |
   | --- | --- |
   | **Model Name** | Required, free-form |
   | **Description** | Optional |
   | **Model Type** | `Pretrained` or `Fine-tuned` — required |
   | **Classes** | Number of output classes the weights are trained for. Default `4`. |
   | **Model File** | The `.pt` / `.pth` weight file (drag-drop or click) |
3. Click **Upload**.

The new card appears as **Draft** and only you see it. Publish it from the card to share.

::: warning State-dict only
The platform expects a **state dict** compatible with the project's `GCNNet` architecture (see [`backend/mcc_gcn/models/gcn.py`](https://github.com/PolarSnowLeopard/MCC-GCN-App/blob/main/backend/mcc_gcn/models/gcn.py)). Files saved with `torch.save(model, ...)` instead of `torch.save(model.state_dict(), ...)` will fail at load time.
:::

### Publish a model

To make a draft model visible to other users on the platform:

1. Find the card.
2. Click the **Publish** action button.
3. The badge flips from `Draft` to `Published`.

Publishing is one-way; if you want to make it private again, contact your administrator.

### Delete a model

For your own non-built-in models:

1. Click the **Delete** action button on the card.
2. Confirm.

::: warning
- **Built-in models cannot be deleted** from the UI.
- Deletion removes the weight file from server storage. Past predictions made with the model are still readable in [History](./history), but you won't be able to re-run them.
:::

## Cards looking empty?

If you see the empty-state illustration (*"No models yet. Click the button above to upload."*), it means:

- You don't have any of your own models yet, **and**
- No built-in models exist (the administrator hasn't run `seed_builtin_model` yet).

In a normal deployment you should always see at least the two built-in models. If not, please tell your administrator to run the seed step.

## Where to go next

- Use a model right away: [Single Prediction](./predict).
- Train your own: [Fine-tuning](./finetune).
