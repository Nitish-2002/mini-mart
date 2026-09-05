import { test, expect, lastEmailTo, extractOtpCode } from "./fixtures";

// TEST-AUTH-030: journey-enduser-signin (experience-design.md#user-journeys)
// ds-auth-001 -> ds-auth-002 with a valid code, plus the wrong-code and
// rate-limited detours as sub-cases.

test("End User signs in with a valid code and lands authenticated", async ({ page }) => {
  const email = `enduser-${Date.now()}@example.com`;

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByRole("button", { name: "Send code" }).click();
  await expect(page).toHaveURL(/\/login\/verify/);

  const sentEmail = await lastEmailTo(email);
  const code = extractOtpCode(sentEmail.text);

  await page.getByLabel("Digit 1 of 6").click();
  await page.keyboard.type(code);
  await page.getByRole("button", { name: "Verify & continue" }).click();

  // No storefront home exists yet (CATALOG isn't built) — "/" is this
  // module's own best redirect target, so the session cookie itself is
  // the real proxy for "lands authenticated," not a specific page.
  await page.waitForURL("/");
  const cookies = await page.context().cookies();
  expect(cookies.find((c) => c.name === "session_token")).toBeTruthy();
});

test("a wrong code shows an inline error without losing the screen", async ({ page }) => {
  const email = `enduser-wrong-${Date.now()}@example.com`;

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByRole("button", { name: "Send code" }).click();
  await expect(page).toHaveURL(/\/login\/verify/);

  await page.getByLabel("Digit 1 of 6").click();
  await page.keyboard.type("000000");
  await page.getByRole("button", { name: "Verify & continue" }).click();

  await expect(page.getByText("That code isn't right. Please try again.")).toBeVisible();
  await expect(page).toHaveURL(/\/login\/verify/); // stays on the same screen
});

test("requesting too many codes shows the rate-limited state", async ({ page, request }) => {
  const email = `enduser-limited-${Date.now()}@example.com`;

  // 5/hour (decision-53): the first 5 are driven directly against the
  // backend (fast, deterministic) — a UI loop's .click() doesn't wait for
  // the async request it triggers, so navigating away right after risks
  // silently dropping some of the 6 intended requests mid-flight. Only the
  // 6th (the one that actually trips ds-auth-003) goes through the real UI.
  for (let i = 0; i < 5; i++) {
    const res = await request.post("http://localhost:8000/v1/auth/otp/request", {
      data: { email, role: "end_user" },
    });
    expect(res.status()).toBe(202);
  }

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByRole("button", { name: "Send code" }).click();

  await expect(page.getByText("Too many attempts")).toBeVisible();
});
