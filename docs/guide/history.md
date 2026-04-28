# History

Every prediction and fine-tuning task submitted through the platform is automatically persisted. The **History** page provides access to all past results.

::: tip Navigation
Select **History** in the sidebar.
:::

## Tabs

The page is organised into two tabs:

| Tab | Content |
| --- | --- |
| **Prediction Tasks** | Single Prediction and Batch Screening submissions |
| **Fine-tune Tasks** | Fine-tuning jobs |

Both tabs display only **your own** tasks. Other users' history is not visible.

## Prediction Tasks

Each row contains:

| Column | Description |
| --- | --- |
| **Type** | `Single` or `Batch` |
| **Status** | `Queued` · `Running` · `Completed` · `Failed` |
| **Created At** | Submission timestamp |
| **Detail** | Opens the result panel |

Clicking **Detail** reopens the full result:

- **Single** predictions show the four-class probability distribution, both SMILES, and the model used — identical to what was displayed on the Prediction page at run time.
- **Batch** predictions show the complete results table with colour-coded class tags.

A type filter at the top of the list allows you to display only Single or only Batch tasks.

## Fine-tune Tasks

Each row contains:

| Column | Description |
| --- | --- |
| **Task Name** | The name assigned at submission |
| **Status** | `Queued` · `Running` · `Completed` · `Failed` |
| **Created At** | Submission timestamp |
| **Detail** | Opens the training log and action buttons |

The detail view provides the per-epoch training log and the same **Test Model** / **Publish Model** actions available on the [Fine-tuning](./finetune) page.

## Notes

- **Task stuck in Queued status**: the Celery worker may be overloaded or stopped. Contact your administrator. The task is not lost — it will resume when the worker recovers.
- **Deleted models do not affect history**: prediction results are stored independently of the weight file. Past results remain viewable even after the model that produced them has been removed.

## Next

- Submit another task: [Single Prediction](./predict) · [Batch Screening](./batch).
