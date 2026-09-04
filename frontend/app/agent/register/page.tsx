"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ErrorStatePanel } from "@/components/shared/ErrorStatePanel";
import { apiFetch, ApiError } from "@/lib/api";

// ds-auth-004 (experience-design.md §4C) — registration form, including the
// photo-upload field (decision-65). Entry point for ss-auth-002.
//
// KNOWN GAP, not silently worked around: no direct-to-OBJECT_STORAGE (S3)
// upload endpoint exists anywhere in this project yet — trd.md's
// agent/register contract assumes the frontend already has a real URL by
// the time it calls this endpoint. Until that upload flow is built (a
// CATALOG-adjacent piece of shared infra, not planned in any current AUTH
// task), the chosen file is inlined as a data: URL and sent as photo_url
// directly. This satisfies the API contract's "a URL string" shape and
// keeps the screen genuinely usable end-to-end, but is not real object
// storage — flag before this goes anywhere near production.
export default function AgentRegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function readFileAsDataUrl(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!photoFile) return;
    setLoading(true);
    setError(null);
    try {
      const photo_url = await readFileAsDataUrl(photoFile);
      await apiFetch("/v1/auth/agent/register", {
        method: "POST",
        body: JSON.stringify({ name, phone, email, photo_url }),
      });
      router.push(`/agent/register/submitted?email=${encodeURIComponent(email)}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError("An application already exists for this email. Check its status instead.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  if (error) {
    return <ErrorStatePanel title="Couldn't submit" message={error} onRetry={() => setError(null)} />;
  }

  return (
    <form onSubmit={handleSubmit}>
      <p className="eyebrow">Become a delivery agent</p>
      <h1>Tell us about you</h1>
      <p>Admin reviews every application before you can start receiving deliveries.</p>
      <Input label="Full name" required value={name} onChange={(e) => setName(e.target.value)} />
      <Input
        label="Phone number"
        type="tel"
        required
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />
      <Input label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
      <Input
        label="Photo (selfie or ID)"
        type="file"
        accept="image/*"
        required
        onChange={(e) => setPhotoFile(e.target.files?.[0] ?? null)}
      />
      <Button type="submit" loading={loading}>
        Submit application
      </Button>
    </form>
  );
}
