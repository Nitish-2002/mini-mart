import { EmailEntryScreen } from "@/components/auth/EmailEntryScreen";

// ds-auth-001, agent context, at /agent/login (CR-007) — the same reused
// screen End User gets, for an already-registered, approved agent.
export default function AgentLoginPage() {
  return (
    <EmailEntryScreen
      role="delivery_agent"
      verifyPath="/agent/login/verify"
      heading="Sign in to deliver"
      intro="Enter your email and we'll send you a one-time code."
    />
  );
}
