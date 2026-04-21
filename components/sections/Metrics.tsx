import ScrollReveal from '@/components/ui/ScrollReveal';

const STATS = [
  { value: '$2.4B+', label: 'Equity Created', sub: 'across active partnerships' },
  { value: '347', label: 'Transformations', sub: 'founders & executives' },
  { value: '94%', label: 'Hit Milestones', sub: 'within 12 months' },
  { value: '6.2×', label: 'Average ROI', sub: 'on invested capital' },
] as const;

export default function Metrics() {
  return (
    <section
      id="results"
      className="w-full py-36 md:py-48 px-8 md:px-20 relative overflow-hidden"
      style={{ background: '#04040C' }}
    >
      {/* Faint radial glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse at 50% 50%, rgba(201,160,48,0.04) 0%, transparent 65%)',
        }}
      />

      <div className="max-w-6xl mx-auto relative">
        <ScrollReveal>
          <div className="mb-20 md:mb-28 text-center">
            <p
              className="text-[10px] tracking-[0.65em] uppercase mb-5"
              style={{ color: 'rgba(201,160,48,0.55)' }}
            >
              The Results
            </p>
            <h2
              className="text-4xl md:text-5xl font-extralight tracking-tight"
              style={{ color: 'rgba(255,255,255,0.88)' }}
            >
              Numbers that don&apos;t lie.
            </h2>
          </div>
        </ScrollReveal>

        {/* Stats grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px">
          {STATS.map((stat, i) => (
            <ScrollReveal key={stat.label} delay={i * 100}>
              <div
                className="flex flex-col items-center text-center py-14 px-6"
                style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}
              >
                <span
                  className="text-5xl md:text-6xl font-thin tracking-tighter mb-3"
                  style={{ color: '#C9A030' }}
                >
                  {stat.value}
                </span>
                <span
                  className="text-xs tracking-[0.4em] uppercase mb-2"
                  style={{ color: 'rgba(255,255,255,0.6)' }}
                >
                  {stat.label}
                </span>
                <span
                  className="text-[10px] tracking-wider"
                  style={{ color: 'rgba(255,255,255,0.22)' }}
                >
                  {stat.sub}
                </span>
              </div>
            </ScrollReveal>
          ))}
        </div>

        {/* Divider rule */}
        <div
          className="mt-20 h-px w-full"
          style={{
            background:
              'linear-gradient(to right, transparent, rgba(201,160,48,0.25) 30%, rgba(201,160,48,0.25) 70%, transparent)',
          }}
        />
      </div>
    </section>
  );
}
