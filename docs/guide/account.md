# Account & Language

A short page covering the things in the corners of the UI.

## Language switcher

Top-right corner of every page is a small button labelled `EN` or `中文`.

- Click it to flip the entire interface between English and Simplified Chinese.
- Your choice is saved in your browser, so the next visit stays in the same language.
- The platform's content is fully translated — there's no mixed-language state.

::: tip
This documentation site has its own language switcher (top-right of the docs nav bar). It is independent of the main app.
:::

## Sign out

Bottom of the sidebar, next to your username and avatar:

- A small **arrow-out** icon (red on hover) signs you out and returns you to the login screen.

## Forgot your password

The platform doesn't expose a self-service password-reset page in the current version. If you forget your password:

- Contact your administrator.
- They can reset it from the server using a Django management command — see the [project README](https://github.com/PolarSnowLeopard/MCC-GCN-App#operations-cheatsheet) for the exact command.

## Your role

Your role is shown under your username in the sidebar:

- **Researcher** — the standard role. You can do everything documented in this guide.
- **Admin** — the same as Researcher, plus access to the Django admin (`/admin/`). Most users won't have this.

You cannot change your own role from the UI — your administrator manages this.
