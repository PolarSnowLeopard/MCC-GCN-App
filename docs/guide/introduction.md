# Introduction

MCC-GCN is a web platform for **multicomponent crystal (MCC) prediction**. Given two molecules, the model predicts how they are most likely to crystallize together.

## What you can do

| Workflow | What it produces |
| --- | --- |
| **Single Prediction** | A 4-class label and probability vector for one molecule pair |
| **Batch Screening** | The same prediction repeated across many pairs from a CSV |
| **Fine-tuning** | A new model trained on your own labelled data, derived from a built-in backbone |
| **Model Management** | Upload, publish, share, or delete your weight files |
| **History** | A full audit trail of everything you have submitted |

## The four prediction classes

The model outputs one of four labels for every molecule pair:

| Label | Meaning |
| --- | --- |
| `Negative` | The two molecules are not expected to form a multicomponent crystal |
| `Salt` | They are expected to form a salt |
| `Cocrystal` | They are expected to form a cocrystal |
| `Solvate` | They are expected to form a solvate |

Probabilities for the four classes always sum to 1. The label shown in the UI is simply the class with the highest probability; you can read the full vector in any prediction result panel.

## Who this guide is for

This documentation assumes you are a **researcher** using the platform — not a developer or sysadmin. It focuses on:

- Where to click in the UI;
- What input the platform expects;
- What output to read off the screen.

For deployment and development topics (Docker, environment variables, REST API), see the project [`README`](https://github.com/PolarSnowLeopard/MCC-GCN-App#readme) instead.

## Where to go next

- **First time?** Start with [Quick Start](./getting-started) to register an account and run your first prediction.
- **Already signed in?** Pick a workflow:
  [Single Prediction](./predict) · [Batch Screening](./batch) · [Fine-tuning](./finetune)
- **Stuck?** Check the [FAQ](./faq).
