import BrainHero from '@/components/hero/BrainHero';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#03030A] text-white">
      {/* ─── WebGL Brain Hero ─────────────────────────────────────── */}
      <BrainHero />

      {/* ─── Below-fold content ───────────────────────────────────── */}
      <section className="flex flex-col items-center justify-center py-32 px-8 text-center">
        <div className="inline-block text-[10px] font-semibold px-4 py-1 tracking-widest uppercase mb-8 border border-[#C9A030]/30 text-[#C9A030]/70">
          Project Chimera
        </div>

        <p className="text-gray-400 text-lg max-w-xl leading-relaxed">
          AI-powered cybersecurity for elite organisations. Detect threats
          before they become breaches.
        </p>

        <div className="flex gap-5 justify-center pt-10">
          <a
            href="/scan"
            className="px-8 py-3 text-sm tracking-widest uppercase font-light bg-[#C9A030]/10 border border-[#C9A030]/40 text-[#C9A030]/90 hover:bg-[#C9A030]/20 hover:border-[#C9A030]/70 transition-all duration-300"
          >
            Start Free Scan
          </a>
          <button className="px-8 py-3 text-sm tracking-widest uppercase font-light border border-white/10 text-white/40 hover:border-white/20 hover:text-white/60 transition-all duration-300">
            Learn More
          </button>
        </div>

        <p className="text-gray-700 text-xs pt-16 tracking-widest uppercase">
          MVP · Next.js + FastAPI + Claude AI
        </p>
      </section>
    </main>
  );
}
