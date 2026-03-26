import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChimeraShield — AI Cybersecurity",
  description: "AI-powered cybersecurity for small and medium businesses.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
