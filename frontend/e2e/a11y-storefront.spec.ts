import AxeBuilder from "@axe-core/playwright";
import { test, expect, lastEmailTo, extractOtpCode } from "./fixtures";

// TEST-AUTH-034: Build of ds-auth-001-003 rendered; complete signup using
// only keyboard (Tab/Enter); paste a full 6-digit code into the OTP input
// (decision-64); zero axe-core violations at metric-a11y-contrast's 4.5:1.
test("End User signup completes keyboard-only, with a pasted OTP code, zero a11y violations", async ({ page }) => {
  const email = `a11y-storefront-${Date.now()}@example.com`;

  await page.goto("/login");
  const emailInput = page.getByLabel("Email");
  await emailInput.focus(); // .focus(), not .click() — no mouse anywhere in this test
  await page.keyboard.type(email);
  await page.keyboard.press("Tab"); // -> the submit button (only one other focusable control)
  await page.keyboard.press("Enter");

  await expect(page).toHaveURL(/\/login\/verify/);
  const axeEmailScreen = await new AxeBuilder({ page }).analyze();
  expect(axeEmailScreen.violations).toEqual([]);

  const sentEmail = await lastEmailTo(email);
  const code = extractOtpCode(sentEmail.text);

  // decision-64: paste a full code into the first box, filling all 6.
  const firstBox = page.getByLabel("Digit 1 of 6");
  await firstBox.focus();
  await firstBox.evaluate((el: HTMLInputElement, pastedCode: string) => {
    const dataTransfer = new DataTransfer();
    dataTransfer.setData("text", pastedCode);
    el.dispatchEvent(new ClipboardEvent("paste", { clipboardData: dataTransfer, bubbles: true, cancelable: true }));
  }, code);

  for (let i = 0; i < 6; i++) {
    await expect(page.getByLabel(`Digit ${i + 1} of 6`)).toHaveValue(code[i]);
  }

  // Tab to "Verify & continue" (the OTP group counts as one stop) and submit.
  await page.keyboard.press("Tab");
  await page.keyboard.press("Enter");
  await page.waitForURL("/");

  const cookies = await page.context().cookies();
  expect(cookies.find((c) => c.name === "session_token")).toBeTruthy();
});

test("the OTP entry screen has zero axe-core violations", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(`a11y-otp-${Date.now()}@example.com`);
  await page.getByRole("button", { name: "Send code" }).click();
  await expect(page).toHaveURL(/\/login\/verify/);

  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
