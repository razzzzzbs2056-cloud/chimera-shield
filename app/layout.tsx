import type { Metadata } from 'next';
import './globals.css';
import Nav from '@/components/ui/Nav';

export const metadata: Metadata = {
  title: 'ChimeraShield — Neural Performance Intelligence',
  description:
    'Elite performance and equity-building for founders, executives, and wealth architects.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased" style={{ background: '#03030A' }}>
        <Nav />
        {children}
      </body>
    </html>
  );
}
