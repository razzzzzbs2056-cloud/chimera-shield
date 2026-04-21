export default function SiteFooter() {
  const year = new Date().getFullYear();

  return (
    <footer
      className="w-full px-8 md:px-20 py-16 border-t border-white/[0.05]"
      style={{ background: '#03030A' }}
    >
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center md:items-end justify-between gap-8">
        {/* Wordmark */}
        <div>
          <p className="text-sm font-extralight tracking-[0.4em] text-white/80">
            CHIMERA<span style={{ color: '#C9A030' }}>SHIELD</span>
          </p>
          <p
            className="text-[9px] tracking-[0.5em] uppercase mt-2"
            style={{ color: 'rgba(255,255,255,0.2)' }}
          >
            Neural Performance Intelligence
          </p>
        </div>

        {/* Center links */}
        <nav className="flex items-center gap-8">
          {['Privacy', 'Terms', 'Contact'].map((item) => (
            <a
              key={item}
              href="#"
              className="text-[10px] tracking-[0.4em] uppercase text-white/20 hover:text-white/50 transition-colors duration-300"
            >
              {item}
            </a>
          ))}
        </nav>

        {/* Copyright */}
        <p
          className="text-[10px] tracking-wider"
          style={{ color: 'rgba(255,255,255,0.15)' }}
        >
          © {year} ChimeraShield. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
