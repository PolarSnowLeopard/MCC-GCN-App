# FAQ

Answers to the most commonly raised questions, organised by topic.

## Sign-in and account

### I forgot my password.

The current version does not offer self-service password reset. Contact your administrator — they can reset the password on the server using a single management command (see the [project README](https://github.com/PolarSnowLeopard/MCC-GCN-App#operations-cheatsheet)).

### I signed in but the sidebar is empty.

You are most likely viewing the Sign In or Register page, which do not display the sidebar. Complete the sign-in process to reach the main workspace.

## SMILES and input

### The platform reports my SMILES as "invalid".

The platform uses RDKit for SMILES parsing. An "invalid" result means RDKit could not construct a molecular graph from the input string. The recommended fix:

- Retrieve the compound's *Canonical SMILES* from [PubChem](https://pubchem.ncbi.nlm.nih.gov/) and paste it directly.

### The Name/CAS lookup returns "Molecule not found".

The lookup feature queries three upstream databases in sequence: **PubChem**, **NIH NCI Cactus**, and **OPSIN**. If none of them recognises the query:

- Verify the spelling of the English compound name.
- Try the **CAS registry number** instead.
- As a last resort, switch to the **By SMILES** tab and paste the SMILES string directly.

::: info
Chinese compound names are not supported by any of the upstream resolvers. Use the English name or CAS number.
:::

### Can I predict salts written as multi-component SMILES (`X.Y`)?

Yes — RDKit will parse them. However, the model featurises the entire `X.Y` as a single graph. For more accurate results, split the salt's components across the **API** and **Coformer** input fields.

## Prediction

### What does "Confidence" represent?

Confidence is the **maximum** of the four class probabilities. For example, a probability vector of `[0.05, 0.05, 0.85, 0.05]` yields a confidence of `85.0%`. The complete vector is always displayed below the primary result.

### What is "bidirectional inference"?

The molecular graph constructed from the pair `(A, B)` is structurally different from `(B, A)` due to the platform's featurisation scheme. To mitigate this asymmetry, the platform evaluates both orderings and averages the resulting softmax vectors. This is handled automatically.

## Batch screening

### My batch task is stuck at "Queued".

Two possible causes:

1. **Worker backlog** — the Celery worker is processing prior tasks. Allow a few minutes, then refresh.
2. **Worker unavailable** — the Celery process may have stopped. Contact your administrator and ask them to inspect `docker compose logs -f celery`. The task is not lost; it will resume when the worker recovers.

### Why are results not visible when I return to the Batch Screening page?

The results table is rendered from the in-page polling state, which resets upon navigation. To re-open a completed batch, go to **History** and select the corresponding row.

### Is there a maximum batch size?

There is no enforced upper limit. However, the default inference pipeline uses CPU only. Submissions of approximately 5,000 pairs or fewer complete within a reasonable time frame. For larger screens, split the input into sequential submissions.

## Fine-tuning

### My fine-tune job failed with "Need at least 2 valid training samples".

This error indicates that fewer than two rows in the submitted CSV contained valid SMILES on both sides **and** a label in `{0, 1, 2, 3}`. Expand the failed task's detail view to identify which rows were rejected.

### Training is slow. How can I speed it up?

The training pipeline runs on CPU by default. Two practical options:

- **Use a smaller dataset** during prototyping; scale up once the configuration is validated.
- **Reduce the number of epochs** — the default of 50 is conservative. Many small datasets converge well before that threshold.

If your administrator has deployed a GPU-enabled build, training will be substantially faster automatically.

### Where does the fine-tuned model appear?

It is registered on the [Models](./models) page with **Draft** status. You can [test](./finetune#testing) it from the task detail view, then [publish](./finetune#publishing) it when satisfied.

### Can I delete a failed fine-tune task?

Failed tasks do not produce a model file, so there is nothing to delete on the model side. The task record itself is retained in [History](./history) for audit purposes. To remove it permanently, contact your administrator.

## Models

### Why can I not delete a built-in model?

Built-in models are protected. The UI and the API both refuse deletion requests. These models serve as shared defaults for all users on the platform.

### My uploaded `.pth` file fails to load.

The most common cause is saving the full model object rather than the state dict:

```python
# Incorrect — serialises the entire model object
torch.save(model, 'model.pth')

# Correct — serialises only the learnable parameters
torch.save(model.state_dict(), 'model.pth')
```

The platform expects the second form. The state dict must be compatible with the project's `GCNNet` architecture (see [`backend/mcc_gcn/models/gcn.py`](https://github.com/PolarSnowLeopard/MCC-GCN-App/blob/main/backend/mcc_gcn/models/gcn.py)).

## Interface and language

### How do I switch between English and Chinese?

Click the **`EN`** / **`中文`** toggle in the upper-right corner of any page. The entire interface switches immediately. Your preference is stored in browser local storage and persists across sessions.

### The page appears unstyled or broken.

Perform a hard refresh: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (macOS). If the issue persists — particularly on the Django admin panel at `/admin/` — report it to your administrator, as this is typically a deployment-level static file issue.

## Still need help?

Open an issue on the [project GitHub repository](https://github.com/PolarSnowLeopard/MCC-GCN-App/issues), or contact your platform administrator with the following information:

1. The page you were on.
2. The exact input you provided (or a screenshot).
3. The error message text, if any.
