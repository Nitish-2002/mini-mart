import { test as base, expect } from "@playwright/test";
import { readFileSync, existsSync } from "fs";
import { Client } from "pg";

const BACKEND_URL = "http://localhost:8000";
const OUTBOX_FILE = "C:/Users/Bhargav/OneDrive/Desktop/MINI MART/backend/.e2e-outbox.jsonl";
const DB_URL = "postgresql://minimart_test:lBR-NbByAPTFJpUuPURPBloo3WPiYk5v@localhost:5434/mini_mart_e2e";

/** Direct DB read for test-orchestration only (e.g. resolving an agent's id
 * to drive an admin status transition) — no admin agent-management UI or
 * list-agents endpoint exists yet (deferred, per this module's own scope),
 * so there's no HTTP-only way to get this value. Mirrors the same
 * direct-DB-read pattern the pytest suite already uses for its own setup. */
export async function getAgentIdByEmail(email: string): Promise<string> {
  const client = new Client({ connectionString: DB_URL });
  await client.connect();
  try {
    const result = await client.query("SELECT id FROM auth_delivery_agents WHERE email = $1", [email]);
    if (result.rows.length === 0) throw new Error(`no agent found for ${email}`);
    return result.rows[0].id as string;
  } finally {
    await client.end();
  }
}

/** TEST-AUTH-033 needs a session whose `exp` has genuinely lapsed, but that
 * claim lives inside the signed JWT itself (in an httpOnly cookie no test
 * code can rewrite) — 7 real days can't elapse in a test run either.
 * Revoking the DB-side session row instead produces the identical
 * observable 401 (system.md's Failure Shape: expired and revoked are
 * rejected the same way, by design), which is what this journey is
 * actually about — the interrupt, not which of the two causes triggered it. */
export async function revokeSessionsForUser(userId: string): Promise<void> {
  const client = new Client({ connectionString: DB_URL });
  await client.connect();
  try {
    await client.query("UPDATE auth_sessions SET revoked_at = now() WHERE user_id = $1", [userId]);
  } finally {
    await client.end();
  }
}

export const test = base.extend({
  // Every journey starts from the same clean, reseeded state — the
  // singleton Admin account and every dynamically-registered end
  // user/agent from a prior test would otherwise leak across tests
  // (workers: 1 keeps them sequential, but not isolated on its own).
  // eslint-plugin-react-hooks pattern-matches any parameter literally named
  // `use` as React's use() hook — this is Playwright's own fixture-runner
  // callback, unrelated; renaming it sidesteps the false positive.
  page: async ({ page }, runFixture) => {
    const res = await fetch(`${BACKEND_URL}/_test/reset`, { method: "POST" });
    if (!res.ok) throw new Error(`/_test/reset failed: ${res.status}`);
    await runFixture(page);
  },
});

export { expect };

type Outbox = { to: string[]; subject: string; text: string };

function readOutbox(): Outbox[] {
  if (!existsSync(OUTBOX_FILE)) return [];
  return readFileSync(OUTBOX_FILE, "utf-8")
    .split("\n")
    .filter(Boolean)
    .map((line) => JSON.parse(line) as Outbox);
}

/** The most recent email sent to `to`, waiting briefly for the
 * fire-and-forget send (trd.md 6a) to land in the outbox file. */
export async function lastEmailTo(to: string): Promise<Outbox> {
  for (let attempt = 0; attempt < 20; attempt++) {
    const matches = readOutbox().filter((entry) => entry.to.includes(to));
    if (matches.length > 0) return matches[matches.length - 1];
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`no email arrived for ${to} in the outbox`);
}

export function extractOtpCode(text: string): string {
  const match = text.match(/verification code is (\d{6})/);
  if (!match) throw new Error(`no OTP code found in: ${text}`);
  return match[1];
}

export function extractResetToken(text: string): string {
  const match = text.match(/token=(\S+)/);
  if (!match) throw new Error(`no reset token found in: ${text}`);
  return match[1];
}
