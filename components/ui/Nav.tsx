'use client';

import { useEffect, useState } from 'react';

const LINKS = ['Philosophy', 'Method', 'Results', 'Apply'] as const;

export default function Nav() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 80);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 px-8 md:px-14 py-6 flex items-center justify-between transition-all duration-700"
      style={{
        background: scrolled ? 'rgba(3,3,10,0.9)' : 'transparent',
        backdropFilter: scrolled ? 'blur(16px)' : 'none',
        borderBottom: scrolled
          ? '1px solid rgba(201,160,48,0.12)'
          : '1px solid transparent',
      }}
    >
      {/* Wordmark */}
      <a
        href="#"
        className="text-sm font-extralight tracking-[0.35em] text-white/90"
      >
        CHIMERA<span style={{ color: '#C9A030' }}>SHIELD</span>
      </a>

      {/* Nav links */}
      <nav className="hidden md:flex items-center gap-10">
        {LINKS.map((item) => (
          <a
            key={item}
            href={`#${item.toLowerCase()}`}
            className="text-[10px] tracking-[0.45em] uppercase text-white/35 hover:text-white/75 transition-colors duration-300"
          >
            {item}
          </a>
        ))}
      </nav>

      {/* CTA */}
      <a
        href="#apply"
        className="text-[10px] tracking-[0.45em] uppercase px-5 py-2.5 transition-all duration-300"
        style={{
          border: '1px solid rgba(201,160,48,0.35)',
          color: 'rgba(201,160,48,0.75)',
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.borderColor =
            'rgba(201,160,48,0.9)';
          (e.currentTarget as HTMLElement).style.color = 'rgba(201,160,48,1)';
          (e.currentTarget as HTMLElement).style.background =
            'rgba(201,160,48,0.06)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.borderColor =
            'rgba(201,160,48,0.35)';
          (e.currentTarget as HTMLElement).style.color =
            'rgba(201,160,48,0.75)';
          (e.currentTarget as HTMLElement).style.background = 'transparent';
        }}
      >
        Apply Now
      </a>
    </header>
  );
}
