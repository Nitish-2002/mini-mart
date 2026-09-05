import AxeBuilder from "@axe-core/playwright";
import { test, expect, lastEmailTo, extractResetToken } from "./fixtures";

const ADMIN_RECOVERY_EMAIL = "e2e-admin@example.com";

// TEST-AUTH-036: Build of ds-auth-007-010 rendered, Admin login + recovery
// flow; complete both using only keyboard; focus order matches visual
// top-to-bottom reading order; zero axe-core violations.
test("Admin logs in keyboard-only, focus order matches visual order, zero a11y violations", async ({ page }) => {
  await page.goto("/admin/login");
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);

  await page.getByLabel("Username").focus();
  await expect(page.getByLabel("Username")).toBeFocused();
  await page.keyboard.type("e2e_admin");
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Password")).toBeFocused(); // matches the visual username-then-password order
  await page.keyboard.type("e2e-admin-password-not-real-12345678");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Sign in" })).toBeFocused();
  await page.keyboard.press("Enter");

  await page.waitForURL("/admin");
});

test("Admin's password-recovery request and confirm screens have zero a11y violations", async ({ page }) => {
  await page.goto("/admin/reset");
  let results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);

  await page.getByLabel("Recovery email").focus();
  await page.keyboard.type(ADMIN_RECOVERY_EMAIL);
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Send reset link" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByText("Check your email")).toBeVisible();

  const sentEmail = await lastEmailTo(ADMIN_RECOVERY_EMAIL);
  const token = extractResetToken(sentEmail.text);
  await page.goto(`/admin/reset/confirm?token=${token}`);

  results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);

  await page.getByLabel("New password", { exact: true }).focus();
  await page.keyboard.type("a-fully-keyboard-driven-password-1");
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Confirm new password")).toBeFocused();
  await page.keyboard.type("a-fully-keyboard-driven-password-1");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Set new password" })).toBeFocused();
  await page.keyboard.press("Enter");
  await page.waitForURL("/admin");
});
