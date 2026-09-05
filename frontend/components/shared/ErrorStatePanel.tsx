import { Button } from "@/components/ui/Button";
import styles from "./ErrorStatePanel.module.css";

// dc-auth-002 (experience-design.md §4C) — icon + message + retry action,
// used identically across ds-auth-003 (rate-limited), ds-auth-010
// (expired/used reset link), ds-auth-012 (generic network/server error).
// Announced via role="alert" so screen readers pick it up without relying
// on color (constraint-a11y). Every current call site renders this as the
// page's *entire* content (the form/normal content it replaces takes its
// own h1 down with it) — title is an h1, not a decorative h2, so the page
// still has exactly one (axe's page-has-heading-one).
interface ErrorStatePanelProps {
  title: string;
  message: string;
  retryLabel?: string;
  onRetry?: () => void;
}

export function ErrorStatePanel({ title, message, retryLabel, onRetry }: ErrorStatePanelProps) {
  return (
    <div className={styles.panel} role="alert">
      <div className={styles.iconCircle} aria-hidden="true">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 9v4m0 4h.01M10.29 3.86l-8.18 14.18A2 2 0 0 0 3.82 21h16.36a2 2 0 0 0 1.71-2.96L13.71 3.86a2 2 0 0 0-3.42 0Z"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      <h1 className={styles.title}>{title}</h1>
      <p className={styles.message}>{message}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          {retryLabel ?? "Try again"}
        </Button>
      )}
    </div>
  );
}
