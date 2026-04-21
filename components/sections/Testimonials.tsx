import ScrollReveal from '@/components/ui/ScrollReveal';

const QUOTES = [
  {
    quote:
      'ChimeraShield didn\'t give me a framework — they gave me an operating system. In nine months I closed a Series B, restructured my cap table, and cut decision latency in half. The ROI is measurable. The transformation is permanent.',
    name: 'A.K.',
    role: 'Founder & CEO, Series B',
    sector: 'Deep Tech · $180M valuation',
  },
  {
    quote:
      'I came in thinking I needed better habits. I left with a completely rebuilt relationship to risk, capital, and time. The neural work was unlike anything in the executive coaching space — it is ruthlessly precise.',
    name: 'M.L.',
    role: 'Managing Partner',
    sector: 'Private Equity · $900M AUM',
  },
] as const;

export default function Testimonials() {
  return (
    <section
      className="w-full py-36 md:py-48 px-8 md:px-20"
      style={{ background: '#03030A' }}
    >
      <div className="max-w-5xl mx-auto">
        <ScrollReveal>
          <p
            className="text-[10px] tracking-[0.65em] uppercase mb-16 text-center"
            style={{ color: 'rgba(201,160,48,0.55)' }}
          >
            Partner Accounts
          </p>
        </ScrollReveal>

        <div className="space-y-1">
          {QUOTES.map((item, i) => (
            <ScrollReveal key={item.name} delay={i * 150}>
              <div
                className="relative p-12 md:p-16"
                style={{
                  border: '1px solid rgba(255,255,255,0.05)',
                  background: 'rgba(255,255,255,0.012)',
                }}
              >
                {/* Opening mark */}
                <div
                  className="absolute top-10 left-12 text-5xl font-thin leading-none"
                  style={{ color: 'rgba(201,160,48,0.2)' }}
                >
                  &ldquo;
                </div>

                <blockquote
                  className="text-base md:text-lg font-light leading-relaxed mt-6 mb-10"
                  style={{ color: 'rgba(255,255,255,0.6)' }}
                >
                  {item.quote}
                </blockquote>

                <div className="flex items-center gap-5">
                  {/* Initial avatar */}
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-xs font-light shrink-0"
                    style={{
                      border: '1px solid rgba(201,160,48,0.35)',
                      color: 'rgba(201,160,48,0.75)',
                    }}
                  >
                    {item.name.split('.')[0]}
                  </div>
                  <div>
                    <p
                      className="text-sm tracking-widest"
                      style={{ color: 'rgba(255,255,255,0.7)' }}
                    >
                      {item.name}
                    </p>
                    <p
                      className="text-[10px] tracking-[0.35em] uppercase mt-0.5"
                      style={{ color: 'rgba(255,255,255,0.3)' }}
                    >
                      {item.role}
                    </p>
                    <p
                      className="text-[10px] tracking-wider mt-0.5"
                      style={{ color: 'rgba(201,160,48,0.45)' }}
                    >
                      {item.sector}
                    </p>
                  </div>
                </div>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
