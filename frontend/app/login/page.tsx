import { EmailEntryScreen } from "@/components/auth/EmailEntryScreen";

export default function LoginPage() {
  return (
    <EmailEntryScreen
      role="end_user"
      verifyPath="/login/verify"
      heading="Welcome to Mini Mart"
      intro="Enter your email and we'll send you a one-time code — no password to remember."
    />
  );
}
