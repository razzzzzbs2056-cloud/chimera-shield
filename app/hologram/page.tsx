import Hologram from "../components/Hologram";

const ASPECTS: Record<string, string> = { "16x10": "16 / 10", "16x9": "16 / 9", "1x1": "1 / 1" };

// Full-bleed showcase of the hologram. Also the capture target for scripts/record-hologram.js.
// ?aspect=16x9 | 1x1 changes the bay shape for video formats.
export default function HologramPage({ searchParams }: { searchParams: { aspect?: string } }) {
  const aspect = ASPECTS[searchParams.aspect ?? ""] ?? undefined;
  return (
    <main className="min-h-screen bg-[#05080c] flex items-center justify-center">
      <Hologram className="max-w-[1600px]" aspectRatio={aspect} />
    </main>
  );
}
