import BrainHero from '@/components/hero/BrainHero';

export const dynamic = 'force-dynamic';
import Philosophy from '@/components/sections/Philosophy';
import Pillars from '@/components/sections/Pillars';
import Metrics from '@/components/sections/Metrics';
import Testimonials from '@/components/sections/Testimonials';
import Apply from '@/components/sections/Apply';
import SiteFooter from '@/components/sections/SiteFooter';

export default function Home() {
  return (
    <main className="bg-[#03030A] text-white">
      <BrainHero />
      <Philosophy />
      <Pillars />
      <Metrics />
      <Testimonials />
      <Apply />
      <SiteFooter />
    </main>
  );
}
