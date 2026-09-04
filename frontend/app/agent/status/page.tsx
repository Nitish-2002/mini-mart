"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { StatusBadge, AgentStatus } from "@/components/shared/StatusBadge";
import { apiFetch, ApiError } from "@/lib/api";

// ds-auth-006 (experience-design.md §4C) — one template, all four
// sm-auth-agent-status states. Shown when an agent's status isn't a simple
// "proceed" case (or, until ORDERS' assigned-orders view exists, always).
const COPY: Record<AgentStatus, { heading: string; message: string }> = {
  pending_approval: {
    heading: "Still under review",
    message: "Admin hasn't made a decision yet. This updates automatically once they do.",
  },
  approved: {
    heading: "You're approved!",
    message: "You can now receive deliveries. Order assignment isn't live yet in this build.",
  },
  deactivated: {
    heading: "Your account has been deactivated",
    message: "Contact Mini Mart's admin if you believe this is a mistake.",
  },
  rejected: {
    heading: "Application not approved",
    message: "Admin has reviewed your application and it wasn't approved this time.",
  },
};

export default function AgentStatusPage() {
  const router = useRouter();
  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [loadFailed, setLoadFailed] = useState(false);

  useEffect(() => {
    apiFetch<{ status: AgentStatus }>("/v1/auth/agent/status")
      .then((res) => setStatus(res.status))
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          router.push("/agent/login");
        } else {
          setLoadFailed(true);
        }
      });
  }, [router]);

  if (loadFailed) return null; // app/error.tsx (ds-auth-012) is the shared failure state
  if (status === null) return null;

  const copy = COPY[status];

  return (
    <div>
      <p className="eyebrow">Your application</p>
      <h1>{copy.heading}</h1>
      <p>{copy.message}</p>
      <StatusBadge status={status} />
      {status === "approved" && <Button onClick={() => router.push("/agent/login")}>Continue to sign in</Button>}
    </div>
  );
}
