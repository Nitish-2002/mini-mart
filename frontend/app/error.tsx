"use client";

import { ErrorStatePanel } from "@/components/shared/ErrorStatePanel";

// ds-auth-012 (experience-design.md §4C) — network/server failure state
// shared across every AUTH screen, via Next.js's own route-level error
// boundary convention rather than a hand-rolled one.
export default function GlobalError({ reset }: { error: Error; reset: () => void }) {
  return (
    <div style={{ display: "flex", minHeight: "100dvh", alignItems: "center", justifyContent: "center", padding: "16px" }}>
      <div style={{ maxWidth: "360px", width: "100%" }}>
        <ErrorStatePanel
          title="Something went wrong"
          message="We couldn't load this page. Check your connection and try again."
          onRetry={reset}
        />
      </div>
    </div>
  );
}
