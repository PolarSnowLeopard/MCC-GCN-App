# Data Formats

A single-page reference for everything the platform consumes or produces in CSV / SMILES form.

## SMILES

The platform parses SMILES with **RDKit**. In practice this means:

- Standard Daylight SMILES are accepted.
- Aromatic notation (`c1ccccc1`) is fine.
- Stereochemistry markers (`/`, `\`, `@`) are accepted but not used by the model.
- Salts written as multi-component SMILES with `.` (e.g. `[Na+].[Cl-]`) work, but they will be featurized as one molecule — usually you want to split them across the API/Coformer slots instead.

::: tip If a SMILES fails
Take the molecule's *Canonical SMILES* from PubChem. RDKit accepts those almost without exception.
:::

## Batch screening CSV

Used by [Batch Screening → Upload CSV](./batch#upload-csv).

```csv
api_smiles,coformer_smiles
CCO,O=C(O)c1ccccc1O
O=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]
```

Rules:

- **Two columns**: `api_smiles`, `coformer_smiles`.
- **Header row**: optional. The first line is skipped only if it contains the word `smiles` (case-insensitive).
- **Encoding**: UTF-8.
- **Empty / malformed rows**: silently dropped.

Click **Download Template** on the Batch page for a working starter file.

## Fine-tuning CSV

Used by [Fine-tuning → Training Data](./finetune#step-1-prepare-your-training-data).

```csv
api_smiles,coformer_smiles,label
CCO,O=C(O)c1ccccc1O,2
c1ccccc1,CC(=O)O,0
```

Rules:

- **Three columns**: `api_smiles`, `coformer_smiles`, `label`.
- **Label** must be an integer in `0..3` matching the platform's class scheme:

| Label | Class |
| --- | --- |
| `0` | `Negative` |
| `1` | `Salt` |
| `2` | `Cocrystal` |
| `3` | `Solvate` |

- **Minimum**: 2 valid rows. (Rows whose SMILES doesn't parse are silently dropped.)
- **Header row**: required (the parser uses `DictReader`).

Click **Download Template** on the Fine-tuning page for a starter file.

## Batch results CSV (export)

What you get when you click **Export CSV** on the Batch results card:

```csv
API SMILES,Coformer SMILES,Prediction,Label,Confidence
"CCO","O=C(O)c1ccccc1O",2,Cocrystal,89.1%
"O=C(O)CCC(=O)O","Nc1ccnc(N)[n+]1[O-]",1,Salt,76.4%
```

Columns:

| Column | Notes |
| --- | --- |
| `API SMILES`, `Coformer SMILES` | Quoted; echoed from the input |
| `Prediction` | Integer class label (0–3) |
| `Label` | Human label (`Negative` / `Salt` / `Cocrystal` / `Solvate`) |
| `Confidence` | Max probability, in percent |

Note: the export deliberately omits the full probability vector (just the predicted class + its confidence). If you need the full vector, fall back to the platform's REST API.

## REST API

For automated workflows the platform also exposes a Token-authenticated REST API. The full reference lives in the [project README](https://github.com/PolarSnowLeopard/MCC-GCN-App#-api-reference).
