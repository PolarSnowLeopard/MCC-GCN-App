# Data Formats

A consolidated reference for all file formats consumed and produced by the platform.

## SMILES strings

The platform uses **RDKit** for SMILES parsing. In practice:

- Standard Daylight SMILES notation is accepted.
- Aromatic shorthand (e.g. `c1ccccc1`) is supported.
- Stereochemistry markers (`/`, `\`, `@`, `@@`) are accepted but are not utilised by the model.
- Multi-component SMILES using the `.` separator (e.g. `[Na+].[Cl-]`) are parseable, but the model will featurise the entire string as a single molecular graph. For salts, it is generally more appropriate to assign each component to the **API** and **Coformer** fields separately.

::: tip
If a SMILES string fails to parse, retrieve the compound's *Canonical SMILES* from [PubChem](https://pubchem.ncbi.nlm.nih.gov/). RDKit accepts these with near-certainty.
:::

## Batch screening CSV (input)

Used by [Batch Screening](./batch).

```csv
api_smiles,coformer_smiles
CCO,O=C(O)c1ccccc1O
O=C(O)CCC(=O)O,Nc1ccnc(N)[n+]1[O-]
```

| Rule | Detail |
| --- | --- |
| **Columns** | Exactly two: `api_smiles`, `coformer_smiles` |
| **Header row** | Optional. The first line is treated as a header and skipped if it contains the substring `smiles` (case-insensitive). |
| **Encoding** | UTF-8 |
| **Invalid rows** | Rows that are empty or do not contain exactly two fields are silently discarded |

Click **Download Template** on the Batch Screening page for a starter file.

## Fine-tuning CSV (input)

Used by [Fine-tuning](./finetune).

```csv
api_smiles,coformer_smiles,label
CCO,O=C(O)c1ccccc1O,2
c1ccccc1,CC(=O)O,0
```

| Rule | Detail |
| --- | --- |
| **Columns** | Exactly three: `api_smiles`, `coformer_smiles`, `label` |
| **Label values** | Integer in `{0, 1, 2, 3}` — see class mapping below |
| **Header row** | **Required** (the parser uses Python's `csv.DictReader`) |
| **Minimum rows** | 2 valid rows (both SMILES parseable, label valid) |
| **Invalid rows** | Silently discarded |

Class mapping:

| Label | Class |
| :---: | --- |
| `0` | Negative |
| `1` | Salt |
| `2` | Cocrystal |
| `3` | Solvate |

Click **Download Template** on the Fine-tuning page for a starter file.

## Batch results CSV (export)

Produced by clicking **Export CSV** on the Batch Screening results card.

```csv
API SMILES,Coformer SMILES,Prediction,Label,Confidence
"CCO","O=C(O)c1ccccc1O",2,Cocrystal,89.1%
"O=C(O)CCC(=O)O","Nc1ccnc(N)[n+]1[O-]",1,Salt,76.4%
```

| Column | Description |
| --- | --- |
| `API SMILES`, `Coformer SMILES` | Quoted; echoed from the input |
| `Prediction` | Integer class label (`0`–`3`) |
| `Label` | Human-readable class name |
| `Confidence` | Maximum class probability, expressed as a percentage |

::: info
The export includes only the predicted class and its confidence. The full four-class probability vector is available through the platform's REST API.
:::

## REST API

For programmatic access, the platform provides a token-authenticated REST API. The complete endpoint reference is documented in the [project README](https://github.com/PolarSnowLeopard/MCC-GCN-App#-api-reference).
