"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ErrorStatePanel } from "@/components/shared/ErrorStatePanel";
import { apiFetch, ApiError } from "@/lib/api";

// ds-auth-001 (experience-design.md §4C) — email entry, reused identically
// for both End User and Delivery Agent (one mechanism, per decision-49) at
// each role's own path prefix (CR-007). ds-auth-003 (rate-limited) is a
// state of this same screen, not a separate route.
interface EmailEntryScreenProps {
  role: "end_user" | "delivery_agent";
  verifyPath: string;
  heading: string;
  intro: string;
}

export function EmailEntryScreen({ role, verifyPath, heading, intro }: EmailEntryScreenProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [rateLimited, setRateLimited] = useState<number | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      await apiFetch("/v1/auth/otp/request", {
        method: "POST",
        body: JSON.stringify({ email, role }),
      });
      router.push(`${verifyPath}?email=${encodeURIComponent(email)}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setRateLimited((err.body.retry_after_seconds as number) ?? 1800);
      }
    } finally {
      setLoading(false);
    }
  }

  if (rateLimited !== null) {
    return (
      <ErrorStatePanel
        title="Too many attempts"
        message={`You've requested a code too many times. Try again in about ${Math.ceil(rateLimited / 60)} minutes.`}
      />
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <p className="eyebrow">Sign in</p>
      <h1>{heading}</h1>
      <p>{intro}</p>
      <Input
        label="Email"
        type="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        autoFocus
      />
      <Button type="submit" loading={loading}>
        Send code
      </Button>
    </form>
  );
}
