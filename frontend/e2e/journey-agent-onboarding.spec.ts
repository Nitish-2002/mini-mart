import { APIRequestContext } from "@playwright/test";
import { test, expect, getAgentIdByEmail, lastEmailTo, extractOtpCode } from "./fixtures";

const BACKEND_URL = "http://localhost:8000";
const TEST_PHOTO = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
  "base64"
);

async function registerAgent(page: import("@playwright/test").Page, email: string, name: string) {
  await page.goto("/agent/register");
  await page.getByLabel("Full name").fill(name);
  await page.getByLabel("Phone number").fill("+15551234567");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Photo (selfie or ID)").setInputFiles({
    name: "id.png",
    mimeType: "image/png",
    buffer: TEST_PHOTO,
  });
  await page.getByRole("button", { name: "Submit application" }).click();
  await expect(page).toHaveURL(/\/agent\/register\/submitted/);
}

/** Drives an Admin agent-status transition directly against the backend —
 * no admin agent-management UI exists yet (deferred, per this module's own
 * decision budget: "raise a design CR when frontend work reaches it"), so
 * this is the "or real backend data" option TEST-AUTH-031's own Data column
 * explicitly allows in place of a state-switcher. Uses request, not page, so
 * the admin session cookie never collides with the agent's own session
 * cookie in the same browser context. */
async function adminSetAgentStatus(request: APIRequestContext, agentId: string, action: string) {
  const login = await request.post(`${BACKEND_URL}/v1/auth/admin/login`, {
    data: { username: "e2e_admin", password: "e2e-admin-password-not-real-12345678" },
  });
  expect(login.ok()).toBeTruthy();
  const cookie = login.headers()["set-cookie"];
  const sessionToken = cookie?.match(/session_token=([^;]+)/)?.[1];

  const update = await request.post(`${BACKEND_URL}/v1/auth/agent/${agentId}/status`, {
    data: { action },
    headers: { cookie: `session_token=${sessionToken}` },
  });
  expect(update.ok()).toBeTruthy();
}

// TEST-AUTH-031: journey-agent-onboarding (experience-design.md#user-journeys)
// ds-auth-004 -> ds-auth-005 -> Admin approves -> agent logs in via OTP ->
// reaches an approved-only view; a parallel rejected sub-case ends at
// ds-auth-006's rejected state.
test("a registered agent is approved and reaches the approved view", async ({ page, request }) => {
  const email = `agent-approve-${Date.now()}@example.com`;
  await registerAgent(page, email, "Ada Agent");

  const agentId = await getAgentIdByEmail(email);
  await adminSetAgentStatus(request, agentId, "approve");

  await page.goto("/agent/login");
  await page.getByLabel("Email").fill(email);
  await page.getByRole("button", { name: "Send code" }).click();
  const sentEmail = await lastEmailTo(email);
  const code = extractOtpCode(sentEmail.text);
  await page.getByLabel("Digit 1 of 6").click();
  await page.keyboard.type(code);
  await page.getByRole("button", { name: "Verify & continue" }).click();

  await page.waitForURL("/agent/status");
  await expect(page.getByText("You're approved!")).toBeVisible();
});

test("a rejected agent sees the rejected state, not the approved one", async ({ page, request }) => {
  const email = `agent-reject-${Date.now()}@example.com`;
  await registerAgent(page, email, "Bo Agent");

  const agentId = await getAgentIdByEmail(email);
  await adminSetAgentStatus(request, agentId, "reject");

  // A rejected agent still has a registered row, so OTP verify still
  // succeeds and issues a session (services.py's find-only lookup doesn't
  // gate on status) — sm-auth-agent-status only blocks them from ever
  // reaching "approved", never from signing in at all; /agent/status is
  // what actually shows them the rejected outcome.
  await page.goto("/agent/login");
  await page.getByLabel("Email").fill(email);
  await page.getByRole("button", { name: "Send code" }).click();
  const sentEmail = await lastEmailTo(email);
  const code = extractOtpCode(sentEmail.text);
  await page.getByLabel("Digit 1 of 6").click();
  await page.keyboard.type(code);
  await page.getByRole("button", { name: "Verify & continue" }).click();

  await page.waitForURL("/agent/status");
  await expect(page.getByText("Application not approved")).toBeVisible();
});
