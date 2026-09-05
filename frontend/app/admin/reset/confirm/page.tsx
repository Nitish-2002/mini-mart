"use client";

import Link from "next/link";
import { Suspense, FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { apiFetch, ApiError } from "@/lib/api";
import { markSessionActive } from "@/lib/session-marker";

// ds-auth-009 (experience-design.md §4C) — new-password entry, reached via
// the emailed link's ?token= query param. ds-auth-010's expired/used-link
// state is the 410 branch below, not a separate route (TRD-AUTH's 410
// token_expired_or_used is the only error this endpoint defines).
function ConfirmContent() {
  const router = useRouter();
  const token = useSearchParams().get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [expired, setExpired] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (password.length < 12) {
      setError("Password must be at least 12 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords don't match.");
      return;
    }
    setLoading(true);
    try {
      await apiFetch("/v1/auth/admin/password-reset/confirm", {
        method: "POST",
        body: JSON.stringify({ token, new_password: password }),
      });
      markSessionActive();
      router.push("/admin");
    } catch (err) {
      if (err instanceof ApiError && err.status === 410) {
        setExpired(true);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  if (expired) {
    return (
      <div>
        <h1>This link has expired</h1>
        <p>Reset links are valid for 1 hour and can only be used once.</p>
        <p>
          <Link href="/admin/reset">Request a new link</Link>
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <p className="eyebrow">Admin</p>
      <h1>Choose a new password</h1>
      <Input
        label="New password"
        type="password"
        required
        minLength={12}
        error={error ?? undefined}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        autoFocus
      />
      <Input
        label="Confirm new password"
        type="password"
        required
        minLength={12}
        value={confirm}
        onChange={(e) => setConfirm(e.target.value)}
      />
      <Button type="submit" loading={loading}>
        Set new password
      </Button>
    </form>
  );
}

export default function AdminResetConfirmPage() {
  return (
    <Suspense fallback={null}>
      <ConfirmContent />
    </Suspense>
  );
}
