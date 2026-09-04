import { OtpVerifyScreen } from "@/components/auth/OtpVerifyScreen";

// ds-auth-002, agent context. Routes to /agent/status regardless of outcome
// — ORDERS' assigned-orders view (the real destination for an approved
// agent) doesn't exist yet, and /agent/status itself handles every status,
// approved included.
export default function AgentVerifyPage() {
  return <OtpVerifyScreen role="delivery_agent" homePath="/agent/status" />;
}
