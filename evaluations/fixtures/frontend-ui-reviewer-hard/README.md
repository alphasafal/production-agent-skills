# account-settings

Account settings screen for the workspace app. Lets a user change their
email and delete their account.

## Files

| File | What it is |
|---|---|
| `AccountSettings.jsx` | The settings page: verify-email banner, email form, error toast, danger zone |
| `DeleteAccountDialog.jsx` | Confirmation dialog for account deletion |
| `settings.css` | Styles for both; design tokens are in `:root` |

`./api` is not included. `fetchAccount()` resolves in 300-900 ms with
`{ email, emailVerified }`. `updateEmail(email)` and `deleteAccount()` resolve
or reject; `deleteAccount()` takes 1-3 seconds and is **not idempotent**: a
second call while the first is in flight returns a 500 and pages on-call.

## How it's mounted

`index.html` has a single `<div id="app-root"></div>`; the whole React tree,
including this page and the dialog, renders into it with
`createRoot(document.getElementById("app-root"))`. There is no portal.

The dialog was reviewed last sprint against our dialog checklist (role,
aria-modal, name, Escape, initial focus, focus trap) and passed. About 40% of
traffic is mobile; screen-reader users are a known group of customers
(accessibility clause in two enterprise contracts).
