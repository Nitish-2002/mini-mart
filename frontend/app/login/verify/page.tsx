"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { OtpInput } from "@/components/ui/OtpInput";
import { apiFetch, ApiError } from "@/lib/api";

// ds-auth-002 (experience-design.md §4C) — 6-digit code entry, live
// countdown to resend, inline error on wrong code. Follows ds-auth-001; on
// success, exits to the catalog home (CATALOG's own IA, out of scope here).
function VerifyForm() {
  const router = useRouter();
  const email = useSearchParams().get("email") ?? "";
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(60);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => setCooldown((s) => s - 1), 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  async function handleVerify() {
    setLoading(true);
    setError(null);
    try {
      await apiFetch("/v1/auth/otp/verify", {
        method: "POST",
        body: JSON.stringify({ email, code, role: "end_user" }),
      });
      router.push("/"); // CATALOG's own home, out of scope here
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("That code isn't right. Please try again.");
        setCode("");
      } else if (err instanceof ApiError && err.status === 410) {
        setError("That code has expired. Request a new one below.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    setCooldown(60);
    setError(null);
    await apiFetch("/v1/auth/otp/request", {
      method: "POST",
      body: JSON.stringify({ email, role: "end_user" }),
    });
  }

  return (
    <div>
      <p className="eyebrow">Verify your email</p>
      <h1>Enter your code</h1>
      <p>
        We sent a 6-digit code to <strong>{email}</strong>.
      </p>
      <OtpInput value={code} onChange={setCode} error={Boolean(error)} disabled={loading} />
      <Button onClick={handleVerify} loading={loading} disabled={code.length < 6}>
        Verify &amp; continue
      </Button>
      <Button variant="ghost" onClick={handleResend} disabled={cooldown > 0}>
        {cooldown > 0 ? `Resend code in ${cooldown}s` : "Resend code"}
      </Button>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={null}>
      <VerifyForm />
    </Suspense>
  );
}
