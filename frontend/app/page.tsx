import { redirect } from "next/navigation";

// CATALOG's own storefront home isn't built yet — until then, the root path
// sends an unauthenticated visitor straight to sign-in (ss-auth-001's entry
// point), rather than showing an empty shell.
export default function RootPage() {
  redirect("/login");
}
