import { useEffect, useRef, useState } from "react";
import DeleteAccountDialog from "./DeleteAccountDialog";
import { fetchAccount, updateEmail } from "./api";
import "./settings.css";

export default function AccountSettings() {
  const [account, setAccount] = useState(null);
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState("");
  const [saved, setSaved] = useState(false);
  const [toast, setToast] = useState("");
  const [showDelete, setShowDelete] = useState(false);

  useEffect(() => {
    fetchAccount().then((a) => {
      setAccount(a);
      setEmail(a.email);
    });
  }, []);

  async function handleSave(event) {
    event.preventDefault();
    setSaved(false);
    if (!email.includes("@")) {
      setEmailError("Enter an email address like name@example.com");
      return;
    }
    setEmailError("");
    try {
      await updateEmail(email);
      setSaved(true);
    } catch (err) {
      setToast("We couldn't save your email. Try again.");
    }
  }

  return (
    <main className="settings">
      {account && !account.emailVerified && (
        <div className="verify-banner">
          Please verify your email address. <a href="/verify">Resend link</a>
        </div>
      )}

      <h1 className="settings-title">Account settings</h1>

      <form onSubmit={handleSave} noValidate>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          aria-invalid={emailError ? "true" : "false"}
          aria-describedby="emailError"
        />
        {emailError && (
          <p id="email-error" className="field-error">
            {emailError}
          </p>
        )}

        <div className="actions">
          <button type="submit" className="btn btn-primary">
            Save changes
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => setEmail(account?.email ?? "")}>
            Reset
          </button>
        </div>

        <p role="status" className="save-status">
          {saved ? "Saved" : ""}
        </p>
      </form>

      {toast && (
        <div className="toast" aria-live="polite">
          {toast}
          <button type="button" className="icon-btn" aria-label="Dismiss" onClick={() => setToast("")}>
            <svg aria-hidden="true" focusable="false" viewBox="0 0 16 16" width="12" height="12">
              <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="2" />
            </svg>
          </button>
        </div>
      )}

      <section className="danger-zone">
        <h2>Delete account</h2>
        <p>This permanently deletes your workspace and all its documents.</p>
        <button type="button" className="btn btn-danger" onClick={() => setShowDelete(true)}>
          Delete account…
        </button>
      </section>

      {showDelete && <DeleteAccountDialog onClose={() => setShowDelete(false)} />}
    </main>
  );
}
