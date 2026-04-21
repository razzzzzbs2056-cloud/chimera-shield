import ScrollReveal from '@/components/ui/ScrollReveal';

export default function Philosophy() {
  return (
    <section
      id="philosophy"
      className="relative w-full py-36 md:py-52 px-8 md:px-20 overflow-hidden"
      style={{ background: '#04040C' }}
    >
      {/* Decorative vertical line */}
      <div
        className="absolute left-0 top-0 bottom-0 w-px"
        style={{
          background:
            'linear-gradient(to bottom, transparent, rgba(201,160,48,0.25) 30%, rgba(201,160,48,0.25) 70%, transparent)',
        }}
      />

      <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-20 md:gap-32 items-start">
        {/* Left — label + manifesto headline */}
        <ScrollReveal direction="left">
          <p
            className="text-[10px] tracking-[0.65em] uppercase mb-8"
            style={{ color: 'rgba(201,160,48,0.55)' }}
          >
            The Philosophy
          </p>
          <h2
            className="text-4xl md:text-5xl font-extralight leading-[1.15] tracking-tight"
            style={{ color: 'rgba(255,255,255,0.88)' }}
          >
            The gap between good and exceptional is never talent.
            <br />
            <span style={{ color: '#C9A030' }}>It is architecture.</span>
          </h2>

          {/* Gold rule */}
          <div
            className="mt-12 h-px w-16"
            style={{ background: 'rgba(201,160,48,0.45)' }}
          />
        </ScrollReveal>

        {/* Right — philosophy body */}
        <ScrollReveal delay={180}>
          <div
            className="space-y-7 text-base font-light leading-relaxed"
            style={{ color: 'rgba(255,255,255,0.45)' }}
          >
            <p>
              Elite performers are not born — they are engineered. Every
              cognitive shortcut, every capital structure, every physical
              protocol is the result of intentional design layered over
              time, tested against pressure, and refined without
              compromise.
            </p>
            <p>
              ChimeraShield exists for the rare individual who refuses to
              accept inherited ceilings. We work with founders, executives,
              and wealth architects who understand that true leverage begins
              in the mind and is measured in equity.
            </p>
            <p
              className="text-sm italic"
              style={{ color: 'rgba(201,160,48,0.6)' }}
            >
              &ldquo;Mastery is the only defensible moat.&rdquo;
            </p>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
