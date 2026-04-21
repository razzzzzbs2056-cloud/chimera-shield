'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';

const BrainCanvas = dynamic(() => import('./BrainCanvas'), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 bg-[#03030A] flex items-center justify-center">
      <div className="w-px h-12 bg-[#C9A030]/40 animate-pulse" />
    </div>
  ),
});

export default function BrainHero() {
  const [isZoomed, setIsZoomed] = useState(false);

  return (
    <section className="relative w-full h-screen bg-[#03030A] overflow-hidden">
      {/* Three.js canvas — full bleed */}
      <BrainCanvas isZoomed={isZoomed} setIsZoomed={setIsZoomed} />

      {/* Vignette + hero copy — fades out on zoom */}
      <div
        className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
        style={{
          opacity: isZoomed ? 0 : 1,
          transition: 'opacity 1.2s ease',
          background:
            'radial-gradient(ellipse at 50% 50%, transparent 35%, #03030A 95%)',
        }}
      >
        <p
          className="text-[10px] tracking-[0.65em] uppercase mb-6"
          style={{ color: 'rgba(185, 145, 18, 0.6)' }}
        >
          Neural Performance Intelligence
        </p>

        <h1 className="text-6xl md:text-8xl font-extralight tracking-[0.06em] text-white/90">
          Chimera
          <span style={{ color: '#C9A030', fontWeight: 300 }}>Shield</span>
        </h1>

        <div className="mt-8 flex items-center gap-4">
          <div className="h-px w-10" style={{ background: 'rgba(201,160,48,0.35)' }} />
          <p className="text-[10px] tracking-[0.55em] uppercase text-white/20">
            Click a golden node
          </p>
          <div className="h-px w-10" style={{ background: 'rgba(201,160,48,0.35)' }} />
        </div>
      </div>

      {/* Return button — appears after zoom completes */}
      <button
        onClick={() => setIsZoomed(false)}
        className="absolute top-8 left-8 z-20 flex items-center gap-3 group"
        style={{
          opacity: isZoomed ? 1 : 0,
          pointerEvents: isZoomed ? 'auto' : 'none',
          transition: isZoomed ? 'opacity 0.8s ease 2.8s' : 'opacity 0.4s ease',
        }}
      >
        <div
          className="h-px w-8 transition-all duration-300"
          style={{ background: 'rgba(201,160,48,0.5)' }}
        />
        <span
          className="text-[10px] tracking-[0.5em] uppercase transition-colors duration-300"
          style={{ color: 'rgba(201,160,48,0.6)' }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.color = 'rgba(201,160,48,1)')
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.color = 'rgba(201,160,48,0.6)')
          }
        >
          Return
        </span>
      </button>

      {/* Microscopic label — appears when zoomed */}
      <div
        className="absolute bottom-10 left-0 right-0 flex justify-center pointer-events-none"
        style={{
          opacity: isZoomed ? 1 : 0,
          transition: isZoomed ? 'opacity 0.8s ease 3.2s' : 'opacity 0.3s ease',
        }}
      >
        <p className="text-[9px] tracking-[0.7em] uppercase text-white/20">
          Neural Fiber-Optic Pathway · Microscopic View
        </p>
      </div>
    </section>
  );
}
