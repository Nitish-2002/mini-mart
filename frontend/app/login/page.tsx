"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ErrorStatePanel } from "@/components/shared/ErrorStatePanel";
import { apiFetch, ApiError } from "@/lib/api";

// ds-auth-001 (experience-design.md §4C) — email entry, End User context.
// Entry point for ss-auth-001. The only field that matters is a valid
// email — no password field exists anywhere in this flow (decision-15).
export default function LoginPage() {
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
        body: JSON.stringify({ email, role: "end_user" }),
      });
      router.push(`/login/verify?email=${encodeURIComponent(email)}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setRateLimited((err.body.retry_after_seconds as number) ?? 1800);
      }
    } finally {
      setLoading(false);
    }
  }

  if (rateLimited !== null) {
    // ds-auth-003 — a state of this screen, not a separate route.
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
      <h1>Welcome to Mini Mart</h1>
      <p>Enter your email and we&apos;ll send you a one-time code — no password to remember.</p>
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
