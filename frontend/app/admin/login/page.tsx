"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ErrorStatePanel } from "@/components/shared/ErrorStatePanel";
import { apiFetch, ApiError } from "@/lib/api";

// ds-auth-007 (experience-design.md §4C) — username/password entry,
// deliberately plain, no OTP step (decision-51). Entry point for
// ss-auth-003. The one login in this module that isn't OTP-based.
export default function AdminLoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [rateLimited, setRateLimited] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await apiFetch("/v1/auth/admin/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      router.push("/admin"); // CATALOG/ORDERS' own admin dashboard, out of scope here
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setRateLimited((err.body.retry_after_seconds as number) ?? 900);
      } else {
        // 401 never distinguishes wrong username from wrong password (enumeration resistance)
        setError("Incorrect username or password.");
      }
    } finally {
      setLoading(false);
    }
  }

  if (rateLimited !== null) {
    return (
      <ErrorStatePanel
        title="Too many attempts"
        message={`Too many login attempts from this connection. Try again in about ${Math.ceil(rateLimited / 60)} minutes.`}
      />
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <p className="eyebrow">Admin</p>
      <h1>Sign in to run your store</h1>
      <p>One account for Mini Mart — catalog, stock, orders, and agents.</p>
      <Input
        label="Username"
        required
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        autoFocus
      />
      <Input
        label="Password"
        type="password"
        required
        error={error ?? undefined}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <Button type="submit" loading={loading}>
        Sign in
      </Button>
      <p>
        <Link href="/admin/reset">Forgot password?</Link>
      </p>
    </form>
  );
}
