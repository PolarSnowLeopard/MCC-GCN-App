# Introduction

MCC-GCN is a web-based platform for **multicomponent crystal (MCC) prediction**. Given a pair of molecules — an active pharmaceutical ingredient (API) and a coformer — the underlying graph convolutional network predicts how they are most likely to co-crystallise.

## Capabilities

| Workflow | Output |
| --- | --- |
| **Single Prediction** | A four-class label and per-class probability vector for one molecule pair |
| **Batch Screening** | The same prediction applied to hundreds or thousands of pairs supplied via CSV |
| **Fine-tuning** | A new model derived from a built-in backbone, trained on your own labelled data |
| **Model Management** | Upload, publish, share, or delete weight files |
| **History** | A persistent audit trail of every submitted task |

## Prediction classes

The model assigns one of four labels to every molecule pair:

| Class | Label | Interpretation |
| :---: | --- | --- |
| 0 | **Negative** | The two molecules are not expected to form a multicomponent crystal |
| 1 | **Salt** | A proton-transfer salt is the most likely outcome |
| 2 | **Cocrystal** | A cocrystal (non-ionic) is the most likely outcome |
| 3 | **Solvate** | A solvate is the most likely outcome |

The four class probabilities always sum to 1. The label displayed in the UI corresponds to the class with the highest probability; the full vector is available in every result panel.

::: info Bidirectional inference
The featurisation step is not strictly symmetric with respect to molecule ordering. To compensate, the platform internally evaluates both `(API, Coformer)` and `(Coformer, API)` and averages the resulting softmax vectors. This happens transparently — no manual intervention is needed.
:::

## Audience

This guide is written for **researchers** who use the platform through its web interface. It covers:

- Navigation and page layout;
- Expected inputs and their formats;
- How to interpret outputs.

For deployment, environment configuration, and REST API documentation, refer to the project [README](https://github.com/PolarSnowLeopard/MCC-GCN-App#readme).

## Navigation

- **First time?** Begin with [Quick Start](./getting-started) — register, sign in, and run your first prediction.
- **Already signed in?** Pick a workflow: [Single Prediction](./predict) · [Batch Screening](./batch) · [Fine-tuning](./finetune)
- **Having trouble?** Consult the [FAQ](./faq).
