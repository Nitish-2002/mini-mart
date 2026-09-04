import { OtpVerifyScreen } from "@/components/auth/OtpVerifyScreen";

export default function VerifyPage() {
  // CATALOG's own storefront home isn't built yet — "/" is this module's
  // best available redirect target, out of AUTH's own scope beyond that.
  return <OtpVerifyScreen role="end_user" homePath="/" />;
}
