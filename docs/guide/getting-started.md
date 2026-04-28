# Quick Start

This walks you through registering, logging in, and running your first prediction. About five minutes.

## 1. Open the platform

Open your browser at the address provided by your administrator, e.g.:

```
http://<your-server>:8880/
```

You will land on the **Sign In** page.

## 2. Create an account

Click **Register** under the sign-in form (or **"Don't have an account? Register"**).

On the registration form:

| Field | What to enter |
| --- | --- |
| **Username** | Any unique handle, letters / digits / underscore |
| **Email** | A real address — used for password recovery later |
| **Password** | At least 6 characters |
| **Confirm Password** | Same as above |

Click **Sign Up**. On success you will be returned to the sign-in screen.

::: tip
If you already have credentials from your administrator, skip to the next step.
:::

## 3. Sign in

Enter your username and password and click **Sign In**.

You will land on the **Single Prediction** page (the main workspace). The left sidebar shows the five workflows:

- 🧪 **Prediction**
- 📊 **Batch Screening**
- 🎯 **Fine-tuning**
- 🕘 **History**
- 📚 **Models**

## 4. Run your first prediction

The fastest path: click **Load sample data (KPX + Salicylic acid)** at the top of the form. This fills both molecule fields with valid SMILES from the paper's experimental set.

Then:

1. In **Select Model**, pick **MCC-GCN v1** (the production fine-tuned model, ready to use).
2. Click **Predict**.
3. After ~1 second the right panel shows:
   - The predicted label (`Cocrystal`, `Salt`, `Solvate`, or `Negative`)
   - The four-class probability vector
   - A confidence percentage

That's it — you have run your first prediction.

## 5. Where to next

- Try predicting your **own pair**: see [Single Prediction](./predict) for SMILES input, name/CAS lookup, and how to read results.
- Have many pairs to try? Jump to [Batch Screening](./batch).
- Want a model adapted to your dataset? See [Fine-tuning](./finetune).
- Curious about every page in the sidebar? See the [Interface Tour](./interface).
