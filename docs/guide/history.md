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
| **ID** | Task identifier |
| **Type** | `Single` or `Batch` |
| **Status** | `Queued` · `Running` · `Completed` · `Failed` |
| **Created At** | Submission timestamp |
| **Detail** | Opens the result panel |

Clicking **Detail** opens the saved input and result:

- **Single** predictions show the API, Coformer, predicted class, and the four-class probability distribution.
- **Batch** predictions show every API and Coformer pair together with its predicted class and confidence.
- If an input row failed, its failure reason is shown in the batch table.
- Inputs remain visible while a task is queued or when a task fails.

Completed batch results can be downloaded with **Export CSV**. The export contains the API, Coformer, prediction, class label, confidence, and any failure reason.

## Fine-tune Tasks

Each row contains:

| Column | Description |
| --- | --- |
| **Task Name** | The name assigned at submission |
| **Status** | `Queued` · `Running` · `Completed` · `Failed` |
| **Created At** | Submission timestamp |
| **Detail** | Opens the saved task information and current status |

Use the [Fine-tuning](./finetune) page to test or publish a completed fine-tuned model.

## Notes

- **Task stuck in Queued status**: the Celery worker may be overloaded or stopped. Contact your administrator. The task is not lost — it will resume when the worker recovers.
- **Deleted models do not affect history**: prediction results are stored independently of the weight file. Past results remain viewable even after the model that produced them has been removed.

## Next

- Submit another task: [Single Prediction](./predict) · [Batch Screening](./batch).
