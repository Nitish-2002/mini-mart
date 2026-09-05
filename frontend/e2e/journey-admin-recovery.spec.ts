import { test, expect, lastEmailTo, extractResetToken } from "./fixtures";

const ADMIN_RECOVERY_EMAIL = "e2e-admin@example.com";
const NEW_PASSWORD = "a-brand-new-e2e-password-123";

// TEST-AUTH-032: journey-admin-recovery (experience-design.md#user-journeys)
// ds-auth-008 -> emailed link -> ds-auth-009 -> new password -> login; the
// used link revisited lands on ds-auth-010.
test("Admin resets their password and logs in with the new one", async ({ page }) => {
  await page.goto("/admin/reset");
  await page.getByLabel("Recovery email").fill(ADMIN_RECOVERY_EMAIL);
  await page.getByRole("button", { name: "Send reset link" }).click();
  await expect(page.getByText("Check your email")).toBeVisible();

  const sentEmail = await lastEmailTo(ADMIN_RECOVERY_EMAIL);
  const token = extractResetToken(sentEmail.text);

  await page.goto(`/admin/reset/confirm?token=${token}`);
  await page.getByLabel("New password", { exact: true }).fill(NEW_PASSWORD);
  await page.getByLabel("Confirm new password").fill(NEW_PASSWORD);
  await page.getByRole("button", { name: "Set new password" }).click();
  await page.waitForURL("/admin");

  // The new password actually works for a fresh login (a new browsing
  // context — the confirm step above already left a live session cookie,
  // and this proves the *credential* itself, not just that session).
  const freshContext = await page.context().browser()!.newContext();
  const freshPage = await freshContext.newPage();
  await freshPage.goto("/admin/login");
  await freshPage.getByLabel("Username").fill("e2e_admin");
  await freshPage.getByLabel("Password").fill(NEW_PASSWORD);
  await freshPage.getByRole("button", { name: "Sign in" }).click();
  await freshPage.waitForURL("/admin");
  await freshContext.close();
});

test("revisiting a used reset link shows the expired/used state", async ({ page }) => {
  await page.goto("/admin/reset");
  await page.getByLabel("Recovery email").fill(ADMIN_RECOVERY_EMAIL);
  await page.getByRole("button", { name: "Send reset link" }).click();

  const sentEmail = await lastEmailTo(ADMIN_RECOVERY_EMAIL);
  const token = extractResetToken(sentEmail.text);

  await page.goto(`/admin/reset/confirm?token=${token}`);
  await page.getByLabel("New password", { exact: true }).fill(NEW_PASSWORD);
  await page.getByLabel("Confirm new password").fill(NEW_PASSWORD);
  await page.getByRole("button", { name: "Set new password" }).click();
  await page.waitForURL("/admin");

  // Revisiting the SAME link after it's already been used.
  await page.goto(`/admin/reset/confirm?token=${token}`);
  await page.getByLabel("New password", { exact: true }).fill("yet-another-password-456");
  await page.getByLabel("Confirm new password").fill("yet-another-password-456");
  await page.getByRole("button", { name: "Set new password" }).click();
  await expect(page.getByText("This link has expired")).toBeVisible();
});
