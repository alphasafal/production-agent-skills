import { useEffect, useRef, useState } from "react";
import { deleteAccount } from "./api";

export default function DeleteAccountDialog({ onClose }) {
  const dialogRef = useRef(null);
  const headingRef = useRef(null);
  const [deleting, setDeleting] = useState(false);
  const [confirmText, setConfirmText] = useState("");

  useEffect(() => {
    const appRoot = document.getElementById("app-root");
    appRoot.setAttribute("aria-hidden", "true");
    headingRef.current.focus();

    function onKeyDown(event) {
      if (event.key === "Escape") onClose();
      if (event.key === "Tab") {
        const focusable = dialogRef.current.querySelectorAll("button, input");
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      appRoot.removeAttribute("aria-hidden");
    };
  }, [onClose]);

  async function handleDelete() {
    setDeleting(true);
    await deleteAccount();
    window.location.assign("/goodbye");
  }

  const canDelete = confirmText === "DELETE";

  return (
    <div className="backdrop">
      <div
        ref={dialogRef}
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-title"
      >
        <h2 id="delete-title" tabIndex={-1} ref={headingRef}>
          Delete your account?
        </h2>
        <p>Type DELETE to confirm. This cannot be undone.</p>
        <label htmlFor="confirm">Confirmation</label>
        <input id="confirm" value={confirmText} onChange={(e) => setConfirmText(e.target.value)} />
        <div className="dialog-actions">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="btn btn-danger"
            aria-disabled={!canDelete || deleting}
            onClick={handleDelete}
          >
            {deleting ? "Deleting…" : "Delete account"}
          </button>
        </div>
      </div>
    </div>
  );
}
