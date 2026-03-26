export default function Home() {
  return (
    <main className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full text-center space-y-6">
        <div className="inline-block bg-blue-600 text-xs font-semibold px-3 py-1 rounded-full tracking-widest uppercase">
          Project Chimera
        </div>
        <h1 className="text-5xl font-bold tracking-tight">
          ChimeraShield
        </h1>
        <p className="text-gray-400 text-lg">
          AI-powered cybersecurity for small and medium businesses.
          Detect threats before they become breaches.
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <button className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition">
            Start Free Scan
          </button>
          <button className="border border-gray-700 hover:border-gray-500 px-6 py-3 rounded-lg font-semibold transition">
            Learn More
          </button>
        </div>
        <p className="text-gray-600 text-sm pt-8">
          MVP — built with Next.js + FastAPI + Claude AI
        </p>
      </div>
    </main>
  );
}
