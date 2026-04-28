# Account & Language

This page covers account-related features and the language preference.

## Language switcher

A small toggle button is displayed in the upper-right corner of every page, labelled **`EN`** or **`中文`**.

- Clicking it switches the entire interface between English and Simplified Chinese.
- The preference is persisted in browser local storage. Subsequent visits default to the last selected language.
- All UI strings are fully translated; mixed-language states do not occur.

::: info
This documentation site has its own independent language switcher, located in the documentation navigation bar. It operates separately from the main application.
:::

## Signing out

At the bottom of the sidebar, next to your username and avatar, there is a **sign-out** icon (an outward-pointing arrow; it turns red on hover). Clicking it terminates your session and returns you to the sign-in page.

## Forgotten password

The current version does not include a self-service password reset mechanism. If you forget your password:

1. Contact your platform administrator.
2. The administrator can reset the password from the server using a Django management command — see the [project README](https://github.com/PolarSnowLeopard/MCC-GCN-App#operations-cheatsheet) for the procedure.

## User roles

Your role is displayed beneath your username in the sidebar:

| Role | Capabilities |
| --- | --- |
| **Researcher** | Full access to all workflows documented in this guide |
| **Admin** | Same as Researcher, plus access to the Django administration panel at `/admin/` |

Role assignment is managed by the administrator and cannot be changed from the UI.
