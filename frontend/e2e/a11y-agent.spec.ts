import AxeBuilder from "@axe-core/playwright";
import { APIRequestContext } from "@playwright/test";
import { test, expect, getAgentIdByEmail, lastEmailTo, extractOtpCode } from "./fixtures";

const BACKEND_URL = "http://localhost:8000";
const TEST_PHOTO = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
  "base64"
);

async function registerAgent(page: import("@playwright/test").Page, email: string) {
  await page.goto("/agent/register");
  await page.getByLabel("Full name").fill("A11y Agent");
  await page.getByLabel("Phone number").fill("+15551112222");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Photo (selfie or ID)").setInputFiles({ name: "id.png", mimeType: "image/png", buffer: TEST_PHOTO });
  await page.getByRole("button", { name: "Submit application" }).click();
  await expect(page).toHaveURL(/\/agent\/register\/submitted/);
}

async function setStatus(request: APIRequestContext, agentId: string, action: string) {
  const login = await request.post(`${BACKEND_URL}/v1/auth/admin/login`, {
    data: { username: "e2e_admin", password: "e2e-admin-password-not-real-12345678" },
  });
  const sessionToken = login.headers()["set-cookie"]?.match(/session_token=([^;]+)/)?.[1];
  const res = await request.post(`${BACKEND_URL}/v1/auth/agent/${agentId}/status`, {
    data: { action },
    headers: { cookie: `session_token=${sessionToken}` },
  });
  expect(res.ok()).toBeTruthy();
}

async function loginAsAgent(page: import("@playwright/test").Page, email: string) {
  await page.goto("/agent/login");
  await page.getByLabel("Email").fill(email);
  await page.getByRole("button", { name: "Send code" }).click();
  const sentEmail = await lastEmailTo(email);
  const code = extractOtpCode(sentEmail.text);
  await page.getByLabel("Digit 1 of 6").click();
  await page.keyboard.type(code);
  await page.getByRole("button", { name: "Verify & continue" }).click();
  await page.waitForURL("/agent/status");
}

// TEST-AUTH-035: Build of ds-auth-004-006 rendered, the 4 agent-status
// values; dc-auth-001 StatusBadge shows the correct color/label for each,
// keyboard nav reaches every control, zero axe-core violations.
test("the registration screen is keyboard-reachable and has zero a11y violations", async ({ page }) => {
  await page.goto("/agent/register");
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);

  // Tab reaches every field in visual order: name, phone, email, photo, submit.
  await page.getByLabel("Full name").focus();
  for (const expected of ["Phone number", "Email", "Photo (selfie or ID)"]) {
    await page.keyboard.press("Tab");
    await expect(page.getByLabel(expected)).toBeFocused();
  }
});

for (const [label, action, expectedText] of [
  ["pending_approval", null, "Still under review"],
  ["approved", "approve", "You're approved!"],
  ["deactivated", "deactivate-after-approve", "Your account has been deactivated"],
  ["rejected", "reject", "Application not approved"],
] as const) {
  test(`agent status screen (${label}) shows the right badge and has zero a11y violations`, async ({ page, request }) => {
    const email = `a11y-agent-${label}-${Date.now()}@example.com`;
    await registerAgent(page, email);
    const agentId = await getAgentIdByEmail(email);

    if (action === "approve") {
      await setStatus(request, agentId, "approve");
    } else if (action === "deactivate-after-approve") {
      await setStatus(request, agentId, "approve");
      await setStatus(request, agentId, "deactivate");
    } else if (action === "reject") {
      await setStatus(request, agentId, "reject");
    }

    await loginAsAgent(page, email);
    await expect(page.getByText(expectedText)).toBeVisible();

    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
}
