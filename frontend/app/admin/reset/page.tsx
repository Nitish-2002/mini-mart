"use client";

import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { apiFetch } from "@/lib/api";

// ds-auth-008 (experience-design.md §4C) — Admin requests a reset link.
// Entry point for ss-auth-004. The confirmation below shows identically
// whether or not the email matched (decision-77) — this screen has no way
// to know, and must not pretend otherwise.
export default function AdminResetRequestPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      await apiFetch("/v1/auth/admin/password-reset/request", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
    } finally {
      setLoading(false);
      setSent(true); // shown regardless of the request's outcome, by design
    }
  }

  if (sent) {
    return (
      <div>
        <h1>Check your email</h1>
        <p>
          If <strong>{email}</strong> is the registered recovery address, we&apos;ve sent a link to
          reset the password. It&apos;s valid for 1 hour.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <p className="eyebrow">Admin</p>
      <h1>Reset your password</h1>
      <p>Enter the recovery email on file and we&apos;ll send a reset link.</p>
      <Input
        label="Recovery email"
        type="email"
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        autoFocus
      />
      <Button type="submit" loading={loading}>
        Send reset link
      </Button>
    </form>
  );
}
