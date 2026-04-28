# FAQ

Quick answers to the questions that come up most often.

## Sign-in & account

### I forgot my password.

There is no self-service reset in the current version. Contact your administrator — they can reset it on the server using a single command (see the [project README](https://github.com/PolarSnowLeopard/MCC-GCN-App#operations-cheatsheet)).

### My account works but the sidebar is empty.

You're probably looking at the **Login** or **Register** page (these don't show the sidebar). Sign in to land on the main workspace.

## SMILES & input

### My SMILES is "invalid" — what does that mean?

The platform tries to parse the SMILES with RDKit. "Invalid" means RDKit could not build a molecule graph from the string. The fastest fix:

- Take the *Canonical SMILES* from PubChem for that molecule and paste that.

### I have a Chinese compound name. The Name lookup says "not found".

The lookup uses PubChem, which only knows English names and CAS numbers. Either:

- Translate the name to English, or
- Use the CAS registry number, or
- Paste the SMILES directly (use the **SMILES Input** tab).

### Can I predict salts written as multi-component SMILES (`X.Y`)?

Yes, RDKit accepts them, but the model will treat the whole `X.Y` as one molecule. For best results, split the salt across the **API** and **Coformer** slots instead.

## Prediction

### What does *Confidence* mean exactly?

It is the **maximum** of the four class probabilities. So a prediction with `[0.05, 0.05, 0.85, 0.05]` shows a confidence of `85.0%`. The full vector is also displayed below the hero result.

### Why does the platform say it does "bidirectional inference"?

The molecule pair `(A, B)` builds a different graph than `(B, A)` because the platform's featurizer is not strictly symmetric. The platform internally runs both orderings and averages the softmax. You don't need to swap manually.

## Batch screening

### My batch task is stuck at *Queued* forever.

Two possibilities:

1. The Celery worker is overloaded — give it a minute, then refresh.
2. The Celery worker is down. Tell your administrator to check `docker compose logs -f celery`. The task itself isn't lost; it resumes when the worker is back.

### Why don't I see results when I come back to the Batch page?

The results table is rendered from the in-page polling state, which resets when you leave. To re-open a completed batch, go to **History → Prediction Tasks** and click the row.

### How big can a batch be?

There's no hard cap, but the inference pipeline is CPU-only by default. Batches under ~5,000 pairs are comfortable; very large screens are best split into sequential submissions.

## Fine-tuning

### My fine-tune failed with *"Need at least 2 valid training samples"*.

Either fewer than 2 rows in your CSV had valid SMILES on **both** sides, or the labels weren't integers `0`–`3`. Open the failed task's detail to see which rows the parser rejected.

### Training is slow — anything I can do?

The pipeline runs on CPU. Two levers:

- **Smaller dataset** for prototyping; scale up once your config looks right.
- **Fewer epochs** — the default `50` is conservative. Many small datasets converge well before that.

If your administrator has a GPU-enabled deployment, training will be substantially faster automatically.

### Where does my fine-tuned model end up?

It appears in the [Models page](./models) as **Draft**. You can [test](./finetune#testing-the-result) it from the same expanded task, then [publish](./finetune#publishing-the-result) when you're happy.

### Can I delete the model produced by a failed fine-tune?

Failed runs don't produce a model file at all; nothing to delete. The failed task itself stays in [History](./history) for reference. If you want it gone permanently, ask your administrator.

## Models

### Why is *Built-in* greyed out — can I delete it?

Built-in models are protected. The platform refuses to delete them from the UI, and the API returns an error too. They're meant as common defaults for everyone.

### My uploaded `.pth` won't load.

Most likely you saved the whole model object instead of just its state dict:

```python
# wrong — saves the entire object
torch.save(model, 'model.pth')

# correct — saves only the parameters
torch.save(model.state_dict(), 'model.pth')
```

The platform expects the second form, with weights matching the project's `GCNNet` architecture. See [`backend/mcc_gcn/models/gcn.py`](https://github.com/PolarSnowLeopard/MCC-GCN-App/blob/main/backend/mcc_gcn/models/gcn.py).

## UI & language

### How do I switch between English and Chinese?

Click the small `EN` / `中文` button in the top-right corner of any page. The whole UI flips. Your choice is remembered in your browser.

### The page looks broken / styles missing.

Hard-refresh: `Ctrl/Cmd + Shift + R`. If the problem persists — particularly on the Django admin under `/admin/` — tell your administrator; this is usually a deployment issue with static files.

## Still stuck?

Open an issue on the [project GitHub](https://github.com/PolarSnowLeopard/MCC-GCN-App/issues), or contact your platform administrator with:

1. The page you were on;
2. Exactly what you typed / uploaded (or a screenshot);
3. The error toast text, if any.
