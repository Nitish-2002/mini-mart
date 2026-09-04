"use client";

import { Button } from "@/components/ui/Button";
import styles from "./SessionExpiredBanner.module.css";

// ds-auth-011 (experience-design.md §4C) — shared shell state, not a
// standalone route. Interrupts any authenticated screen when the 7-day
// session lapses (decision-52) or is otherwise rejected (SY-AUTH-013);
// "Sign in again" returns to this same role's own login entry point rather
// than a generic landing page, so the person doesn't lose their place.
interface SessionExpiredBannerProps {
  loginHref: string;
}

export function SessionExpiredBanner({ loginHref }: SessionExpiredBannerProps) {
  return (
    <div className={styles.overlay} role="alertdialog" aria-modal="true" aria-live="assertive">
      <div className={styles.dialog}>
        <h2 className={styles.title}>Your session has expired</h2>
        <p className={styles.message}>
          Sign in again to keep going — you&apos;ll come right back to this page.
        </p>
        <Button
          onClick={() => {
            window.location.href = `${loginHref}?returnTo=${encodeURIComponent(window.location.pathname)}`;
          }}
        >
          Sign in again
        </Button>
      </div>
    </div>
  );
}
