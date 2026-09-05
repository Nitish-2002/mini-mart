import AxeBuilder from "@axe-core/playwright";
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

// TEST-AUTH-037: Build of ds-auth-011/012 rendered; a forced session-expiry,
// a forced network failure; both states announced via aria-live (verified
// via the accessibility tree, not just visually), zero axe-core violations.
test("session-expiry (ds-auth-011) is announced via the accessibility tree, zero a11y violations", async ({
  page,
  request,
}) => {
  const email = `a11y-shared-expiry-${Date.now()}@example.com`;
  await page.goto("/agent/register");
  await page.getByLabel("Full name").fill("Dee Agent");
  await page.getByLabel("Phone number").fill("+15558887777");
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

  await revokeSessionsForUser(agentId);
  await page.reload();

  // role="alertdialog" + aria-modal + aria-live="assertive" — present in
  // the accessibility tree, not just visually rendered text.
  const dialog = page.getByRole("alertdialog");
  await expect(dialog).toBeVisible();
  await expect(dialog).toHaveAccessibleName("Your session has expired");

  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

test("a forced network failure shows the generic error state (ds-auth-012), zero a11y violations", async ({ page }) => {
  // Force a genuine network failure on the one authenticated GET this app
  // makes, rather than a handled 4xx — this is what actually reaches
  // app/error.tsx's boundary (a caught ApiError never throws during render).
  // No login needed: the route is intercepted client-side before the
  // request would ever reach the backend to be authenticated at all.
  await page.route("**/v1/auth/agent/status", (route) => route.abort("failed"));
  await page.goto("/agent/status");

  // Next.js dev mode injects its own role="alert" route announcer alongside
  // the real one — scope by content to get ErrorStatePanel's, not either.
  const alert = page.getByRole("alert").filter({ hasText: "Something went wrong" });
  await expect(alert).toBeVisible();

  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
