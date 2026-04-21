import ScrollReveal from '@/components/ui/ScrollReveal';

const PILLARS = [
  {
    number: '01',
    title: 'Neural Architecture',
    subtitle: 'Cognitive Rewiring',
    body: 'We map your existing decision frameworks, identify latent bottlenecks, and install high-leverage mental models drawn from neuroscience, game theory, and elite operator psychology. The result: faster pattern recognition, cleaner signal isolation, and compounding cognitive output.',
    icon: (
      <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
        <circle cx="18" cy="18" r="2" fill="#C9A030" opacity="0.9" />
        <circle cx="8" cy="10" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="28" cy="10" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="6" cy="24" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="30" cy="24" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="18" cy="30" r="1.5" fill="#C9A030" opacity="0.5" />
        <line x1="18" y1="18" x2="8" y2="10" stroke="#C9A030" strokeWidth="0.6" opacity="0.35" />
        <line x1="18" y1="18" x2="28" y2="10" stroke="#C9A030" strokeWidth="0.6" opacity="0.35" />
        <line x1="18" y1="18" x2="6" y2="24" stroke="#C9A030" strokeWidth="0.6" opacity="0.35" />
        <line x1="18" y1="18" x2="30" y2="24" stroke="#C9A030" strokeWidth="0.6" opacity="0.35" />
        <line x1="18" y1="18" x2="18" y2="30" stroke="#C9A030" strokeWidth="0.6" opacity="0.35" />
        <line x1="8" y1="10" x2="28" y2="10" stroke="#C9A030" strokeWidth="0.4" opacity="0.2" />
        <line x1="6" y1="24" x2="30" y2="24" stroke="#C9A030" strokeWidth="0.4" opacity="0.2" />
      </svg>
    ),
  },
  {
    number: '02',
    title: 'Somatic Performance',
    subtitle: 'Physical Sovereignty',
    body: 'Peak cognitive output demands a biological substrate engineered for sustained performance. We build bespoke physical protocols — recovery architecture, hormonal optimisation, and sleep engineering — calibrated to the demands of elite executive function and high-stakes decision-making.',
    icon: (
      <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
        <path d="M18 4 L18 32" stroke="#C9A030" strokeWidth="0.7" opacity="0.3" />
        <path d="M4 18 L32 18" stroke="#C9A030" strokeWidth="0.7" opacity="0.3" />
        <circle cx="18" cy="18" r="10" stroke="#C9A030" strokeWidth="0.8" opacity="0.4" fill="none" />
        <circle cx="18" cy="18" r="5" stroke="#C9A030" strokeWidth="0.8" opacity="0.6" fill="none" />
        <circle cx="18" cy="18" r="1.8" fill="#C9A030" opacity="0.9" />
      </svg>
    ),
  },
  {
    number: '03',
    title: 'Capital Engineering',
    subtitle: 'Equity Architecture',
    body: 'Wealth is not accumulated — it is constructed. We architect asymmetric equity positions, structure capital vehicles with embedded optionality, and engineer liquidity pathways that compound silently while you operate at the edge of your zone. Income is rented. Equity is owned.',
    icon: (
      <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
        <polyline
          points="4,28 10,20 16,23 22,12 28,15 34,6"
          stroke="#C9A030"
          strokeWidth="1"
          fill="none"
          opacity="0.7"
        />
        <circle cx="4" cy="28" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="10" cy="20" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="16" cy="23" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="22" cy="12" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="28" cy="15" r="1.5" fill="#C9A030" opacity="0.5" />
        <circle cx="34" cy="6" r="2" fill="#C9A030" opacity="0.9" />
        <line x1="4" y1="31" x2="4" y2="33" stroke="#C9A030" strokeWidth="0.6" opacity="0.3" />
        <line x1="10" y1="31" x2="10" y2="33" stroke="#C9A030" strokeWidth="0.6" opacity="0.3" />
        <line x1="16" y1="31" x2="16" y2="33" stroke="#C9A030" strokeWidth="0.6" opacity="0.3" />
        <line x1="22" y1="31" x2="22" y2="33" stroke="#C9A030" strokeWidth="0.6" opacity="0.3" />
        <line x1="28" y1="31" x2="28" y2="33" stroke="#C9A030" strokeWidth="0.6" opacity="0.3" />
        <line x1="34" y1="31" x2="34" y2="33" stroke="#C9A030" strokeWidth="0.6" opacity="0.3" />
      </svg>
    ),
  },
] as const;

export default function Pillars() {
  return (
    <section
      id="method"
      className="w-full py-36 md:py-48 px-8 md:px-20"
      style={{ background: '#03030A' }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <ScrollReveal>
          <div className="mb-20 md:mb-28">
            <p
              className="text-[10px] tracking-[0.65em] uppercase mb-5"
              style={{ color: 'rgba(201,160,48,0.55)' }}
            >
              The Method
            </p>
            <h2
              className="text-4xl md:text-5xl font-extralight tracking-tight"
              style={{ color: 'rgba(255,255,255,0.88)' }}
            >
              Three pillars.
              <br />
              One integrated system.
            </h2>
          </div>
        </ScrollReveal>

        {/* Pillar cards — pure CSS hover via Tailwind */}
        <div className="grid md:grid-cols-3 gap-0.5">
          {PILLARS.map((pillar, i) => (
            <ScrollReveal key={pillar.number} delay={i * 120}>
              <div className="group relative p-10 md:p-12 h-full flex flex-col border border-white/[0.05] bg-white/[0.012] hover:bg-[#C9A030]/[0.04] hover:border-[#C9A030]/[0.18] transition-all duration-700 cursor-default">
                {/* Number */}
                <span
                  className="text-[11px] tracking-[0.5em] font-light mb-8 block"
                  style={{ color: 'rgba(201,160,48,0.35)' }}
                >
                  {pillar.number}
                </span>

                {/* Icon */}
                <div className="mb-8">{pillar.icon}</div>

                {/* Title */}
                <h3
                  className="text-xl font-light tracking-wide mb-2"
                  style={{ color: 'rgba(255,255,255,0.88)' }}
                >
                  {pillar.title}
                </h3>
                <p
                  className="text-[10px] tracking-[0.45em] uppercase mb-7"
                  style={{ color: 'rgba(201,160,48,0.5)' }}
                >
                  {pillar.subtitle}
                </p>

                {/* Body */}
                <p
                  className="text-sm font-light leading-relaxed mt-auto"
                  style={{ color: 'rgba(255,255,255,0.38)' }}
                >
                  {pillar.body}
                </p>

                {/* Bottom accent — visible on hover */}
                <div
                  className="absolute bottom-0 left-10 right-10 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-700"
                  style={{ background: 'rgba(201,160,48,0.3)' }}
                />
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
