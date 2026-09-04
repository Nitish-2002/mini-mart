"use client";

import Link from "next/link";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { StatusBadge } from "@/components/shared/StatusBadge";

// ds-auth-005 (experience-design.md §4C) — confirms the registration was
// received and sets expectations (a real wait estimate, not a generic
// success toast — this is a new process with no existing pattern to lean on).
function SubmittedContent() {
  const email = useSearchParams().get("email") ?? "your email";

  return (
    <div>
      <h1>Application received</h1>
      <p>
        We&apos;ve sent your details to Mini Mart&apos;s admin. Most applications are reviewed
        within a day or two — we&apos;ll email <strong>{email}</strong> either way.
      </p>
      <StatusBadge status="pending_approval" />
      <p>
        <Link href="/agent/status">Check my status →</Link>
      </p>
    </div>
  );
}

export default function RegisterSubmittedPage() {
  return (
    <Suspense fallback={null}>
      <SubmittedContent />
    </Suspense>
  );
}
