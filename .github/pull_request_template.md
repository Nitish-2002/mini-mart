## Summary

<!-- What changed and why -->

## Checklist

- [ ] Tests pass locally
- [ ] If this PR touches `backend/app/auth/**`: every new or changed secret
      comparison (OTP codes, reset tokens) uses `hmac.compare_digest`, never
      `==` or `is` (TEST-AUTH-003, TRD-AUTH-015 — a code-review property,
      not something CI can catch automatically)
