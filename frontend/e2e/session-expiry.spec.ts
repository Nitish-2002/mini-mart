import { APIRequestContext } from "@playwright/test";
import { test, expect, getAgentIdByEmail, revokeSessionsForUser, lastEmailTo, extractOtpCode } from "./fixtures";

const BACKEND_URL = "http://localhost:8000";
const TEST_PHOTO = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
  "base64"
);

async function approveAgent(request: APIRequestContext, agentId: string) {
  const login = await request.post(`${BACKEND_URL}/v1/auth/admin/login`, {
    data: { username: "e2e_admin", password: "e2e-admin-password-not-real-12345678" },
  });
  const sessionToken = login.headers()["set-cookie"]?.match(/session_token=([^;]+)/)?.[1];
  await request.post(`${BACKEND_URL}/v1/auth/agent/${agentId}/status`, {
    data: { action: "approve" },
    headers: { cookie: `session_token=${sessionToken}` },
  });
}

// TEST-AUTH-033: an authenticated session with expires_at forced into the
// past, reload -> ds-auth-011 interrupts; re-authenticating returns to the
// same page rather than a generic landing page.
test("a lapsed session interrupts with ds-auth-011, not a silent redirect", async ({ page, request }) => {
  const email = `agent-expiry-${Date.now()}@example.com`;

  await page.goto("/agent/register");
  await page.getByLabel("Full name").fill("Cy Agent");
  await page.getByLabel("Phone number").fill("+15559999999");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Photo (selfie or ID)").setInputFiles({ name: "id.png", mimeType: "image/png", buffer: TEST_PHOTO });
  await page.getByRole("button", { name: "Submit application" }).click();
  await expect(page).toHaveURL(/\/agent\/register\/submitted/); // waits for the registration POST to actually resolve

  const agentId = await getAgentIdByEmail(email);
  await approveAgent(request, agentId);

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

  await revokeSessionsForUser(agentId);
  await page.reload();

  await expect(page.getByText("Your session has expired")).toBeVisible();
  await page.getByRole("button", { name: "Sign in again" }).click();
  await expect(page).toHaveURL(/\/agent\/login\?returnTo=%2Fagent%2Fstatus/);
});
