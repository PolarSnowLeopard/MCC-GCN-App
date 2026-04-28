# Interface Tour

A quick reference for every part of the UI.

## Layout

The application has three regions:

| Region | Purpose |
| --- | --- |
| **Sidebar** (left, dark) | Workflow navigation + your account + sign-out button |
| **Topbar** (top right) | Language switcher (`EN` / `中文`) |
| **Main area** | The active workflow page |

## Sidebar items

| Icon | Label | Page |
| --- | --- | --- |
| 🧪 | Prediction | [Single Prediction](./predict) |
| 📊 | Batch Screening | [Batch Screening](./batch) |
| 🎯 | Fine-tuning | [Fine-tuning](./finetune) |
| 🕘 | History | [History](./history) |
| 📚 | Models | [Model Management](./models) |

The active page is highlighted in blue.

## Sidebar footer

At the bottom of the sidebar you'll see your **avatar** (first letter of your username), your **username**, and your role (`Researcher` or `Admin`). The arrow icon next to it is the **sign-out** button.

## Topbar

Top right of every page:

- **`EN` / `中文`** — switches the entire UI language at runtime. Your choice is remembered in your browser, so the next time you open the platform it stays in the language you picked.

## Common page elements

Most workflow pages share the same building blocks:

- **Page title** — the bold heading at the top.
- **Page description** — the smaller line below the title.
- **Content cards** — white panels with a subtle shadow, each holding one logical group (input / configuration / results).
- **Action buttons** — primary actions are blue; destructive actions are red and always require confirmation.

Once you can identify these, every page works the same way: read the title → fill the cards → click the primary button → read the result.

## Where to go next

- [Single Prediction](./predict) — run your first prediction.
- [Account & Language](./account) — change your language or sign out.
