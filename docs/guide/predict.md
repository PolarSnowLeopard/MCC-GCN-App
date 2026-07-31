# Single Prediction

The **Prediction** page answers the question: *given two molecules, what is the most likely co-crystallisation outcome?* The platform returns a four-class label and the full probability vector.

::: tip Navigation
Select **Prediction** in the sidebar. This page is also the default landing page after sign-in.
:::

## Page layout

The page is divided into two columns:

- **Left** — Input panel with two top-level tabs:
  - **Free Prediction** — enter your own molecules (default)
  - **Paper Samples** — the 64 experimental pairs from the published study, pre-loaded for quick evaluation
- **Right** — Result panel (empty before the first prediction)

## Free Prediction workflow

### Step 1 — Select a model

The **Select Model** dropdown lists every model visible to your account:

- Built-in models (e.g. `MCC-GCN Pretrained v2`, `MCC-GCN v1`)
- Your own fine-tuned models
- Models published by other users

Each entry carries a tag: `Pretrained` (blue) or `Fine-tuned` (green). For routine inference, **`MCC-GCN v1`** — the production fine-tuned model — is recommended.

::: info
If no model is selected, the platform automatically selects the built-in fine-tuned model when you click **Predict**.
:::

### Step 2 — Enter the molecule pair

Two input modes are available as inner tabs below the model selector.

#### By SMILES

The most direct path when you already have SMILES strings.

| Field | Description |
| --- | --- |
| **API Molecule** | The canonical SMILES of the active pharmaceutical ingredient |
| **Coformer Molecule** | The canonical SMILES of the coformer |

::: tip Obtaining a SMILES string
Look up the compound on [PubChem](https://pubchem.ncbi.nlm.nih.gov/) and locate the *Canonical SMILES* entry under *Names and Identifiers*. The platform's RDKit parser accepts most standard SMILES dialects.
:::

#### By Name / CAS

If you do not have a SMILES string at hand, the platform can resolve one from a compound name or CAS registry number.

1. Switch to the **Name / CAS** tab.
2. Enter the compound's **English name** (e.g. `Salicylic acid`) or **CAS number** (e.g. `69-72-7`) in the search field.
3. Click **Lookup**. The platform queries multiple chemical databases in sequence (PubChem, NIH NCI Cactus, and OPSIN) through a backend proxy. On success, the resolved SMILES is automatically filled into the editable SMILES input below.
4. Review and, if necessary, manually edit the resolved SMILES.
5. Repeat for the second molecule.

::: warning
- Only **English names** and **CAS registry numbers** are supported; Chinese compound names will not resolve.
- If none of the upstream databases recognises the query, a *"Molecule not found"* message is displayed. Switch to the **By SMILES** tab and enter the SMILES manually.
:::

### Step 3 — Run the prediction

Click the **Predict** button at the bottom of the form.

- Typical inference time is approximately one second.
- Validation failures (missing fields, unparseable SMILES) are reported via toast notifications.
- If both SMILES fields are empty, a warning prompts you to complete the form.

## Paper Samples workflow

For reproducing published experimental results or rapid benchmarking:

1. Switch to the **Paper Samples** tab.
2. Select a model (same dropdown as Free Prediction).
3. Select an **API molecule** and a **Coformer** from the two dropdown menus. The coformer list is searchable — type to filter the 30 entries.
4. The resolved SMILES for both selections are displayed beneath the dropdowns for verification.
5. Click **Predict**.

## Interpreting the result

Once a prediction completes, the right column displays:

| Section | Content |
| --- | --- |
| **Classification** | The predicted class number (`Class 0`–`Class 3`) and its human-readable label (`Negative`, `Salt`, `Cocrystal`, or `Solvate`) |
| **Confidence** | The maximum of the four class probabilities, expressed as a percentage |
| **Probability bars** | One row per class with a coloured bar and exact percentage |
| **Input summary** | The API and Coformer SMILES that were sent to the model, useful for confirming what the resolver produced |

The result is automatically persisted to [History](./history).

## Common error messages

| Message | Resolution |
| --- | --- |
| *"Please select a model"* | Choose a model from the dropdown, or click Predict to auto-select. |
| *"Please fill in or look up SMILES for both molecules"* | At least one SMILES field is empty. Enter or look up both molecules. |
| *"Molecule not found"* | The name or CAS was not recognised by any upstream resolver. Try a synonym, use the CAS number, or paste the SMILES directly. |
| *"Prediction failed"* | The SMILES was syntactically valid but RDKit could not construct a molecular graph (e.g. malformed ring system). Use a canonical SMILES from PubChem. |

## Technical notes

- **Bidirectional inference**: the platform evaluates both molecule orderings `(API, Coformer)` and `(Coformer, API)`, then averages the softmax outputs. This compensates for the non-symmetric nature of the graph featurisation.
- **Probabilistic output**: a prediction of `Cocrystal` with 65% confidence is meaningfully different from one at 95%. Use the probability vector to prioritise candidates for experimental validation rather than relying on the label alone.

## Next

- Screen many pairs simultaneously: [Batch Screening](./batch).
- Train a domain-specific model: [Fine-tuning](./finetune).
- Review a previous result: [History](./history).
