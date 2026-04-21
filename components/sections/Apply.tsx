'use client';

import ScrollReveal from '@/components/ui/ScrollReveal';
import { useState } from 'react';

export default function Apply() {
  const [submitted, setSubmitted] = useState(false);

  return (
    <section
      id="apply"
      className="relative w-full py-40 md:py-56 px-8 md:px-20 overflow-hidden"
      style={{ background: '#04040C' }}
    >
      {/* Background radial */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse at 50% 40%, rgba(201,160,48,0.07) 0%, transparent 60%)',
        }}
      />

      {/* Top border accent */}
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background:
            'linear-gradient(to right, transparent, rgba(201,160,48,0.3) 30%, rgba(201,160,48,0.3) 70%, transparent)',
        }}
      />

      <div className="max-w-3xl mx-auto relative text-center">
        <ScrollReveal>
          <p
            className="text-[10px] tracking-[0.65em] uppercase mb-6"
            style={{ color: 'rgba(201,160,48,0.55)' }}
          >
            Applications Open
          </p>

          <h2
            className="text-5xl md:text-7xl font-extralight tracking-tight leading-[1.1] mb-6"
            style={{ color: 'rgba(255,255,255,0.9)' }}
          >
            Q3 2026
            <br />
            <span style={{ color: '#C9A030' }}>Cohort</span>
          </h2>

          <p
            className="text-sm tracking-widest uppercase mb-3"
            style={{ color: 'rgba(255,255,255,0.25)' }}
          >
            12 seats · 90-day full-system transformation
          </p>

          <p
            className="text-base font-light leading-relaxed mt-8 mb-14 max-w-xl mx-auto"
            style={{ color: 'rgba(255,255,255,0.4)' }}
          >
            Each cohort accepts a strict maximum of twelve principals. The
            application is not a formality — it is the first filter. We do
            not work with everyone, and that is by design.
          </p>
        </ScrollReveal>

        {!submitted ? (
          <ScrollReveal delay={200}>
            <form
              className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto"
              onSubmit={(e) => {
                e.preventDefault();
                setSubmitted(true);
              }}
            >
              <input
                type="email"
                required
                placeholder="your@email.com"
                className="flex-1 px-5 py-4 text-sm font-light tracking-wide bg-transparent outline-none placeholder:text-white/20 text-white/80"
                style={{ border: '1px solid rgba(255,255,255,0.1)' }}
              />
              <button
                type="submit"
                className="px-8 py-4 text-[10px] tracking-[0.5em] uppercase font-light whitespace-nowrap transition-all duration-300"
                style={{
                  background: 'rgba(201,160,48,0.14)',
                  border: '1px solid rgba(201,160,48,0.5)',
                  color: 'rgba(201,160,48,0.9)',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.background =
                    'rgba(201,160,48,0.25)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.background =
                    'rgba(201,160,48,0.14)';
                }}
              >
                Request Access
              </button>
            </form>

            <p
              className="text-[10px] tracking-wider mt-5"
              style={{ color: 'rgba(255,255,255,0.18)' }}
            >
              Qualified applicants receive a private briefing within 48 hours.
            </p>
          </ScrollReveal>
        ) : (
          <ScrollReveal>
            <div
              className="inline-block px-10 py-6"
              style={{ border: '1px solid rgba(201,160,48,0.3)' }}
            >
              <p
                className="text-sm tracking-[0.4em] uppercase"
                style={{ color: 'rgba(201,160,48,0.8)' }}
              >
                Application received.
              </p>
              <p
                className="text-[10px] tracking-wider mt-2"
                style={{ color: 'rgba(255,255,255,0.25)' }}
              >
                Expect a private briefing within 48 hours.
              </p>
            </div>
          </ScrollReveal>
        )}
      </div>
    </section>
  );
}
