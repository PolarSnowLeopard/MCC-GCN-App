# Single Prediction

The **Prediction** page is for "I have two molecules — what do you think happens when I crystallize them together?". You get back a 4-class label and the full probability vector.

::: tip Reach the page
Click 🧪 **Prediction** in the sidebar. It is also the default landing page after sign-in.
:::

## Page anatomy

The page is split in two columns:

- **Left**: input panel. Two top-level tabs:
  - **Free Prediction** — your own molecules (default)
  - **Paper Samples** — the 64 experimental pairs from our paper, ready to fire
- **Right**: result panel. Empty before your first run.

## Workflow A: Free Prediction

### 1. Pick a model

The **Select Model** dropdown lists every model visible to you:

- Built-in models (`MCC-GCN Pretrained v1`, `MCC-GCN v1`)
- Your own fine-tuned models
- Models that other users have published

Each entry has a tag — `Pretrained` (blue) or `Fine-tuned` (green). For routine prediction, **`MCC-GCN v1`** (the fine-tuned production model) is the recommended default.

### 2. Choose how to enter the molecules

Below the model dropdown, two **input modes** are available as inner tabs:

#### SMILES Input (default)

The fastest path if you already have SMILES strings.

| Field | What to enter |
| --- | --- |
| **API Molecule → SMILES** | The SMILES of the active pharmaceutical ingredient |
| **Coformer Molecule → SMILES** | The SMILES of the coformer |

::: tip Where to get a SMILES
Search the molecule on **PubChem** → look for the *Canonical SMILES* line in the *Names and Identifiers* section. RDKit also accepts most standard SMILES dialects.
:::

#### Name / CAS Input

If you don't have a SMILES at hand:

1. Switch to the **Name / CAS Input** tab.
2. In the API field, type the English compound name (e.g. `Salicylic acid`) or the CAS registry number (e.g. `69-72-7`).
3. Click **Lookup**. The platform queries PubChem; on success the resolved SMILES appears below the input.
4. Repeat for the coformer.

::: warning
Chinese names are **not** supported — use English names or CAS numbers.
If a molecule isn't on PubChem, you'll see *"Molecule not found"*. Fall back to **SMILES Input** in that case.
:::

### 3. Predict

Click the big blue **Predict** button at the bottom.

- Inference takes about 1 second on the default models.
- Validation errors (empty fields, invalid SMILES) show a toast at the top right.

## Workflow B: Paper Samples

For reproducing or quickly trying paper experiments:

1. Switch to the **Paper Samples** tab.
2. Pick a model (same dropdown as in *Free Prediction*).
3. Pick **API Molecule** and **Coformer Molecule** from the two dropdowns. The coformer dropdown is filterable — start typing to narrow the 64 entries.
4. The resolved SMILES for both appear below the dropdowns for sanity check.
5. Click **Predict selected pair**.

## Reading the result

Once a prediction completes, the right column populates:

- **Hero block** — the predicted class number (`Class 0`–`Class 3`), the human label (`Negative` / `Salt` / `Cocrystal` / `Solvate`), and a **Confidence** percentage (the maximum of the four class probabilities).
- **Probability bars** — one row per class, with a coloured bar showing the probability and the exact percentage at the right.
- **Meta block** — the API and Coformer SMILES that were actually used (useful when you used the lookup feature and want to confirm what the model saw).

The result is also saved to your [History](./history) automatically.

## Common errors

| Error toast | What to do |
| --- | --- |
| *"Please select a model"* | Pick something from the **Select Model** dropdown. |
| *"Please enter or look up API SMILES"* | At least one of the two molecule fields is empty. |
| *"Molecule not found"* | The name/CAS isn't on PubChem. Try a synonym or paste a SMILES directly. |
| *"Prediction failed"* | The SMILES was syntactically valid but RDKit could not build a graph (e.g. malformed aromatic ring). Try a canonical SMILES from PubChem. |

## Tips

- Click **Load sample data (KPX + Salicylic acid)** at the top of the form for a known-good pair if you just want to verify the platform is alive.
- **Bidirectional inference**: the platform internally runs the model on both `(API, Coformer)` and `(Coformer, API)` and averages the softmax — you don't need to swap manually.
- Predicted-cocrystal results don't *guarantee* the pair will crystallize; use the probabilities to triage candidates for experiment.

## Where to go next

- Many pairs to test? [Batch Screening](./batch).
- Want a model adapted to your dataset? [Fine-tuning](./finetune).
- Looking up a past run? [History](./history).
