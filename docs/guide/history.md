# History

Every prediction and fine-tuning job you submit is saved. The **History** page is where you go back and look.

::: tip Reach the page
Click 🕘 **History** in the sidebar.
:::

## Two tabs

The page has two tabs at the top:

| Tab | Shows |
| --- | --- |
| **Prediction Tasks** | Your *Single Prediction* and *Batch Screening* runs |
| **Fine-tune Tasks** | Your *Fine-tuning* runs |

Both tabs show your records only — other users' history is private.

## Prediction Tasks

Each row shows:

| Column | Notes |
| --- | --- |
| **Type** | `Single` or `Batch` |
| **Status** | `Queued` / `Running` / `Completed` / `Failed` (Completed for synchronous Single predictions) |
| **Created At** | Timestamp |
| **Detail** | Click to open the result panel |

Click **Detail** on any row to re-open the result:

- For **Single** predictions you see exactly what was on the right panel of the Prediction page when you ran it (4-class probabilities, both SMILES, the model used).
- For **Batch** predictions you see the full result table with the same colour-coded class tags.

You can use the type filter at the top to show only Single or only Batch tasks.

## Fine-tune Tasks

Each row shows:

| Column | Notes |
| --- | --- |
| **Task Name** | The name you gave at submission |
| **Status** | `Queued` / `Running` / `Completed` / `Failed` |
| **Created At** | Timestamp |
| **Detail** | Click to open log + actions |

Opening the detail shows the full per-epoch training log and the same **Test Model** / **Publish Model** buttons as on the [Fine-tuning page](./finetune).

## Tips

- **Status sticking on Queued?** Either the Celery worker is overloaded or it's not running at all. Tell your administrator. Your task isn't lost — it stays in the queue and finishes when the worker comes back.
- **Old predictions can still be re-opened** even after the model that made them has been deleted; the result data is stored independently of the weight file.

## Where to go next

- Run another one: [Single Prediction](./predict) / [Batch Screening](./batch).
