# Quick Start

This walkthrough covers account creation, sign-in, and a first prediction. Estimated time: under five minutes.

## 1. Open the platform

Navigate to the URL provided by your administrator:

```
https://<your-domain>/
```

You will be presented with the **Sign In** page.

::: tip HTTPS
The platform is served over HTTPS. Plain HTTP requests are automatically redirected.
:::

## 2. Create an account

Click **Register** below the sign-in form.

| Field | Requirement |
| --- | --- |
| **Username** | Unique; letters, digits, and underscores |
| **Email** | A valid address (used for administrative contact) |
| **Password** | Minimum 6 characters |
| **Confirm Password** | Must match the password field |

Click **Sign Up**. On success you will be redirected to the sign-in page.

::: tip
If your administrator has already provisioned credentials for you, skip directly to sign-in.
:::

## 3. Sign in

Enter your username and password, then click **Sign In**.

You will land on the **Single Prediction** page — the default workspace. The left sidebar provides access to the five core workflows:

- **Prediction** — single molecule-pair inference
- **Batch Screening** — bulk CSV-based inference
- **Fine-tuning** — transfer learning on custom data
- **History** — audit trail of all past tasks
- **Models** — model library management

A **User Guide** link at the bottom of the sidebar opens this documentation site.

## 4. Run your first prediction

The quickest path uses the built-in experimental dataset:

1. On the Prediction page, switch to the **Paper Samples** tab.
2. Select an **API molecule** and a **Coformer** from the two dropdowns — these are the 64 experimental pairs from the published study.
3. A model is selected automatically. Click **Predict**.
4. The right panel displays:
   - The predicted class label (e.g. `Cocrystal`)
   - The four-class probability distribution
   - A confidence percentage (the maximum class probability)

You have completed your first prediction.

## 5. Next steps

- Predict with **your own molecules**: see [Single Prediction](./predict) for SMILES input and name/CAS resolution.
- Screen **many pairs at once**: [Batch Screening](./batch).
- Train a **domain-specific model**: [Fine-tuning](./finetune).
- Explore the **full interface**: [Interface Tour](./interface).
