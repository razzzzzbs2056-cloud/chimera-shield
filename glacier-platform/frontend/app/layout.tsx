import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Himalayan Glacier Intelligence",
  description:
    "Cryosphere intelligence & early-warning platform — Nepal–Tibet border. Experimental hazard indicators, not official warnings.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="topbar">
          <div>
            <h1>
              <span className="brand-dot" />
              HIMALAYAN CRYOSPHERE INTELLIGENCE
            </h1>
            <div className="sub">
              Nepal–Tibet border · continuous glacier monitoring · evidence-grounded
            </div>
          </div>
          <div className="sub">
            <a href="/">OVERVIEW</a> &nbsp;·&nbsp; <a href="/about">METHOD & INTEGRITY</a>
          </div>
        </div>
        {children}
      </body>
    </html>
  );
}
