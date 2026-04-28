# Interface Tour

A reference for the application's layout and common UI elements.

## Layout

The interface is composed of three regions:

| Region | Location | Purpose |
| --- | --- | --- |
| **Sidebar** | Left, dark background | Workflow navigation, user information, sign-out |
| **Topbar** | Upper right | Language switcher |
| **Main area** | Centre | The active workflow page |

## Sidebar navigation

| Label | Destination |
| --- | --- |
| **Prediction** | [Single Prediction](./predict) |
| **Batch Screening** | [Batch Screening](./batch) |
| **Fine-tuning** | [Fine-tuning](./finetune) |
| **History** | [History](./history) |
| **Models** | [Model Management](./models) |
| **User Guide** | Opens this documentation site in a new tab |

The currently active page is indicated by a blue highlight.

## Sidebar footer

The bottom of the sidebar displays:

- Your **avatar** (the first letter of your username)
- Your **username** and **role** (`Researcher` or `Admin`)
- A **sign-out** button (arrow icon; turns red on hover)

## Language switcher

Located in the upper-right corner of every page:

- **`EN` / `中文`** — toggles the entire interface between English and Simplified Chinese at runtime. The preference is persisted in browser local storage across sessions.

## Common page elements

Most workflow pages share the following building blocks:

| Element | Description |
| --- | --- |
| **Page title** | Bold heading at the top of the main area |
| **Page description** | Subtitle line providing brief context |
| **Content cards** | White panels with subtle shadow; each groups one logical unit (input, configuration, or results) |
| **Primary buttons** | Blue; trigger the main workflow action |
| **Destructive buttons** | Red; always preceded by a confirmation dialog |

The general interaction pattern is consistent: read the heading, fill the card fields, click the primary button, review the output.

## Next

- [Single Prediction](./predict) — your first hands-on workflow.
- [Account & Language](./account) — language preference and sign-out details.
