import type { Metadata } from "next";
import { Fredoka, Inter } from "next/font/google";
import "./globals.css";

// decision-61: Inter is the body/UI typeface everywhere. Fredoka (CR-006) is
// the wordmark/display face only — never used for body copy.
const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const fredoka = Fredoka({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "600"],
});

export const metadata: Metadata = {
  title: "Mini Mart",
  description: "Online ordering and cash-on-delivery for your neighbourhood mart.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${fredoka.variable}`}>{children}</body>
    </html>
  );
}
